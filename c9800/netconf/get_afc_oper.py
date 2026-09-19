#!/usr/bin/env python3
"""Read the C9800 AFC operational state over NETCONF and summarize it.

Covers the cloud statistics (message counters, health check, blockers)
and the per-AP AFC responses when 6 GHz APs are present.

    python3 get_afc_oper.py --host 198.51.100.10 --user admin
"""
import argparse
import re
import sys

from common import add_device_args, connect

CLOUD_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-afc-cloud-oper"
OPER_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-afc-oper"

CLOUD_FIELDS = ["num-afc-ap", "afc-msg-sent", "afc-msg-rcvd", "afc-msg-err",
                "afc-msg-pending", "min-msg-rtt", "max-msg-rtt", "avg-rtt"]
HEALTH_FIELDS = ["hc-timestamp", "query-in-progress",
                 "country-not-supported", "num-hc-down"]


def leaf(xml: str, tag: str):
    match = re.search(rf"<{tag}>([^<]*)</{tag}>", xml)
    return match.group(1) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_device_args(parser)
    args = parser.parse_args()

    with connect(args) as session:
        cloud = str(session.get(("subtree",
                    f'<afc-cloud-oper-data xmlns="{CLOUD_NS}"/>')))
        oper = str(session.get(("subtree",
                   f'<afc-oper-data xmlns="{OPER_NS}"/>')))

    print("== AFC cloud statistics ==")
    for field in CLOUD_FIELDS:
        print(f"  {field:22s} {leaf(cloud, field)}")
    print("== Health check ==")
    for field in HEALTH_FIELDS:
        print(f"  {field:22s} {leaf(cloud, field)}")
    errors = re.search(r"<hc-error-status>(.*?)</hc-error-status>",
                       cloud, re.S)
    if errors:
        print("== Current blockers (hc-error-status) ==")
        for tag, value in re.findall(r"<([a-z0-9-]+)>([^<]*)</\1>",
                                     errors.group(1)):
            print(f"  {tag:22s} {value}")

    responses = re.findall(r"<ewlc-afc-ap-resp>.*?</ewlc-afc-ap-resp>",
                           oper, re.S)
    print(f"== Per-AP AFC responses: {len(responses)} ==")
    for response in responses:
        mac = leaf(response, "ap-mac")
        expiry = leaf(response, "expire-time")
        print(f"  ap {mac}  grant expires {expiry}")
    if not responses:
        print("  none (no 6 GHz APs with AFC activity on this controller)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
