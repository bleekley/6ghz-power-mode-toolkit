#!/usr/bin/env python3
"""Set std-pwr-mode-allowed on a named 6 GHz RF profile over NETCONF.

CAUTION: this is the write path. The read scripts in this folder were run
against a live 17.17.1 controller; this edit-config structure comes from
the same schema but you should test it in a lab before production use.
Enabling the bit only permits Standard Power. The AP still needs AFC
onboarding, geolocation, height, and a supported country before any
radio changes mode.

The script reads the running config first and refuses to write unless the
named profile already exists and is a 6 GHz profile: a NETCONF merge to a
misspelled name would otherwise silently create a new profile.

    python3 set_std_power_bit.py --host 198.51.100.10 --user admin \
        --profile default-rf-profile-6ghz --value true
"""
import argparse
import sys
import xml.etree.ElementTree as ET

from common import add_device_args, connect

RF_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-rf-cfg"
NC_NS = "urn:ietf:params:xml:ns:netconf:base:1.0"


def build_payload(profile: str, value: str) -> str:
    # Built with an XML library, not string substitution, so profile
    # names containing &, <, or quotes become valid text nodes.
    config = ET.Element(f"{{{NC_NS}}}config")
    rf_cfg = ET.SubElement(config, f"{{{RF_NS}}}rf-cfg-data")
    profiles = ET.SubElement(rf_cfg, f"{{{RF_NS}}}rf-profiles")
    entry = ET.SubElement(profiles, f"{{{RF_NS}}}rf-profile")
    ET.SubElement(entry, f"{{{RF_NS}}}name").text = profile
    ET.SubElement(entry, f"{{{RF_NS}}}std-pwr-mode-allowed").text = value
    return ET.tostring(config, encoding="unicode")


def find_band(reply: str, profile: str):
    """Return the named profile's band leaf, or None if it is absent."""
    root = ET.fromstring(reply)
    for entry in root.iter(f"{{{RF_NS}}}rf-profile"):
        if entry.findtext(f"{{{RF_NS}}}name") == profile:
            return entry.findtext(f"{{{RF_NS}}}band", default="?")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_device_args(parser)
    parser.add_argument("--profile", required=True,
                        help="6 GHz RF profile name")
    parser.add_argument("--value", choices=["true", "false"], required=True)
    args = parser.parse_args()

    flt = ("subtree",
           f'<rf-cfg-data xmlns="{RF_NS}"><rf-profiles/></rf-cfg-data>')
    with connect(args) as session:
        band = find_band(
            str(session.get_config(source="running", filter=flt)),
            args.profile)
        if band is None:
            print(f"RF profile {args.profile!r} is not in the running "
                  "config; refusing to write (a merge would create it). "
                  "Check the name with get_std_power_bit.py.",
                  file=sys.stderr)
            return 1
        if "6-ghz" not in band:
            print(f"RF profile {args.profile!r} has band {band!r}, not "
                  "6 GHz; refusing to write.", file=sys.stderr)
            return 1

        payload = build_payload(args.profile, args.value)
        reply = session.edit_config(target="running", config=payload)
        print(reply)
        print(f"std-pwr-mode-allowed set to {args.value} on "
              f"{args.profile}. Confirm with get_std_power_bit.py and "
              "remember to save the configuration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
