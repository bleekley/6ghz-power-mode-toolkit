#!/usr/bin/env python3
"""Read the C9800 AFC operational state over NETCONF and summarize it.

Covers the cloud statistics (message counters, health check, blockers)
and the per-AP AFC responses when 6 GHz APs are present.

    python3 get_afc_oper.py --host 198.51.100.10 --user admin
"""
import argparse
import sys
import xml.etree.ElementTree as ET

from common import add_device_args, connect

CLOUD_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-afc-cloud-oper"
OPER_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-afc-oper"

CLOUD_FIELDS = ["num-afc-ap", "afc-msg-sent", "afc-msg-rcvd", "afc-msg-err",
                "afc-msg-pending", "min-msg-rtt", "max-msg-rtt", "avg-rtt"]
HEALTH_FIELDS = ["hc-timestamp", "query-in-progress",
                 "country-not-supported", "num-hc-down"]


def parse(reply: str, label: str):
    try:
        return ET.fromstring(reply)
    except ET.ParseError as err:
        print(f"could not parse the {label} reply: {err}", file=sys.stderr)
        sys.exit(2)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def leaf(root, ns: str, tag: str):
    element = root.find(f".//{{{ns}}}{tag}")
    return element.text if element is not None else None


def summarize(cloud: str, oper: str) -> int:
    """Print the AFC summary from the two get replies; return rc."""
    cloud_root = parse(cloud, "afc-cloud-oper")
    oper_root = parse(oper, "afc-oper")

    if cloud_root.find(f".//{{{CLOUD_NS}}}afc-cloud-oper-data") is None:
        print("the reply carried no afc-cloud-oper data: the model may be "
              "unsupported on this release, or the reply was incomplete",
              file=sys.stderr)
        return 1

    print("== AFC cloud statistics ==")
    for field in CLOUD_FIELDS:
        print(f"  {field:22s} {leaf(cloud_root, CLOUD_NS, field)}")
    print("== Health check ==")
    for field in HEALTH_FIELDS:
        print(f"  {field:22s} {leaf(cloud_root, CLOUD_NS, field)}")

    # The healthcheck carries a YANG choice: a healthy service reports the
    # cloud-hc-ok leaf, an unhealthy one reports an hc-error-status
    # container naming the blocker. Exactly one of the two appears.
    ok = leaf(cloud_root, CLOUD_NS, "cloud-hc-ok")
    errors = cloud_root.find(f".//{{{CLOUD_NS}}}hc-error-status")
    if ok is not None:
        print(f"== Cloud health: OK (cloud-hc-ok = {ok}) ==")
    if errors is not None:
        print("== Current blockers (hc-error-status) ==")
        for element in errors.iter():
            if element is errors or len(element):
                continue
            print(f"  {local(element.tag):22s} {element.text}")
    if ok is None and errors is None:
        print("== Cloud health: not reported (neither cloud-hc-ok nor "
              "hc-error-status present) ==")

    if oper_root.find(f".//{{{OPER_NS}}}afc-oper-data") is None:
        print("== Per-AP AFC responses: no afc-oper data in the reply ==")
        return 1
    responses = list(oper_root.iter(f"{{{OPER_NS}}}ewlc-afc-ap-resp"))
    print(f"== Per-AP AFC responses: {len(responses)} ==")
    for response in responses:
        mac = response.findtext(f"{{{OPER_NS}}}ap-mac")
        expiry = response.findtext(f"{{{OPER_NS}}}expire-time")
        print(f"  ap {mac}  grant expires {expiry}")
    if not responses:
        print("  none (no 6 GHz APs with AFC activity on this controller)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_device_args(parser)
    args = parser.parse_args()

    with connect(args) as session:
        cloud = str(session.get(("subtree",
                    f'<afc-cloud-oper-data xmlns="{CLOUD_NS}"/>')))
        oper = str(session.get(("subtree",
                   f'<afc-oper-data xmlns="{OPER_NS}"/>')))
    return summarize(cloud, oper)


if __name__ == "__main__":
    sys.exit(main())
