import logging
from enum import Enum

import requests
from requests import RequestException

logger = logging.getLogger(__name__)


class OPNSenseHAState(Enum):
    ACTIVE = "active"
    HOT_STANDBY = "hot_standby"
    UNAVAILABLE = "unavailable"
    MAINTENANCE_MODE = "maintenancemode"


class OPNSenseTrafficMetric(Enum):
    IN = "rate_bits_in"
    OUT = "rate_bits_out"


class OPNSenseTraffic:
    interface: str = None
    metric: OPNSenseTrafficMetric = None
    value: int = 0

    def __init__(self, interface: str, metric: OPNSenseTrafficMetric, value: int = 0):
        self.value = value
        self.interface = interface
        self.metric = metric

    @property
    def labels(self):
        return {"metric": self.metric.value, "interface": self.interface}

    def __eq__(self, opn_traffic):
        """Used by unittest to assert expected values"""
        return (
            self.interface == opn_traffic.interface
            and self.metric == opn_traffic.metric
            and self.value == opn_traffic.value
        )

    def __repr__(self):
        return f"{self.interface} - {self.metric} = {self.value}"


class OPNSenseRole(Enum):
    MAIN = "main"
    BACKUP = "backup"


class OPNSenseAPI:
    host: str = None
    login: str = None
    password: str = None
    role: OPNSenseRole = None

    def __init__(self, role, host, login, password):
        self.role = role
        self.host = host
        self.login = login
        self.password = password

    @property
    def labels(self):
        return {
            "host": self.host,
            "role": self.role.value,
        }

    def prepare_url(self, path):
        return f"https://{self.host}{path}"

    def get(self, path, timeout=2):
        response = requests.get(
            self.prepare_url(path),
            auth=(self.login, self.password),
            timeout=timeout,
            # # as today I'm using the opnsense selfsigned certificat
            # # but we should avoid this instead trust any certificat
            verify=False,
        )
        response.raise_for_status()
        return response.json()

    def get_interface_vip_status(self) -> OPNSenseHAState:
        try:
            data = self.get("/api/diagnostics/interface/get_vip_status/")
        except RequestException as ex:
            logger.error(
                "Get VIP STATUS on %s failed with the following error %r", self.host, ex
            )
            return OPNSenseHAState.UNAVAILABLE
        if data["carp"]["maintenancemode"]:
            return OPNSenseHAState.MAINTENANCE_MODE
        is_active = all([row["status"] == "MASTER" for row in data["rows"]])
        if is_active:
            return OPNSenseHAState.ACTIVE
        is_backup = all([row["status"] == "BACKUP" for row in data["rows"]])
        if is_backup:
            return OPNSenseHAState.HOT_STANDBY
        logger.warning(
            "this host %s is no active nor backup received payload %s", self.host, data
        )
        return OPNSenseHAState.UNAVAILABLE

    def get_traffic(self, interfaces):
        if not interfaces:
            return []
        try:
            data = self.get(f"/api/diagnostics/traffic/top/{interfaces}", timeout=15)
        except RequestException as ex:
            logger.error(
                "Get diagnostics traffic on %s interface(s) for %s host failed with the following error %r",
                interfaces,
                self.host,
                ex,
            )
            return []
        traffics = []
        for interface in interfaces.split(","):
            traffic_in = OPNSenseTraffic(interface, OPNSenseTrafficMetric.IN)
            traffic_out = OPNSenseTraffic(interface, OPNSenseTrafficMetric.OUT)
            for record in data.get(interface, {}).get("records", []):
                traffic_in.value += record.get(OPNSenseTrafficMetric.IN.value, 0)
                traffic_out.value += record.get(OPNSenseTrafficMetric.OUT.value, 0)
            traffics.extend([traffic_in, traffic_out])
        return traffics
