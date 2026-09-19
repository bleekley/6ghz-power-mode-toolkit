# pyATS monitor: 6 GHz Standard Power readiness on a C9800

A pyATS Blitz trigger that reports Standard Power readiness as pass or
fail, over NETCONF, with Easypy HTML and JSON reporting. Verified against
a live Catalyst 9800-CL running IOS-XE 17.17.1: five checks passed and
two failed, and both failures were true statements about that controller
(not OTP onboarded, Standard Power bit still false).

## Why NETCONF and not CLI parsing

genieparser ships no parser for any `show wireless afc` command (checked
at version 26.8), so a CLI monitor means writing and maintaining your own
parsers. The AFC YANG operational models are already structured data. One
CLI `execute` section stays in the monitor on purpose, as the no-parser
fallback pattern.

## What it checks

| Section | Asserts |
|---|---|
| afc_oper_model_answers | The AFC operational model is registered and answers. |
| afc_cloud_message_errors_are_zero | `afc-msg-err` equals 0. |
| afc_health_check_never_down | `healthcheck/num-hc-down` equals 0. |
| afc_country_is_supported | `country-not-supported` is false. |
| afc_controller_is_onboarded | `hc-error-status/not-otp-upgraded` is false. |
| standard_power_allowed_on_6ghz_profile | `std-pwr-mode-allowed` is true. |
| cli_cross_check_six_ghz_ap_count | `show wireless afc statistics` contains the expected fields. |

A controller that is not ready fails the matching checks, which is the
point. Treat a green run as "Standard Power can proceed here".

## Running it

```bash
cp testbed.example.yaml testbed.yaml   # edit host and credentials
pyats run job afc_job.py --testbed-file testbed.yaml
pyats logs view                        # browse the HTML report
```

The controller needs `netconf-yang` enabled and a privilege 15 user.

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
   uses the Tcl bridge, so copy `sitecustomize.py.example` into your
   environment's site-packages to make it unimportable. Confirmed on
   macOS 26, Apple Silicon, Python 3.13, pyATS 26.8.

Also check `pyats version check` first: a version-mismatched install
(pyats packages on one release train, genie on another) refuses to start
any job.
