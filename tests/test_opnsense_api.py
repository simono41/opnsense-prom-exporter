import responses

from opnsense_exporter.opnsense_api import (
    OPNSenseAPI,
    OPNSenseRole,
    OPNSenseTraffic,
    OPNSenseTrafficMetric,
)

from .common import (
    BACKUP_HOST,
    LOGIN,
    MAIN_HOST,
    PASSWORD,
    generate_diagnostics_traffic_interface_paylaod,
    generate_get_vip_status_paylaod,
)


@responses.activate
def test_get_interface_vip_status_active():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("MASTER", "MASTER", False),
    )

    assert (
        OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD)
        .get_interface_vip_status()
        .value
        == "active"
    )


@responses.activate
def test_get_interface_vip_status_backup():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("BACKUP", "BACKUP", False),
    )

    assert (
        OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD)
        .get_interface_vip_status()
        .value
        == "hot_standby"
    )


@responses.activate
def test_get_interface_vip_status_mainteance_mode():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("MASTER", "MASTER", True),
    )

    assert (
        OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD)
        .get_interface_vip_status()
        .value
        == "maintenancemode"
    )


@responses.activate
def test_get_interface_vip_status_unavailable_weird_case():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("MASTER", "BACKUP", False),
    )
    assert (
        OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD)
        .get_interface_vip_status()
        .value
        == "unavailable"
    )


@responses.activate
def test_get_interface_vip_status_unavailable_rest_api_error():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        json={"error": "not found"},
        status=404,
    )
    assert (
        OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD)
        .get_interface_vip_status()
        .value
        == "unavailable"
    )


@responses.activate
def test_get_traffic():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/traffic/top/wan,lan",
        body=generate_diagnostics_traffic_interface_paylaod(),
    )
    assert OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD).get_traffic(
        "wan,lan"
    ) == [
        OPNSenseTraffic("wan", OPNSenseTrafficMetric.IN, value=101026),
        OPNSenseTraffic("wan", OPNSenseTrafficMetric.OUT, value=86020),
        OPNSenseTraffic("lan", OPNSenseTrafficMetric.IN, value=188490),
        OPNSenseTraffic("lan", OPNSenseTrafficMetric.OUT, value=952),
    ]


@responses.activate
def test_get_traffic_none():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/traffic/top/test-not-found",
        json={"error": "not found"},
        status=404,
    )
    assert (
        OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD).get_traffic(
            "test-not-found"
        )
        == []
    )


@responses.activate
def test_get_traffic_empty_string():
    rsp = responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/traffic/top/",
        json={"not": "called"},
    )
    assert (
        OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD).get_traffic("") == []
    )
    assert rsp.call_count == 0


def test_labels():
    assert OPNSenseAPI(OPNSenseRole.MAIN, MAIN_HOST, LOGIN, PASSWORD).labels == {
        "role": "main",
        "host": MAIN_HOST,
    }
    assert OPNSenseAPI(OPNSenseRole.BACKUP, BACKUP_HOST, LOGIN, PASSWORD).labels == {
        "role": "backup",
        "host": BACKUP_HOST,
    }
