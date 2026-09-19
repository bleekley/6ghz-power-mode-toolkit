# pyATS precheck: 6 GHz Standard Power, controller side, on a C9800

A pyATS Blitz trigger that answers one question as pass or fail, over
NETCONF: does anything on the controller block Standard Power? Verified
against a live Catalyst 9800-CL running IOS-XE 17.17.1: five checks
passed and two failed, and both failures were true statements about that
controller (not OTP onboarded, Standard Power bit still false).

## Scope: what a green run means

A green run means the controller side is clear: the AFC models answer,
no message or health-check errors, country supported, cloud health OK,
and the RF profile allows Standard Power. It does NOT mean an AP is
ready to transmit at Standard Power. Per-AP capability, location,
height, radio state, RF-tag attachment, grants, and grant expiry are not
checked here; read those with `show wireless afc ap` or
`../c9800/netconf/get_afc_oper.py`. Two checks assert on historical
counters (`afc-msg-err`, `num-hc-down`), so a controller that errored
once and recovered keeps failing them until the counters clear. The
profile name is hard-coded to `default-rf-profile-6ghz` in
`afc_monitor.yaml`; edit it for your profile, and confirm that profile
is actually attached to your APs' RF tag.

## Why NETCONF and not CLI parsing

genieparser ships no parser for any `show wireless afc` command (checked
at version 26.8), so a CLI monitor means writing and maintaining your own
parsers. The AFC YANG operational models are already structured data. One
CLI `execute` section stays in the trigger on purpose, as the no-parser
fallback pattern; note it only greps for headings, so it passes even
with zero 6 GHz APs joined.

## What it checks

| Section | Asserts |
|---|---|
| afc_oper_model_answers | The AFC operational model is registered and answers. (An empty reply also passes; this only proves the model exists.) |
| afc_cloud_message_errors_are_zero | `afc-msg-err` equals 0 (historical counter). |
| afc_health_check_never_down | `healthcheck/num-hc-down` equals 0 (historical counter). |
| afc_country_is_supported | `country-not-supported` is false. |
| afc_cloud_health_is_ok | `healthcheck/cloud-hc-ok` is true. The healthcheck is a YANG choice: healthy reports this leaf, unhealthy reports an `hc-error-status` container naming the blocker instead. |
| standard_power_allowed_on_6ghz_profile | `std-pwr-mode-allowed` is true on the named profile. |
| cli_cross_check_six_ghz_ap_count | `show wireless afc statistics` contains the expected fields. |

A controller that is not ready fails the matching checks, which is the
point. Treat a green run as "nothing on the controller blocks Standard
Power", then verify the per-AP story separately.

## Setup and running

```bash
python3 -m venv venv && . venv/bin/activate
pip install "pyats[full]"              # built against pyATS/Genie 26.x
pyats version check                    # confirm one release train
cp testbed.example.yaml testbed.yaml   # edit host and credentials
pyats run job afc_job.py --testbed-file testbed.yaml
pyats logs view                        # browse the HTML report
```

The controller needs `netconf-yang` enabled. The standard setup is a
privilege 15 user; from 17.5, read-only NETCONF is possible with a
lower-privilege user plus NACM rules.

## Three traps, hit while building this

1. **Blitz `datastore` must be a dict**, with `type`, `lock`, and
   `retry` keys. The string `running` fails with
   `AttributeError: 'str' object has no attribute 'get'`.
2. **The Blitz `connection:` value is the mapping datafile's context
   key** (`yang` in `mapping.yaml`), not the testbed connection name.
   Using the testbed name gives
   `AttributeError: 'Device' object has no attribute 'netconf'`.
3. **On macOS, Easypy can segfault before any test runs.** The genie
   harness connect step imports `pyats.tcl`, which creates a Tcl/Tk
   interpreter inside a forked child of a multi-threaded process, and
   macOS kills the child with SIGSEGV and no traceback. Nothing here
   uses the Tcl bridge, so copy the example into your virtualenv's
   site-packages **renamed to `sitecustomize.py`** (the `.example`
   suffix must come off or Python will not import it):

   ```bash
   cp sitecustomize.py.example \
      "$(python3 -c 'import site; print(site.getsitepackages()[0])')/sitecustomize.py"
   ```

   This blocks `_tkinter` for everything in that virtualenv, which is
   why it belongs in a per-project venv and not the system Python.
   Confirmed on macOS 26, Apple Silicon, Python 3.13, pyATS 26.8.

Also check `pyats version check` first: a version-mismatched install
(pyats packages on one release train, genie on another) refuses to start
any job.

One more, hit while re-verifying: **activate the venv, do not just call
`venv/bin/pyats` by absolute path.** Easypy's pre-job environment check
reads the `pip` that is on your PATH, so if the system Python carries a
mismatched pyATS install, the job aborts with its version table and zero
tests run, even though the venv itself is clean. `source
venv/bin/activate` puts the venv's pip first and the check passes.
