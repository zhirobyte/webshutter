#!/usr/bin/env python3
"""Connect crt.name discovery to the existing WebShutter engine."""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from discovery.crtname import discover

PROJECT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


def main():
    parser = argparse.ArgumentParser(
        description="WebShutter domain discovery and screenshot workflow"
    )
    parser.add_argument("domain", help="Root domain, e.g. example.com")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument(
        "--capture",
        action="store_true",
        help="Start Selenium screenshots after discovery"
    )
    args = parser.parse_args()

    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")

    name = args.name or (
        "discovery_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    if not PROJECT_RE.fullmatch(name):
        parser.error("Project name must contain only letters, digits, - or _")

    project_dir = Path("screenshots") / name
    project_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] Discovering: {args.domain}", flush=True)
    hosts = discover(args.domain)

    all_hosts = project_dir / "discovered-hosts.txt"
    all_hosts.write_text(
        "\n".join(hosts) + ("\n" if hosts else ""),
        encoding="utf-8"
    )

    selected = hosts[:args.limit]
    target_file = project_dir / "capture-targets.txt"
    target_file.write_text(
        "\n".join(selected) + ("\n" if selected else ""),
        encoding="utf-8"
    )

    print(f"[+] Discovered: {len(hosts)} hostnames")
    print(f"[+] Selected: {len(selected)} targets")
    print(f"[+] Full list: {all_hosts}")
    print(f"[+] Capture list: {target_file}")

    if not args.capture:
        print("[+] Discovery complete. No screenshots started.")
        return

    if not selected:
        print("[!] No targets available for screenshots.")
        return

    print("[+] Starting existing WebShutter engine...", flush=True)

    command = [
        sys.executable,
        str(Path(__file__).resolve().parent / "webshutter.py"),
        "--file",
        str(target_file.resolve()),
        "--name",
        name
    ]

    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
