import argparse
import os
import socket
import time

from dotenv import load_dotenv
from prometheus_client import Enum, Gauge, start_http_server

from opnsense_exporter.opnsense_api import OPNSenseAPI, OPNSenseRole

load_dotenv()

HA_STATES = ["active", "hot_standby", "unavailable", "maintenancemode"]
main_ha_state = Enum(
    "opnsense_main_ha_state",
    "OPNSense HA state of the MAIN server",
    [
        "instance",
        "host",
        "role",
    ],
    states=HA_STATES,
)
backup_ha_state = Enum(
    "opnsense_backup_ha_state",
    "OPNSense HA state of the BACKUP server",
    [
        "instance",
        "host",
        "role",
    ],
    states=HA_STATES,
)
active_server_bytes_received = Gauge(
    "opnsense_active_server_bytes_received",
    "Active OPNSense server bytes received on WAN interface",
    [
        "instance",
        "host",
        "role",
    ],
)
active_server_bytes_transmitted = Gauge(
    "opnsense_active_server_bytes_transmitted",
    "Active OPNSense server bytes transmitted on WAN interface",
    [
        "instance",
        "host",
        "role",
    ],
)


class OPNSensePrometheusExporter:
    def __init__(
        self,
        main: OPNSenseAPI,
        backup: OPNSenseAPI,
        exporter_instance: str = "",
        check_frequency: int = 1,
    ):
        self.main = main
        self.backup = backup
        self.exporter_instance = exporter_instance
        self.check_frequency = check_frequency

    def process_requests(self):
        """A dummy function that takes some time."""
        main_state = self.main.get_interface_vip_status()
        backup_sate = self.backup.get_interface_vip_status()
        main_ha_state.labels(instance=self.exporter_instance, **self.main.labels).state(
            main_state
        )
        backup_ha_state.labels(
            instance=self.exporter_instance, **self.backup.labels
        ).state(backup_sate)
        active_opnsense = None
        if main_state == "active":
            active_opnsense = self.main
        if backup_sate == "active":
            active_opnsense = self.backup
        if active_opnsense:
            bytes_received, bytes_transmitted = active_opnsense.get_wan_trafic()
            if bytes_received or bytes_received == 0:
                active_server_bytes_received.labels(
                    instance=self.exporter_instance, **active_opnsense.labels
                ).set(bytes_received)
            if bytes_transmitted or bytes_transmitted == 0:
                active_server_bytes_transmitted.labels(
                    instance=self.exporter_instance, **active_opnsense.labels
                ).set(bytes_transmitted)

    def start_server(self):
        # Start up the server to expose the metrics.
        start_http_server(8000)
        # Generate some requests.
        while True:
            self.process_requests()
            time.sleep(self.check_frequency)


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
            "Exporter Instance name, default value computed with hostname "
            "where the server is running. Use to set the instance label."
        ),
    )

    arguments = parser.parse_args()

    server = OPNSensePrometheusExporter(
        OPNSenseAPI(
            OPNSenseRole.MAIN, arguments.main, arguments.user, arguments.password
        ),
        OPNSenseAPI(
            OPNSenseRole.BACKUP, arguments.backup, arguments.user, arguments.password
        ),
        check_frequency=arguments.frequency,
        exporter_instance=arguments.prom_instance,
    )
    server.start_server()

    # return the server instance mainly for test purpose
    return server
