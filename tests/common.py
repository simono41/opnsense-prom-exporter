import json

MAIN_HOST = "192.168.1.1"
BACKUP_HOST = "192.168.1.2"
LOGIN = "user"
PASSWORD = "pwd"


def generate_get_vip_status_paylaod(state_wan, state_lan, maintenance_mode):
    return json.dumps(
        {
            "total": 2,
            "rowCount": 2,
            "current": 1,
            "rows": [
                {
                    "interface": "wan",
                    "vhid": "1",
                    "advbase": "1",
                    "advskew": "0",
                    "subnet": "176.149.171.241",
                    "status": state_wan,
                    "mode": "carp",
                    "status_txt": state_wan,
                    "vhid_txt": "1 (freq. 1/0)",
                },
                {
                    "interface": "lan",
                    "vhid": "3",
                    "advbase": "1",
                    "advskew": "0",
                    "subnet": "192.168.200.1",
                    "status": state_lan,
                    "mode": "carp",
                    "status_txt": state_lan,
                    "vhid_txt": "3 (freq. 1/0)",
                },
            ],
            "carp": {
                "demotion": "0",
                "allow": "1",
                "maintenancemode": maintenance_mode,
                "status_msg": "",
            },
        }
    )


def generate_diagnostics_traffic_interface_paylaod():
    return json.dumps(
        {
            "wan": {
                "records": [
                    {
                        "address": "0.1.2.3",
                        "rate_bits_in": 15300,
                        "rate_bits_out": 1720,
                        "rate_bits": 17020,
                        "cumulative_bytes_in": 3830,
                        "cumulative_bytes_out": 441,
                        "cumulative_bytes": 4271,
                        "tags": [],
                        "details": [
                            {
                                "address": "0.1.2.3",
                                "rate": "15.3Kb",
                                "rate_bits": 15300,
                                "cumulative": "3.83KB",
                                "cumulative_bytes": 3830,
                                "tags": ["local"],
                            }
                        ],
                        "rname": "fake value",
                        "rate_in": "15.3 kb",
                        "rate_out": "1.72 kb",
                        "rate": "17.02 kb",
                        "cumulative_in": "3.83 kb",
                        "cumulative_out": "441.0 b",
                        "cumulative": "4.27 kb",
                    },
                    {
                        "address": "0.1.2.3",
                        "rate_bits_in": 4470,
                        "rate_bits_out": 7290,
                        "rate_bits": 11760,
                        "cumulative_bytes_in": 1120,
                        "cumulative_bytes_out": 1820,
                        "cumulative_bytes": 2940,
                        "tags": [],
                        "details": [
                            {
                                "address": "0.1.2.3",
                                "rate": "4.47Kb",
                                "rate_bits": 4470,
                                "cumulative": "1.12KB",
                                "cumulative_bytes": 1120,
                                "tags": ["local"],
                            }
                        ],
                        "rname": "fake value",
                        "rate_in": "4.47 kb",
                        "rate_out": "7.29 kb",
                        "rate": "11.76 kb",
                        "cumulative_in": "1.12 kb",
                        "cumulative_out": "1.82 kb",
                        "cumulative": "2.94 kb",
                    },
                    {
                        "address": "0.1.2.3",
                        "rate_bits_in": 272,
                        "rate_bits_out": 272,
                        "rate_bits": 544,
                        "cumulative_bytes_in": 68,
                        "cumulative_bytes_out": 68,
                        "cumulative_bytes": 136,
                        "tags": [],
                        "details": [
                            {
                                "address": "0.1.2.3",
                                "rate": "272b",
                                "rate_bits": 272,
                                "cumulative": "68B",
                                "cumulative_bytes": 68,
                                "tags": ["local"],
                            }
                        ],
                        "rname": "fake value",
                        "rate_in": "272.0 b",
                        "rate_out": "272.0 b",
                        "rate": "544.0 b",
                        "cumulative_in": "68.0 b",
                        "cumulative_out": "68.0 b",
                        "cumulative": "136.0 b",
                    },
                    {
                        "address": "0.1.2.3",
                        "rate_bits_in": 272,
                        "rate_bits_out": 272,
                        "rate_bits": 544,
                        "cumulative_bytes_in": 68,
                        "cumulative_bytes_out": 68,
                        "cumulative_bytes": 136,
                        "tags": [],
                        "details": [
                            {
                                "address": "0.1.2.3",
                                "rate": "272b",
                                "rate_bits": 272,
                                "cumulative": "68B",
                                "cumulative_bytes": 68,
                                "tags": ["local"],
                            }
                        ],
                        "rname": "fake value",
                        "rate_in": "272.0 b",
                        "rate_out": "272.0 b",
                        "rate": "544.0 b",
                        "cumulative_in": "68.0 b",
                        "cumulative_out": "68.0 b",
                        "cumulative": "136.0 b",
                    },
                    {
                        "address": "0.1.2.3",
                        "rate_bits_in": 0,
                        "rate_bits_out": 480,
                        "rate_bits": 480,
                        "cumulative_bytes_in": 0,
                        "cumulative_bytes_out": 120,
                        "cumulative_bytes": 120,
                        "tags": [],
                        "details": [
                            {
                                "address": "0.1.2.3",
                                "rate": "0b",
                                "rate_bits": 0,
                                "cumulative": "0B",
                                "cumulative_bytes": 0,
                                "tags": ["local"],
                            },
                            {
                                "address": "0.1.2.3",
                                "rate": "0b",
                                "rate_bits": 0,
                                "cumulative": "0B",
                                "cumulative_bytes": 0,
                                "tags": ["local"],
                            },
                        ],
                        "rname": "fake value",
                        "rate_in": "0.0 b",
                        "rate_out": "480.0 b",
                        "rate": "480.0 b",
                        "cumulative_in": "0.0 b",
                        "cumulative_out": "120.0 b",
                        "cumulative": "120.0 b",
                    },
                    {
                        "address": "0.1.2.3",
                        "rate_bits_in": 224,
                        "rate_bits_out": 0,
                        "rate_bits": 224,
                        "cumulative_bytes_in": 56,
                        "cumulative_bytes_out": 0,
                        "cumulative_bytes": 56,
                        "tags": [],
                        "details": [
                            {
                                "address": "0.1.2.3",
                                "rate": "224b",
                                "rate_bits": 224,
                                "cumulative": "56B",
                                "cumulative_bytes": 56,
                                "tags": ["local"],
                            }
                        ],
                        "rname": "fake value",
                        "rate_in": "224.0 b",
                        "rate_out": "0.0 b",
                        "rate": "224.0 b",
                        "cumulative_in": "56.0 b",
                        "cumulative_out": "0.0 b",
                        "cumulative": "56.0 b",
                    },
                ],
                "status": "ok",
            }
        }
    )
