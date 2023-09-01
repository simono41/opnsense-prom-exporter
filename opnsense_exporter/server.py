import argparse
import os
import socket
import time

from dotenv import load_dotenv
from prometheus_client import Enum, Gauge, start_http_server

from opnsense_exporter.opnsense_api import OPNSenseAPI

load_dotenv()

HA_STATES = ["active", "hot_standby", "unavailable", "maintenancemode"]
main_ha_state = Enum(
    "opnsense_main_ha_state", "OPNSense HA state of the MAIN server", states=HA_STATES
)
backup_ha_state = Enum(
    "opnsense_backup_ha_state",
    "OPNSense HA state of the BACKUP server",
    states=HA_STATES,
)
active_server_bytes_received = Gauge(
    "opnsense_active_server_bytes_received",
    "Active OPNSense server bytes received on WAN interface",
)
active_server_bytes_transmitted = Gauge(
    "opnsense_active_server_bytes_transmitted",
    "Active OPNSense server bytes transmitted on WAN interface",
)


def process_requests(main, backup):
    """A dummy function that takes some time."""
    main_state = main.get_interface_vip_status()
    backup_sate = backup.get_interface_vip_status()
    main_ha_state.state(main_state)
    backup_ha_state.state(backup_sate)
    bytes_received = None
    bytes_transmitted = None
    if main_state == "active":
        bytes_received, bytes_transmitted = main.get_wan_trafic()
    if backup_sate == "active":
        bytes_received, bytes_transmitted = backup.get_wan_trafic()
    active_server_bytes_received.set(bytes_received or -1)
    active_server_bytes_transmitted.set(bytes_transmitted or -1)


def start_server(main: OPNSenseAPI, backup: OPNSenseAPI, check_frequency: int = 1):
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        process_requests(main, backup)
        time.sleep(check_frequency)


def run():
    parser = argparse.ArgumentParser(
        description="OPNSense prometheus exporter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--check-frequency-seconds",
        "-c",
        type=int,
        dest="frequency",
        default=int(os.environ.get("CHECK_FREQUENCY_SECONDS", 2)),
        help="How often (in seconds) this server requests OPNSense servers",
    )
    parser.add_argument(
        "--main-host",
        "-m",
        type=str,
        dest="main",
        default=os.environ.get("OPNSENSE_MAIN_HOST", None),
        help="MAIN OPNsense server that should be in `active` state in normal configuration.",
    )
    parser.add_argument(
        "--backup-host",
        "-b",
        type=str,
        dest="backup",
        default=os.environ.get("OPNSENSE_BACKUP_HOST", None),
        help="BACKUP OPNsense server that should be `hot_standby` state in normal configuration.",
    )
    parser.add_argument(
        "--opnsense-user",
        "-u",
        type=str,
        dest="user",
        default=os.environ.get("OPNSENSE_USERNAME", None),
        help="OPNsense user. Expect to be the same on MAIN and BACKUP servers",
    )
    parser.add_argument(
        "--opnsense-password",
        "-p",
        type=str,
        dest="password",
        default=os.environ.get("OPNSENSE_PASSWORD", None),
        help="OPNsense password. Expect to be the same on MAIN and BACKUP servers",
    )
    parser.add_argument(
        "--prometheus-instance",
        dest="prom_instance",
        type=str,
        default=socket.gethostname(),
        help=(
            "Instance name, default value computed with hostname "
            "where the server is running. Use to set the instance label."
        ),
    )

    arguments = parser.parse_args()
    start_server(
        OPNSenseAPI(arguments.main, arguments.user, arguments.password),
        OPNSenseAPI(arguments.backup, arguments.user, arguments.password),
        check_frequency=arguments.frequency,
    )
