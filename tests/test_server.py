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


class FakePromMetric:
    _labels = {}

    def labels(self, *args, **kwargs):
        self._labels = kwargs
        return self


class FakePromEnum(FakePromMetric):
    _state = None
    count_state_calls = 0

    def state(self, state):
        self.count_state_calls += 1
        self._state = state


class FakePromGauge(FakePromMetric):
    value = None
    count_set_calls = 0

    def set(self, value):
        self.count_set_calls += 1
        self.value = value


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

    main_ha_state_mock = FakePromEnum()
    backup_ha_state_mock = FakePromEnum()
    active_server_bytes_received_mock = FakePromGauge()
    active_server_bytes_transmitted_mock = FakePromGauge()

    with mock.patch("opnsense_exporter.server.main_ha_state", new=main_ha_state_mock):
        with mock.patch(
            "opnsense_exporter.server.backup_ha_state", new=backup_ha_state_mock
        ):
            with mock.patch(
                "opnsense_exporter.server.active_server_bytes_received",
                new=active_server_bytes_received_mock,
            ):
                with mock.patch(
                    "opnsense_exporter.server.active_server_bytes_transmitted",
                    new=active_server_bytes_transmitted_mock,
                ):
                    process_requests(
                        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD),
                        OPNSenseAPI(BACKUP_HOST, LOGIN, PASSWORD),
                    )

    assert main_ha_state_mock._state == "active"
    assert main_ha_state_mock.count_state_calls == 1
    assert main_ha_state_mock._labels == {"instance": "", "host": MAIN_HOST}

    assert backup_ha_state_mock._state == "hot_standby"
    assert backup_ha_state_mock.count_state_calls == 1
    assert backup_ha_state_mock._labels == {"instance": "", "host": BACKUP_HOST}

    assert active_server_bytes_received_mock.value == 11725192686820
    assert active_server_bytes_received_mock.count_set_calls == 1
    assert active_server_bytes_received_mock._labels == {
        "instance": "",
        "host": MAIN_HOST,
    }

    assert active_server_bytes_transmitted_mock.value == 2489262014203
    assert active_server_bytes_transmitted_mock.count_set_calls == 1
    assert active_server_bytes_transmitted_mock._labels == {
        "instance": "",
        "host": MAIN_HOST,
    }


@responses.activate
def test_process_requests_backup_active():
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

    main_ha_state_mock = FakePromEnum()
    backup_ha_state_mock = FakePromEnum()
    active_server_bytes_received_mock = FakePromGauge()
    active_server_bytes_transmitted_mock = FakePromGauge()

    with mock.patch("opnsense_exporter.server.main_ha_state", new=main_ha_state_mock):
        with mock.patch(
            "opnsense_exporter.server.backup_ha_state", new=backup_ha_state_mock
        ):
            with mock.patch(
                "opnsense_exporter.server.active_server_bytes_received",
                new=active_server_bytes_received_mock,
            ):
                with mock.patch(
                    "opnsense_exporter.server.active_server_bytes_transmitted",
                    new=active_server_bytes_transmitted_mock,
                ):
                    process_requests(
                        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD),
                        OPNSenseAPI(BACKUP_HOST, LOGIN, PASSWORD),
                    )
    assert main_ha_state_mock._state == "maintenancemode"
    assert main_ha_state_mock.count_state_calls == 1
    assert main_ha_state_mock._labels == {"instance": "", "host": MAIN_HOST}

    assert backup_ha_state_mock._state == "active"
    assert backup_ha_state_mock.count_state_calls == 1
    assert backup_ha_state_mock._labels == {"instance": "", "host": BACKUP_HOST}

    assert active_server_bytes_received_mock.value == 11725192686820
    assert active_server_bytes_received_mock.count_set_calls == 1
    assert active_server_bytes_received_mock._labels == {
        "instance": "",
        "host": BACKUP_HOST,
    }

    assert active_server_bytes_transmitted_mock.value == 2489262014203
    assert active_server_bytes_transmitted_mock.count_set_calls == 1
    assert active_server_bytes_transmitted_mock._labels == {
        "instance": "",
        "host": BACKUP_HOST,
    }


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

    main_ha_state_mock = FakePromEnum()
    backup_ha_state_mock = FakePromEnum()
    active_server_bytes_received_mock = FakePromGauge()
    active_server_bytes_transmitted_mock = FakePromGauge()

    with mock.patch("opnsense_exporter.server.main_ha_state", new=main_ha_state_mock):
        with mock.patch(
            "opnsense_exporter.server.backup_ha_state", new=backup_ha_state_mock
        ):
            with mock.patch(
                "opnsense_exporter.server.active_server_bytes_received",
                new=active_server_bytes_received_mock,
            ):
                with mock.patch(
                    "opnsense_exporter.server.active_server_bytes_transmitted",
                    new=active_server_bytes_transmitted_mock,
                ):
                    process_requests(
                        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD),
                        OPNSenseAPI(BACKUP_HOST, LOGIN, PASSWORD),
                    )

    assert main_ha_state_mock._state == "maintenancemode"
    assert main_ha_state_mock.count_state_calls == 1
    assert main_ha_state_mock._labels == {"instance": "", "host": MAIN_HOST}

    assert backup_ha_state_mock._state == "unavailable"
    assert backup_ha_state_mock.count_state_calls == 1
    assert backup_ha_state_mock._labels == {"instance": "", "host": BACKUP_HOST}

    assert active_server_bytes_received_mock.count_set_calls == 0
    assert active_server_bytes_transmitted_mock.count_set_calls == 0


@responses.activate
def test_process_with_falsy_value():
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
        f"https://{BACKUP_HOST}/api/diagnostics/traffic/interface",
        body=generate_diagnostics_traffic_interface_paylaod(),
        status=404,
    )

    main_ha_state_mock = FakePromEnum()
    backup_ha_state_mock = FakePromEnum()
    active_server_bytes_received_mock = FakePromGauge()
    active_server_bytes_transmitted_mock = FakePromGauge()

    with mock.patch("opnsense_exporter.server.main_ha_state", new=main_ha_state_mock):
        with mock.patch(
            "opnsense_exporter.server.backup_ha_state", new=backup_ha_state_mock
        ):
            with mock.patch(
                "opnsense_exporter.server.active_server_bytes_received",
                new=active_server_bytes_received_mock,
            ):
                with mock.patch(
                    "opnsense_exporter.server.active_server_bytes_transmitted",
                    new=active_server_bytes_transmitted_mock,
                ):
                    process_requests(
                        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD),
                        OPNSenseAPI(BACKUP_HOST, LOGIN, PASSWORD),
                    )
    assert main_ha_state_mock._state == "active"
    assert main_ha_state_mock.count_state_calls == 1
    assert main_ha_state_mock._labels == {"instance": "", "host": MAIN_HOST}

    assert backup_ha_state_mock.count_state_calls == 1
    assert backup_ha_state_mock._state == "hot_standby"
    assert backup_ha_state_mock._labels == {"instance": "", "host": BACKUP_HOST}

    assert active_server_bytes_received_mock.count_set_calls == 0
    assert active_server_bytes_transmitted_mock.count_set_calls == 0
