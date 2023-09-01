import responses

from opnsense_exporter.opnsense_api import OPNSenseAPI

from .common import (
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
        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD).get_interface_vip_status() == "active"
    )


@responses.activate
def test_get_interface_vip_status_backup():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/interface/get_vip_status/",
        body=generate_get_vip_status_paylaod("BACKUP", "BACKUP", False),
    )

    assert (
        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD).get_interface_vip_status()
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
        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD).get_interface_vip_status()
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
        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD).get_interface_vip_status()
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
        OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD).get_interface_vip_status()
        == "unavailable"
    )


@responses.activate
def test_get_wan_traffic():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/traffic/interface",
        body=generate_diagnostics_traffic_interface_paylaod(),
    )
    assert OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD).get_wan_trafic() == (
        11725192686820,
        2489262014203,
    )


@responses.activate
def test_get_wan_traffic_none():
    responses.add(
        responses.GET,
        f"https://{MAIN_HOST}/api/diagnostics/traffic/interface",
        json={"error": "not found"},
        status=404,
    )
    assert OPNSenseAPI(MAIN_HOST, LOGIN, PASSWORD).get_wan_trafic() == (
        None,
        None,
    )
