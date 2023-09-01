import logging

import requests
from requests import RequestException

logger = logging.getLogger(__name__)


class OPNSenseAPI:
    host: str = None
    login: str = None
    password: str = None

    def __init__(self, host, login, password):
        self.host = host
        self.login = login
        self.password = password

    def prepare_url(self, path):
        return f"https://{self.host}{path}"

    def get(self, path):
        response = requests.get(
            self.prepare_url(path),
            auth=(self.login, self.password),
            timeout=0.5,
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
            data = self.get("/api/diagnostics/traffic/interface")
        except RequestException as ex:
            logger.error(
                "Get diagnostics traffic on WAN interface for %s host failed with the following error %r",
                self.host,
                ex,
            )
            return None, None
        return (
            int(data["interfaces"]["wan"]["bytes received"]),
            int(data["interfaces"]["wan"]["bytes transmitted"]),
        )


#    def get_server_system_status(self):
#        # https://192.168.200.1/api/core/system/status
#        return {
#            "CrashReporter":
#            {
#                "statusCode":2,
#                "message":"No problems were detected.",
#                "logLocation":"/crash_reporter.php",
#                "timestamp":"0",
#                "status":"OK"
#            },
#            "Firewall":{
#                "statusCode":2,
#                "message":"No problems were detected.",
#                "logLocation":"/ui/diagnostics/log/core/firewall",
#                "timestamp":"0",
#                "status":"OK"
#            },
#            "System":{"status":"OK"}
#        }
