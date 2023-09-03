from typing import List
from unittest import mock

import responses

from opnsense_exporter.opnsense_api import OPNSenseAPI, OPNSenseRole
from opnsense_exporter.server import OPNSensePrometheusExporter, run

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
    _labels_calls = None

    def __init__(self):
        self._labels = {}
        self._labels_calls = []

    @property
    def count_labels_calls(self) -> int:
        return len(self._labels_calls)

    def labels(self, *args, **kwargs):
        self._labels = kwargs
        self._labels_calls.append(kwargs)
        return self


class FakePromEnum(FakePromMetric):
    _state: str = None
    _state_calls: List[str] = []

    def __init__(self):
        super().__init__()
        self._state_calls = []

    @property
    def count_state_calls(self) -> int:
        return len(self._state_calls)

    def state(self, state: str):
        self._state = state
        self._state_calls.append(state)


class FakePromGauge(FakePromMetric):
    _value: int = None
    _set_calls: List[int] = []

    def __init__(self):
        super().__init__()
        self._set_calls = []

    @property
    def count_set_calls(self) -> int:
        return len(self._set_calls)

    def set(self, value: int):
        self._value = value
        self._set_calls.append(value)


@mock.patch("opnsense_exporter.server.OPNSensePrometheusExporter.start_server")
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
            "-i",
            "efg,hij",
            "--prometheus-instance",
            "server-hostname-instance",
        ],
    ):
        server = run()
        server_mock.assert_called_once()

        assert server.main.role == OPNSenseRole.MAIN
        assert server.main.host == "main.host"
        assert server.main.login == "user-test"
        assert server.main.password == "pwd-test"
        assert server.backup.role == OPNSenseRole.BACKUP
        assert server.backup.host == "backup.host"
        assert server.backup.login == "user-test"
        assert server.backup.password == "pwd-test"
        assert server.check_frequency == 15
        assert server.interfaces == "efg,hij"


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
        f"https://{MAIN_HOST}/api/diagnostics/traffic/top/wan",
        body=generate_diagnostics_traffic_interface_paylaod(),
    )

    opnsense_server_ha_state_mock = FakePromEnum()
    opnsense_active_server_traffic_rate_mock = FakePromGauge()

    with mock.patch(
        "opnsense_exporter.server.opnsense_server_ha_state",
        new=opnsense_server_ha_state_mock,
    ):
        with mock.patch(
            "opnsense_exporter.server.opnsense_active_server_traffic_rate",
            new=opnsense_active_server_traffic_rate_mock,
        ):
            OPNSensePrometheusExporter(
                OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD),
                OPNSenseAPI(OPNSenseRole.BACKUP, BACKUP_HOST, LOGIN, PASSWORD),
                "wan",
            ).process_requests()

    assert opnsense_server_ha_state_mock.count_state_calls == 2
    assert opnsense_server_ha_state_mock._labels_calls == [
        {
            "instance": "",
            "host": MAIN_HOST,
            "role": "main",
        },
        {
            "instance": "",
            "host": BACKUP_HOST,
            "role": "backup",
        },
    ]
    assert opnsense_server_ha_state_mock._state_calls == ["active", "hot_standby"]

    assert opnsense_active_server_traffic_rate_mock.count_set_calls == 2
    assert opnsense_active_server_traffic_rate_mock._labels_calls == [
        {
            "instance": "",
            "host": MAIN_HOST,
            "role": "main",
            "interface": "wan",
            "metric": "rate_bits_in",
        },
        {
            "instance": "",
            "host": MAIN_HOST,
            "role": "main",
            "interface": "wan",
            "metric": "rate_bits_out",
        },
    ]
    assert opnsense_active_server_traffic_rate_mock._set_calls == [101026, 86020]


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
        f"https://{BACKUP_HOST}/api/diagnostics/traffic/top/wan",
        body=generate_diagnostics_traffic_interface_paylaod(),
    )

    opnsense_server_ha_state_mock = FakePromEnum()
    opnsense_active_server_traffic_rate_mock = FakePromGauge()

    with mock.patch(
        "opnsense_exporter.server.opnsense_server_ha_state",
        new=opnsense_server_ha_state_mock,
    ):
        with mock.patch(
            "opnsense_exporter.server.opnsense_active_server_traffic_rate",
            new=opnsense_active_server_traffic_rate_mock,
        ):
            OPNSensePrometheusExporter(
                OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD),
                OPNSenseAPI(OPNSenseRole.BACKUP, BACKUP_HOST, LOGIN, PASSWORD),
                "wan",
            ).process_requests()

    assert opnsense_server_ha_state_mock.count_state_calls == 2
    assert opnsense_server_ha_state_mock._labels_calls == [
        {
            "instance": "",
            "host": MAIN_HOST,
            "role": "main",
        },
        {
            "instance": "",
            "host": BACKUP_HOST,
            "role": "backup",
        },
    ]
    assert opnsense_server_ha_state_mock._state_calls == ["maintenancemode", "active"]

    assert opnsense_active_server_traffic_rate_mock.count_set_calls == 2
    opnsense_active_server_traffic_rate_mock._labels_calls == [
        {
            "instance": "",
            "host": BACKUP_HOST,
            "role": "backup",
            "interface": "wan",
            "metric": "rate_bits_in",
        },
        {
            "instance": "",
            "host": BACKUP_HOST,
            "role": "backup",
            "interface": "wan",
            "metric": "rate_bits_out",
        },
    ]
    assert opnsense_active_server_traffic_rate_mock._set_calls == [101026, 86020]


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
        f"https://{BACKUP_HOST}/api/diagnostics/traffic/top/wan",
        body=generate_diagnostics_traffic_interface_paylaod(),
    )

    opnsense_server_ha_state_mock = FakePromEnum()
    opnsense_active_server_traffic_rate_mock = FakePromGauge()

    with mock.patch(
        "opnsense_exporter.server.opnsense_server_ha_state",
        new=opnsense_server_ha_state_mock,
    ):
        with mock.patch(
            "opnsense_exporter.server.opnsense_active_server_traffic_rate",
            new=opnsense_active_server_traffic_rate_mock,
        ):
            OPNSensePrometheusExporter(
                OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD),
                OPNSenseAPI(OPNSenseRole.BACKUP, BACKUP_HOST, LOGIN, PASSWORD),
                "wan",
            ).process_requests()

    assert opnsense_server_ha_state_mock.count_state_calls == 2
    assert opnsense_server_ha_state_mock._labels_calls == [
        {
            "instance": "",
            "host": MAIN_HOST,
            "role": "main",
        },
        {
            "instance": "",
            "host": BACKUP_HOST,
            "role": "backup",
        },
    ]
    assert opnsense_server_ha_state_mock._state_calls == [
        "maintenancemode",
        "unavailable",
    ]

    assert opnsense_active_server_traffic_rate_mock.count_set_calls == 0


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
        f"https://{BACKUP_HOST}/api/diagnostics/traffic/top/wan",
        body=generate_diagnostics_traffic_interface_paylaod(),
        status=404,
    )

    opnsense_server_ha_state_mock = FakePromEnum()
    opnsense_active_server_traffic_rate_mock = FakePromGauge()

    with mock.patch(
        "opnsense_exporter.server.opnsense_server_ha_state",
        new=opnsense_server_ha_state_mock,
    ):
        with mock.patch(
            "opnsense_exporter.server.opnsense_active_server_traffic_rate",
            new=opnsense_active_server_traffic_rate_mock,
        ):
            OPNSensePrometheusExporter(
                OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD),
                OPNSenseAPI(OPNSenseRole.BACKUP, BACKUP_HOST, LOGIN, PASSWORD),
                "wan",
            ).process_requests()

    assert opnsense_server_ha_state_mock.count_state_calls == 2
    assert opnsense_server_ha_state_mock._labels_calls == [
        {
            "instance": "",
            "host": MAIN_HOST,
            "role": "main",
        },
        {
            "instance": "",
            "host": BACKUP_HOST,
            "role": "backup",
        },
    ]
    assert opnsense_server_ha_state_mock._state_calls == ["active", "hot_standby"]

    assert opnsense_active_server_traffic_rate_mock.count_set_calls == 0
