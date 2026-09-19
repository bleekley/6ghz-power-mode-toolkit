"""Shared connection handling for the C9800 NETCONF scripts."""
import argparse
import getpass
import os


def add_device_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", required=True, help="controller address")
    parser.add_argument("--port", type=int, default=830)
    parser.add_argument("--user",
                        default=os.environ.get("WLC_USER", "admin"))
    parser.add_argument("--password",
                        default=os.environ.get("WLC_PASSWORD"),
                        help="or set WLC_PASSWORD; prompts if absent")


def connect(args):
    from ncclient import manager  # imported here so --help works without it
    password = args.password or getpass.getpass(f"Password for {args.user}: ")
    return manager.connect(host=args.host, port=args.port,
                           username=args.user, password=password,
                           hostkey_verify=False, allow_agent=False,
                           look_for_keys=False, timeout=60,
                           device_params={"name": "iosxe"})
