[![pipeline status](https://gitlab.com/micro-entreprise/opnsense-prom-exporter/badges/main/pipeline.svg)](https://gitlab.com/micro-entreprise/opnsense-prom-exporter/)
[![coverage report](https://gitlab.com/micro-entreprise/opnsense-prom-exporter/badges/main/coverage.svg)](https://gitlab.com/micro-entreprise/opnsense-prom-exporter/)
[![Version status](https://img.shields.io/pypi/v/opnsense-prom-exporter.svg)](https://pypi.python.org/pypi/opnsense-prom-exporter/)
[![PyPi Package](https://img.shields.io/pypi/dm/opnsense-prom-exporter?label=pypi%20downloads)](https://pypi.org/project/opnsense-prom-exporter)



# OPNSense Prometheus exporter

I've configures OPNSense with High Availability settings using 2 servers.

* https://docs.opnsense.org/manual/hacarp.html
* https://docs.opnsense.org/manual/how-tos/carp.html

So I've 2 servers: *MAIN* and *BACKUP*, in normal situation *MAIN* server
is expected to be `active` and the *BACKUP* server to be in `hot_standby` state.


The initial needs was to be able to make sure that *BACKUP* server is ready (hot standby)
to get the main server role with the `active` state at any time.

> Unfortunately I've not found a proper configuration to call OPNSense HTTP API over
> opnvpn on backup server using blackbox configuratoin. That why I've started to develop
> this exporter install on a server on the LAN to be able to resquest both OPNSense servers.

## Metrics

This exporter gives following metrics:

* ``:


## Usage


> *Note*: Most updated documentation from command line !

```
opnsense-exporter --help
```
