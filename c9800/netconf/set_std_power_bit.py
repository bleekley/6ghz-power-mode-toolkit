#!/usr/bin/env python3
"""Set std-pwr-mode-allowed on a named 6 GHz RF profile over NETCONF.

CAUTION: this is the write path. The read scripts in this folder were run
against a live 17.17.1 controller; this edit-config structure comes from
the same schema but you should test it in a lab before production use.
Enabling the bit only permits Standard Power. The AP still needs AFC
onboarding, geolocation, height, and a supported country before any
radio changes mode.

    python3 set_std_power_bit.py --host 198.51.100.10 --user admin \
        --profile default-rf-profile-6ghz --value true
"""
import argparse
import sys

from common import add_device_args, connect

RF_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-rf-cfg"

TEMPLATE = """<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <rf-cfg-data xmlns="{ns}">
    <rf-profiles>
      <rf-profile>
        <name>{profile}</name>
        <std-pwr-mode-allowed>{value}</std-pwr-mode-allowed>
      </rf-profile>
    </rf-profiles>
  </rf-cfg-data>
</config>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_device_args(parser)
    parser.add_argument("--profile", required=True,
                        help="6 GHz RF profile name")
    parser.add_argument("--value", choices=["true", "false"], required=True)
    args = parser.parse_args()

    payload = TEMPLATE.format(ns=RF_NS, profile=args.profile,
                              value=args.value)
    with connect(args) as session:
        reply = session.edit_config(target="running", config=payload)
        print(reply)
        print(f"std-pwr-mode-allowed set to {args.value} on "
              f"{args.profile}. Confirm with get_std_power_bit.py and "
              "remember to save the configuration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
