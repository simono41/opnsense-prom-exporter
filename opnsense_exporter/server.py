import argparse
import logging
import os
import socket
import time

from dotenv import load_dotenv
from prometheus_client import Enum, Gauge, start_http_server

from opnsense_exporter.opnsense_api import OPNSenseAPI, OPNSenseHAState, OPNSenseRole

logger = logging.getLogger(__name__)
load_dotenv()

HA_STATES = [enum.value for enum in list(OPNSenseHAState)]


class DeprecatedPromEnum(Enum, DeprecationWarning):
    def state(self, *args, **kwargs):
        super().state(*args, **kwargs)
        logger.warning("This metric %s will be removed in v1.0.0", self._name)


main_ha_state = DeprecatedPromEnum(
    "opnsense_main_ha_state",
    "OPNSense HA state of the MAIN server",
    [
        "instance",
        "host",
        "role",
    ],
    states=HA_STATES,
)
backup_ha_state = DeprecatedPromEnum(
    "opnsense_backup_ha_state",
    "OPNSense HA state of the BACKUP server",
    [
        "instance",
        "host",
        "role",
    ],
    states=HA_STATES,
)

opnsense_server_ha_state = Enum(
    "opnsense_server_ha_state",
    "OPNSense server HA state",
    [
        "instance",
        "host",
        "role",
    ],
    states=HA_STATES,
)

opnsense_active_server_traffic_rate = Gauge(
    "opnsense_active_server_traffic_rate",
    "Active OPNSense server bytes in/out per interface",
    [
        "instance",
        "host",
        "role",
        "interface",
        "metric",
    ],
)


class OPNSensePrometheusExporter:
    def __init__(
        self,
        main: OPNSenseAPI,
        backup: OPNSenseAPI,
        interfaces,
        exporter_instance: str = "",
        check_frequency: int = 1,
    ):
        self.main = main
        self.backup = backup
        self.interfaces = interfaces
        self.exporter_instance = exporter_instance
        self.check_frequency = check_frequency

    def process_requests(self):
        """A dummy function that takes some time."""
        main_state = self.main.get_interface_vip_status()
        backup_sate = self.backup.get_interface_vip_status()
        main_ha_state.labels(instance=self.exporter_instance, **self.main.labels).state(
            main_state.value
        )
        backup_ha_state.labels(
            instance=self.exporter_instance, **self.backup.labels
        ).state(backup_sate.value)
        opnsense_server_ha_state.labels(
            instance=self.exporter_instance, **self.main.labels
        ).state(main_state.value)
        opnsense_server_ha_state.labels(
            instance=self.exporter_instance, **self.backup.labels
        ).state(backup_sate.value)
        active_opnsense = None
        if main_state == OPNSenseHAState.ACTIVE:
            active_opnsense = self.main
        if backup_sate == OPNSenseHAState.ACTIVE:
            active_opnsense = self.backup
        if active_opnsense:
            for traffic in active_opnsense.get_traffic(self.interfaces):
                if traffic.value:
                    opnsense_active_server_traffic_rate.labels(
                        instance=self.exporter_instance,
                        **active_opnsense.labels,
                        **traffic.labels
                    ).set(traffic.value)

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
        "--opnsense-interfaces",
        "-i",
        type=str,
        dest="interfaces",
        default=os.environ.get("OPNSENSE_INTERFACES", "wan,lan"),
        help="OPNsense interfaces (coma separated) list to export trafic rates (bytes/s)",
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
        arguments.interfaces,
        check_frequency=arguments.frequency,
        exporter_instance=arguments.prom_instance,
    )
    server.start_server()

    # return the server instance mainly for test purpose
    return server
