"""Shared connection handling for the C9800 NETCONF scripts."""
import argparse
import getpass
import os
import sys


def add_device_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", required=True, help="controller address")
    parser.add_argument("--port", type=int, default=830)
    parser.add_argument("--user",
                        default=os.environ.get("WLC_USER", "admin"))
    parser.add_argument("--insecure", action="store_true",
                        help="skip SSH host key verification. Lab use "
                             "only: this accepts any server key.")


def connect(args):
    from ncclient import manager  # imported here so --help works without it
    from ncclient.transport.errors import SSHUnknownHostError
    # Password comes from the environment or an interactive prompt, never
    # from argv, where other local users could read it in the process list.
    password = os.environ.get("WLC_PASSWORD") or getpass.getpass(
        f"Password for {args.user}: ")
    try:
        return manager.connect(host=args.host, port=args.port,
                               username=args.user, password=password,
                               hostkey_verify=not args.insecure,
                               allow_agent=False, look_for_keys=False,
                               timeout=60, device_params={"name": "iosxe"})
    except SSHUnknownHostError:
        print(f"Host key for {args.host} is not in your known_hosts.\n"
              f"Connect once with: ssh -p {args.port} "
              f"{args.user}@{args.host}\n"
              "or, for a lab controller only, rerun with --insecure.",
              file=sys.stderr)
        sys.exit(1)
