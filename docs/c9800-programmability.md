# The Catalyst 9800 programmability surface for 6 GHz power modes

Measured on a Catalyst 9800-CL running IOS-XE 17.17.1, with the on-box
YANG pulled over NETCONF `get-schema`. Cisco shipped AFC support in
IOS-XE 17.12.3; the config leaf appears in the published YANG from
17.13.1.

## Set

The writable surface is one boolean per 6 GHz RF profile, plus the
standard machinery for attaching profiles to APs (RF tags). There is no
per-AP power mode setting, no way to force a radio into Standard Power,
no configurable AFC server, and no API that triggers an AFC query.

CLI:

```
ap dot11 6ghz rf-profile <name>
 tx-power standard
```

NETCONF/YANG (also reachable over RESTCONF, see
`../c9800/restconf-paths.md`):

```
Cisco-IOS-XE-wireless-rf-cfg:rf-cfg-data/rf-profiles/rf-profile[name]/std-pwr-mode-allowed
```

Catalyst Center Intent API: `enableStandardPowerService` on the wireless
RF profile endpoints. As of the 3.1.6 documentation set (swept
2026-09-18, all 1,393 endpoint specs), Catalyst Center had no dedicated
API for provisioning the per-AP geolocation AFC requires — only an
AP-height read field — so a rollout on that release cannot be completed
by API alone. Cisco's 3.2.3 SDK adds per-AP geolocation height and
uncertainty to the access point configuration write path, so check your
release before assuming the gap.

The three names above are the same bit. None of the three documentation
sets mentions the other two names, which makes searching miserable, so
keep all three handy.

## Verify

CLI, in rough order of usefulness:

```
show wireless afc ap
show wireless afc statistics
show wireless afc request
show wireless afc response
show wireless afc geolocation
show running-config all | section ap dot11 6ghz rf-profile
```

(The command reference documents `request` and `response` without
arguments; they cover all radios.)

`show wireless afc ap` is the readiness checklist. Its columns are the
conditions an AP must satisfy: AFC status, power mode capability, current
power mode, AP, radio, and RF-profile admin states, the RF-profile
tx-power standard bit, country allowed, location known, and height known.

`show running-config all` prints the default state of the bit as
`no tx-power standard`, which is the fastest way to confirm which way a
profile is set.

## Monitor

Two read-only YANG models carry the whole operational story, pollable
over NETCONF or RESTCONF and, as operational data, candidates for
streaming telemetry:

* `Cisco-IOS-XE-wireless-afc-oper`: the AFC request and response per AP,
  including per-channel granted power and the grant expiry timestamp.
* `Cisco-IOS-XE-wireless-afc-cloud-oper`: message counters, error
  counters, round-trip times, and a periodic health check block (my
  bench showed a 30-second cadence; Cisco documentation shows longer
  timers, so treat the interval as release-dependent). The block carries
  a YANG choice: healthy reports the `cloud-hc-ok` leaf, unhealthy
  reports an `hc-error-status` container naming the blocker (for example
  `not-otp-upgraded`).

Useful alarm fields: `afc-msg-err`, `healthcheck/num-hc-down`,
`healthcheck/country-not-supported`, `healthcheck/cloud-hc-ok` (absent
means unhealthy), `hc-error-status/*`, and the grant `expire-time` per
AP response. Whether these models support on-change
telemetry subscriptions is unverified; plan for periodic polling until
you prove otherwise on your release.

The `../pyats/` controller-side precheck asserts on these fields and
adds one CLI cross-check. genieparser ships no parser for any `show wireless afc`
command (checked at version 26.8), which is why the monitor is NETCONF
end to end.

## Adjust

Adjusting comes down to flipping the profile bit, moving APs between RF
profiles via tags, and fixing whatever the readiness columns say is
blocking (location, height, country, onboarding). The AFC's own grants
are not adjustable from the controller; you influence them only through
better location data and power mode selection.

## One undocumented loose end

`Cisco-IOS-XE-wireless-access-point-cmd-rpc` has carried an RPC input
leaf `rlp-sp-pwrmode-switch` since 17.11.1, described in the schema as a
recommendation to switch a radio from LPI mode to SP mode. It is the
only per-radio power mode write path in the modeled surface, and Cisco
does not document it. On 17.17.1 the enclosing RPC
(`set-open-rrm-channel-auto`) is registered and callable: a misspelled
RPC name is rejected at the protocol layer, while the real name is
accepted and validated field by field. Input element order follows the
schema strictly, and `mac-addr` takes the colon-separated
`ietf-yang-types` format, not Cisco dotted. Its effect against a real
6 GHz radio is untested. If you test it, open an issue with what you
find.
