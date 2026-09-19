#!/usr/bin/env python3
"""Report std-pwr-mode-allowed for every 6 GHz RF profile on a C9800.

An absent leaf means the default, false, which the CLI shows as
"no tx-power standard".

    python3 get_std_power_bit.py --host 198.51.100.10 --user admin
"""
import argparse
import re
import sys

from common import add_device_args, connect

RF_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-rf-cfg"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_device_args(parser)
    args = parser.parse_args()

    flt = ("subtree",
           f'<rf-cfg-data xmlns="{RF_NS}"><rf-profiles/></rf-cfg-data>')
    with connect(args) as session:
        reply = str(session.get_config(source="running", filter=flt))

    profiles = re.findall(r"<rf-profile>.*?</rf-profile>", reply, re.S)
    found = 0
    for profile in profiles:
        band = re.search(r"<band>([^<]+)</band>", profile)
        if not band or "6-ghz" not in band.group(1):
            continue
        found += 1
        name = re.search(r"<name>([^<]+)</name>", profile)
        bit = re.search(r"<std-pwr-mode-allowed>([^<]+)"
                        r"</std-pwr-mode-allowed>", profile)
        value = bit.group(1) if bit else "false (default, leaf absent)"
        print(f"{name.group(1) if name else '?':32s} "
              f"std-pwr-mode-allowed = {value}")
    if not found:
        print("no 6 GHz RF profiles found in the running config")
    return 0


if __name__ == "__main__":
    sys.exit(main())
