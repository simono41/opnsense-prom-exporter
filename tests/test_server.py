from unittest import mock

import responses

from opnsense_exporter.opnsense_api import OPNSenseAPI
from opnsense_exporter.server import process_requests, run

from .common import (
    BACKUP_HOST,
    LOGIN,
    MAIN_HOST,
    PASSWORD,
    generate_diagnostics_traffic_interface_paylaod,
    generate_get_vip_status_paylaod,
)


@mock.patch("opnsense_exporter.server.start_server")
def test_parser(server_mock):
    with mock.patch(
        "sys.argv",
        [
            "opnsense-exporter",
            "-c",
            "15",
            "-m",
            "main.host",
            "-b",
            "backup.host",
            "-u",
            "user-test",
            "-p",
            "pwd-test",
            "--prometheus-instance",
            "server-hostname-instance",
        ],
    ):
        run()
        server_mock.assert_called_once()
        main, bck = server_mock.call_args.args
        assert main.login == "user-test"
        assert bck.login == "user-test"
        assert main.password == "pwd-test"
        assert bck.password == "pwd-test"
        assert main.host == "main.host"
        assert bck.host == "backup.host"
        assert server_mock.call_args.kwargs["check_frequency"] == 15


@responses.activate
def test_process_requests():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("MASTER", "MASTER", False),
    )
    responses.add(
        responses.GET,
        f"https://{BACKUP_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("BACKUP", "BACKUP", False),
    )
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/traffic/interface",
        body=generate_diagnostics_traffic_interface_paylaod(),
    )
    with mock.patch(
        "opnsense_exporter.server.main_ha_state.state"
    ) as main_ha_state_mock:
        with mock.patch(
            "opnsense_exporter.server.backup_ha_state.state"
        ) as backup_ha_state_mock:
            with mock.patch(
                "opnsense_exporter.server.active_server_bytes_received.set"
            ) as active_server_bytes_received_mock:
                with mock.patch(
                    "opnsense_exporter.server.active_server_bytes_transmitted.set"
                ) as active_server_bytes_transmitted_mock:
                    process_requests(
                        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD),
                        OPNSenseAPI(BACKUP_HOST, LOGIN, PASSWORD),
                    )
    main_ha_state_mock.assert_called_once_with("active")
    backup_ha_state_mock.assert_called_once_with("hot_standby")
    active_server_bytes_received_mock.assert_called_once_with(11725192686820)
    active_server_bytes_transmitted_mock.assert_called_once_with(2489262014203)


@responses.activate
def test_process_requests_backend_active():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("MASTER", "MASTER", True),
    )
    responses.add(
        responses.GET,
        f"https://{BACKUP_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("MASTER", "MASTER", False),
    )
    responses.add(
        responses.GET,
        f"https://{BACKUP_HOST}/api/diagnostics/traffic/interface",
        body=generate_diagnostics_traffic_interface_paylaod(),
    )
    with mock.patch(
        "opnsense_exporter.server.main_ha_state.state"
    ) as main_ha_state_mock:
        with mock.patch(
            "opnsense_exporter.server.backup_ha_state.state"
        ) as backup_ha_state_mock:
            with mock.patch(
                "opnsense_exporter.server.active_server_bytes_received.set"
            ) as active_server_bytes_received_mock:
                with mock.patch(
                    "opnsense_exporter.server.active_server_bytes_transmitted.set"
                ) as active_server_bytes_transmitted_mock:
                    process_requests(
                        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD),
                        OPNSenseAPI(BACKUP_HOST, LOGIN, PASSWORD),
                    )
    main_ha_state_mock.assert_called_once_with("maintenancemode")
    backup_ha_state_mock.assert_called_once_with("active")
    active_server_bytes_received_mock.assert_called_once_with(11725192686820)
    active_server_bytes_transmitted_mock.assert_called_once_with(2489262014203)


@responses.activate
def test_process_no_active():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("MASTER", "MASTER", True),
    )
    responses.add(
        responses.GET,
        f"https://{BACKUP_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("MASTER", "MASTER", True),
        status=404,
    )
    responses.add(
        responses.GET,
        f"https://{BACKUP_HOST}/api/diagnostics/traffic/interface",
        body=generate_diagnostics_traffic_interface_paylaod(),
    )
    with mock.patch(
        "opnsense_exporter.server.main_ha_state.state"
    ) as main_ha_state_mock:
        with mock.patch(
            "opnsense_exporter.server.backup_ha_state.state"
        ) as backup_ha_state_mock:
            with mock.patch(
                "opnsense_exporter.server.active_server_bytes_received.set"
            ) as active_server_bytes_received_mock:
                with mock.patch(
                    "opnsense_exporter.server.active_server_bytes_transmitted.set"
                ) as active_server_bytes_transmitted_mock:
                    process_requests(
                        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD),
                        OPNSenseAPI(BACKUP_HOST, LOGIN, PASSWORD),
                    )
    main_ha_state_mock.assert_called_once_with("maintenancemode")
    backup_ha_state_mock.assert_called_once_with("unavailable")
    active_server_bytes_received_mock.assert_called_once_with(-1)
    active_server_bytes_transmitted_mock.assert_called_once_with(-1)
