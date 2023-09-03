[![pipeline status](https://gitlab.com/micro-entreprise/opnsense-prom-exporter/badges/main/pipeline.svg)](https://gitlab.com/micro-entreprise/opnsense-prom-exporter/)
[![coverage report](https://gitlab.com/micro-entreprise/opnsense-prom-exporter/badges/main/coverage.svg)](https://gitlab.com/micro-entreprise/opnsense-prom-exporter/)
[![Version status](https://img.shields.io/pypi/v/opnsense-prom-exporter.svg)](https://pypi.python.org/pypi/opnsense-prom-exporter/)
[![PyPi Package](https://img.shields.io/pypi/dm/opnsense-prom-exporter?label=pypi%20downloads)](https://pypi.org/project/opnsense-prom-exporter)

# OPNSense Prometheus exporter

I've configures OPNSense with High Availability settings using 2 servers.

- https://docs.opnsense.org/manual/hacarp.html
- https://docs.opnsense.org/manual/how-tos/carp.html

So I've 2 servers: _MAIN_ and _BACKUP_, in normal situation _MAIN_ server
is expected to be `active` and the _BACKUP_ server to be in `hot_standby` state.

The initial needs was to be able to make sure that _BACKUP_ server is ready (hot standby)
to get the main server role with the `active` state at any time.

> Unfortunately I've not found a proper configuration to call OPNSense HTTP API over
> opnvpn on backup server using blackbox configuratoin. That why I've started to develop
> this exporter install on a server on the LAN to be able to resquest both OPNSense servers.

## Metrics

This exporter gives following metrics, all metrics received following labels:

- `instance`: by default this is set with the hostname where is running this exporter service
- `host`: the host of the OPNSense
- `role`: `main` or `backup` to determine the OPNSense server role.

### Enums

- `opnsense_main_ha_state`: (deprecated) OPNSense HA state of the MAIN server
- `opnsense_backup_ha_state`: (deprecated) OPNSense HA state of the BACKUP server
- `opnsense_server_ha_state`: OPNSense HA state, on of following value:
  - **active**: that OPNSense server is receiving traffic
  - **hot_standby**: the OPNSense server is ready to be promote as active server
  - **maintenancemode**: the OPNSense server was turned into maintenance mode
  - **unavailable**: the OPNSense server wasn't accessible or return unexpected value

### Gauges

- `opnsense_active_server_traffic_rate`: Active OPNSense server traffic rate per interfaces bits/s
  add following labels:
  - **interface**: the interface to export (values given using `--opnsense-interfaces`)
  - **metric**: the metric name (as today one of `rate_bits_in`, `rate_bits_in`)

## Usage

> _Note_: Most updated documentation from command line !

```
opnsense-exporter --help
usage: opnsense-exporter [-h] [--check-frequency-seconds FREQUENCY]
                         [--main-host MAIN] [--backup-host BACKUP]
                         [--opnsense-user USER]
                         [--opnsense-interfaces INTERFACES]
                         [--opnsense-password PASSWORD]
                         [--prometheus-instance PROM_INSTANCE]

OPNSense prometheus exporter

optional arguments:
  -h, --help            show this help message and exit
  --check-frequency-seconds FREQUENCY, -c FREQUENCY
                        How often (in seconds) this server requests
                        OPNSense servers (default: 2)
  --main-host MAIN, -m MAIN
                        MAIN OPNsense server that should be in `active`
                        state in normal configuration.
  --backup-host BACKUP, -b BACKUP
                        BACKUP OPNsense server that should be `hot_standby`
                        state in normal configuration.
  --opnsense-user USER, -u USER
                        OPNsense user. Expect to be the same on MAIN and
                        BACKUP servers
  --opnsense-interfaces INTERFACES, -i INTERFACES
                        OPNsense interfaces (coma separated) list to export
                        trafic rates (bytes/s) (default: wan,lan)
  --opnsense-password PASSWORD, -p PASSWORD
                        OPNsense password. Expect to be the same on MAIN
                        and BACKUP servers
  --prometheus-instance PROM_INSTANCE
                        Exporter Instance name, default value computed with
                        hostname where the server is running. Use to set
                        the instance label. (default: my-opnsense-prom-exporter-server)
```

You can setup env through `.env` file or environment variables with defined as default values
(so command line will get the precedent):

- **CHECK_FREQUENCY_SECONDS**: default value for `--check-frequency-seconds` param
- **OPNSENSE_MAIN_HOST**: default value for `--main-host` param
- **OPNSENSE_BACKUP_HOST**: default value for `--backup-host` param
- **OPNSENSE_USERNAME**: default value for `--opnsense-user` param
- **OPNSENSE_PASSWORD**: default value for `--opnsense-password` param
- **OPNSENSE_INTERFACES**: default value for `--opnsense-interfaces` param

## Roadmap

- allow to change the listening port (today it force using `8000`)
- allow to configure timeouts using environment variables
- improves logging to get a debug mode to understand errors based on unexpected payloads

## Changelog

### Version 0.5.1 (2023-09-01)

- FIX `opnsense_server_ha_state` calls were not
  implemented

### Version 0.5.0 (2023-09-01)

- add role label in metrics
- all to configure supervised interfaces using `--opnsense-interfaces`
- replace `active_server_bytes_received` and
  `active_server_bytes_transmitted` by
  `opnsense_active_server_traffic_rate`
- add `opnsense_server_ha_state` and mark `opnsense_main_ha_state`
  and `opnsense_backup_ha_state` as deprecated.

### Version 0.4.0 (2023-09-02)

- Higher timeout while getting WAN traffic info

### Version 0.3.0 (2023-09-02)

- Use proper method to compute WAN traffic

### Version 0.2.0 (2023-09-01)

- Setup automatic release from gitlab while pushing new tag

### Version 0.1.0 (2023-09-01)

- Initial version
