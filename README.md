# 6 GHz Power Mode Toolkit

Tools and reference material for whether a 6 GHz Wi-Fi deployment should run 
Low Power Indoor (LPI) or Standard Power, and how to configure, verify, and 
monitor that choice programmatically on a Cisco Catalyst 9800.

Every enterprise 6 GHz AP runs in one of these two infrastructure modes
(US rules also define very-low-power and geofenced variable-power device
classes, which this toolkit does not cover). LPI needs no coordination
and gets the full band, but its power ceilings are low, and client
ceilings sit 6 dB lower still, which shrinks the usable cell. Standard
Power raises the ceilings on both sides of the link: the EIRP cap sits
6 dB higher, the power-density cap far higher, and how much of that a
real cell collects depends on the grant and the channel width. Clients
stay capped at least 6 dB below the AP's authorized power, so the
asymmetry never goes away. In exchange, the AP must register its 3D
location
with an Automated Frequency Coordination (AFC) service, re-authorize
every 24 hours, operate only in U-NII-5 and U-NII-7, and give up
whatever channels the AFC masks off at that location. LPI buys spectrum
at the cost of power. Standard Power buys power at the cost of spectrum
and a standing operational dependency.

## What is in here

| Path | What it does |
|---|---|
| `decision/decide.py` | Asks a short questionnaire about your site and prints a mode recommendation with reasons. Prerequisites gate the answer: it never recommends Standard Power over a missing requirement. |
| `decision/modes.csv` | The LPI versus Standard Power comparison as data. |
| `docs/` | The decision guide, an AFC primer, and the C9800 programmability reference. |
| `c9800/` | CLI cheat sheet, RESTCONF paths, and runnable ncclient scripts for the NETCONF surface. |
| `pyats/` | A pyATS Blitz controller-side precheck: seven pass/fail checks (six NETCONF, one CLI cross-check). Easypy HTML and JSON reporting. It does not check per-AP readiness or grants. |

## Quick start

Decide which mode fits your site:

```bash
python3 decision/decide.py
```

Read the Standard Power readiness state off a live C9800 over NETCONF:

```bash
python3 -m venv venv && . venv/bin/activate
pip install ncclient
python3 c9800/netconf/get_afc_oper.py --host <wlc> --user <user>
```

The scripts verify the controller's SSH host key against your
`known_hosts` by default; connect once with plain `ssh`, or pass
`--insecure` for a lab controller. The password comes from the
`WLC_PASSWORD` environment variable or an interactive prompt, never
from the command line.

Run the controller precheck (see `pyats/README.md` for setup, including
the macOS note):

```bash
python3 -m venv venv && . venv/bin/activate
pip install "pyats[full]"    # built against pyATS/Genie 26.x
cd pyats
cp testbed.example.yaml testbed.yaml   # then edit host and credentials
pyats run job afc_job.py --testbed-file testbed.yaml
```

## The one configuration bit, and its three names

On the Catalyst 9800 the entire writable control surface for 6 GHz
Standard Power is a single boolean on the 6 GHz RF profile. Each
management surface calls it something different, and none of the three
documentation sets mentions the other two names:

| Surface | Name |
|---|---|
| C9800 CLI | `tx-power standard` under `ap dot11 6ghz rf-profile` |
| IOS-XE YANG | `std-pwr-mode-allowed` in `Cisco-IOS-XE-wireless-rf-cfg` |
| Catalyst Center Intent API | `enableStandardPowerService` |

Everything else is read-only: the AFC request and response, per-channel
granted power, grant expiry, and the cloud health check all live in
operational models you can poll or stream. `docs/c9800-programmability.md`
maps the whole surface.

## How we verified

The C9800 findings in this repo were measured on a live Catalyst 9800-CL
running IOS-XE 17.17.1, with the on-box YANG pulled over NETCONF
`get-schema`. The pyATS precheck ran against that controller and reported
correct results, including correct failures. Three things are documented
here as unverified, and the docs say so where it applies: whether the AFC
operational models support on-change telemetry, the behavior of the
undocumented `rlp-sp-pwrmode-switch` RPC input against a real 6 GHz
radio, and the `set_std_power_bit.py` write path, whose structure comes
from the schema but which you should test in a lab before production use.
Regulatory statements were checked against 47 CFR 15.407 and FCC 20-51
in September 2026; rules change, so verify against the current text
before relying on them.

## Credits and sources

The decision framing draws on a Tech Field Day podcast discussion between
Tom Hollingsworth, Keith Parsons, and Mark Houtz, plus 47 CFR 15.407,
Cisco's C9800 configuration guides, the published IOS-XE YANG models,
and original lab work. This project is not affiliated with Cisco.
Regulatory rules vary by country and change over time, so confirm
current rules for your domain before deploying.

## License

MIT. See `LICENSE`.
