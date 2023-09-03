import logging
from enum import Enum

import requests
from requests import RequestException

logger = logging.getLogger(__name__)


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

    def get_interface_vip_status(self):
        try:
            data = self.get("/api/diagnostics/interface/get_vip_status/")
        except RequestException as ex:
            logger.error(
                "Get VIP STATUS on %s failed with the following error %r", self.host, ex
            )
            return "unavailable"
        if data["carp"]["maintenancemode"]:
            return "maintenancemode"
        is_active = all([row["status"] == "MASTER" for row in data["rows"]])
        if is_active:
            return "active"
        is_backup = all([row["status"] == "BACKUP" for row in data["rows"]])
        if is_backup:
            return "hot_standby"
        logger.warning(
            "this host %s is no active nor backup received payload %s", self.host, data
        )
        return "unavailable"

    def get_wan_trafic(self):
        try:
            data = self.get("/api/diagnostics/traffic/top/wan", timeout=15)
        except RequestException as ex:
            logger.error(
                "Get diagnostics traffic on WAN interface for %s host failed with the following error %r",
                self.host,
                ex,
            )
            return None, None

        received = 0
        transmitted = 0
        for record in data.get("wan", []).get("records", []):
            received += record.get("rate_bits_in", 0)
            transmitted += record.get("rate_bits_out", 0)
        return received, transmitted
