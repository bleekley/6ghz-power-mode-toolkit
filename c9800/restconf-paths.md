# RESTCONF paths for 6 GHz power mode work

RESTCONF paths derive mechanically from the YANG models as
`/restconf/data/{module}:{container}/...`. Send
`Accept: application/yang-data+json`. Percent-encode list keys such as
`<name>` when they carry URL-special characters (`R&D` becomes `R%26D`).

## Set (PATCH or PUT)

```
/restconf/data/Cisco-IOS-XE-wireless-rf-cfg:rf-cfg-data/rf-profiles/rf-profile=<name>/std-pwr-mode-allowed
```

## Verify (GET, running config)

```
/restconf/data/Cisco-IOS-XE-wireless-rf-cfg:rf-cfg-data/rf-profiles
```

## Monitor (GET, operational)

```
/restconf/data/Cisco-IOS-XE-wireless-afc-oper:afc-oper-data
/restconf/data/Cisco-IOS-XE-wireless-afc-oper:afc-oper-data/ewlc-afc-ap-resp=<ap-mac>
/restconf/data/Cisco-IOS-XE-wireless-afc-cloud-oper:afc-cloud-oper-data
```

The same data drives the NETCONF scripts in `netconf/`, which is the
better path for polling because a single session can batch the reads.
