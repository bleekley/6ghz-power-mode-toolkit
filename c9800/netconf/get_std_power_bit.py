#!/usr/bin/env python3
"""Report std-pwr-mode-allowed for every 6 GHz RF profile on a C9800.

An absent leaf means the default, false, which the CLI shows as
"no tx-power standard".

    python3 get_std_power_bit.py --host 198.51.100.10 --user admin
"""
import argparse
import sys
import xml.etree.ElementTree as ET

from common import add_device_args, connect

RF_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-rf-cfg"


def report(reply: str) -> int:
    """Print the per-profile state from a get-config reply; return rc."""
    try:
        root = ET.fromstring(reply)
    except ET.ParseError as err:
        print(f"could not parse the NETCONF reply: {err}", file=sys.stderr)
        return 2

    if root.find(f".//{{{RF_NS}}}rf-cfg-data") is None:
        print("the reply carried no rf-cfg data: the model may be "
              "unsupported on this release, or the reply was incomplete",
              file=sys.stderr)
        return 1

    found = 0
    for profile in root.iter(f"{{{RF_NS}}}rf-profile"):
        band = profile.findtext(f"{{{RF_NS}}}band")
        if band is None or "6-ghz" not in band:
            continue
        found += 1
        name = profile.findtext(f"{{{RF_NS}}}name", default="?")
        bit = profile.findtext(f"{{{RF_NS}}}std-pwr-mode-allowed")
        value = bit if bit is not None else "false (default, leaf absent)"
        print(f"{name:32s} std-pwr-mode-allowed = {value}")
    if not found:
        print("no 6 GHz RF profiles found in the running config")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_device_args(parser)
    args = parser.parse_args()

    flt = ("subtree",
           f'<rf-cfg-data xmlns="{RF_NS}"><rf-profiles/></rf-cfg-data>')
    with connect(args) as session:
        reply = str(session.get_config(source="running", filter=flt))
    return report(reply)


if __name__ == "__main__":
    sys.exit(main())
