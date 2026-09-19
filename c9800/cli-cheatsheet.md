# C9800 CLI cheat sheet: 6 GHz Standard Power

## Enable Standard Power on a 6 GHz RF profile

```
configure terminal
 ap dot11 6ghz rf-profile <profile-name>
  tx-power standard
 end
```

Disable it with `no tx-power standard`. The default is off, which
`show running-config all` prints explicitly:

```
show running-config all | section ap dot11 6ghz rf-profile
```

## Readiness and state

```
show wireless afc ap
show wireless afc statistics
show wireless afc request  <radio-mac>
show wireless afc response <radio-mac>
show wireless afc geolocation
```

`show wireless afc ap` columns are the per-AP readiness checklist: AFC
status, power mode capability, current power mode, admin states, the
RF-profile tx-power standard bit, country allowed, location known, and
height known. An empty table with `Total number of 6GHz APs : 0` in the
statistics output means no joined AP has a 6 GHz radio.

`show wireless afc statistics` includes the cloud health check. On a
9800-CL that has not been onboarded to Cisco's cloud, the status reads
`Not OTP upgraded`, and nothing will reach the AFC service until the
one-time-password token import is done.

## NETCONF prerequisite

```
configure terminal
 netconf-yang
 end
```

NETCONF listens on port 830 and needs AAA with a privilege 15 user.
Allow a couple of minutes after enabling before the port answers.
