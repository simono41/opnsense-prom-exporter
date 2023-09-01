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

### Enums

- `opnsense_main_ha_state`: OPNSense HA state of the MAIN server
- `opnsense_backup_ha_state`: OPNSense HA state of the BACKUP server

### Gauges

- `opnsense_active_server_bytes_received`: Active OPNSense server bytes received on WAN interface
- `opnsense_active_server_bytes_transmitted`: Active OPNSense server bytes transmitted on WAN interface

## Usage

> _Note_: Most updated documentation from command line !

```
opnsense-exporter --help
usage: opnsense-exporter [-h] [--check-frequency-seconds FREQUENCY]
                         [--main-host MAIN] [--backup-host BACKUP]
                         [--opnsense-user USER]
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
                        BACKUP OPNsense server that should be
                        `hot_standby` state in normal configuration.
  --opnsense-user USER, -u USER
                        OPNsense user. Expect to be the same on MAIN and
                        BACKUP servers
  --opnsense-password PASSWORD, -p PASSWORD
                        OPNsense password. Expect to be the same on MAIN
                        and BACKUP servers
  --prometheus-instance PROM_INSTANCE
                        Exporter Instance name, default value computed
                        with hostname where the server is running. Use to
```

You can setup env through `.env` file or environment variables with defined as default values
(so command line will get the precedent):

- **CHECK_FREQUENCY_SECONDS**: default value for `--check-frequency-seconds` param
- **OPNSENSE_MAIN_HOST**: default value for `--main-host` param
- **OPNSENSE_BACKUP_HOST**: default value for `--backup-host` param
- **OPNSENSE_USERNAME**: default value for `--opnsense-user` param
- **OPNSENSE_PASSWORD**: default value for `--opnsense-password` param

## Roadmap

- allow to change the listening port (today it force using `8000`)

## Changelog

### Version 0.1.0

Initial version
