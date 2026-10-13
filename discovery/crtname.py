#!/usr/bin/env python3
"""Certificate-transparency hostname discovery via crt.name."""

import argparse
import re
import urllib.parse
import urllib.request
from pathlib import Path

HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)


def discover(domain: str) -> list[str]:
    domain = domain.strip().lower().rstrip(".")

    if not HOSTNAME_RE.fullmatch(domain):
        raise ValueError("Invalid root domain")

    url = "https://crt.name/v1/search?" + urllib.parse.urlencode(
        {"apex": domain}
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "WebShutter/1.0"}
    )

    with urllib.request.urlopen(request, timeout=45) as response:
        text = response.read(20 * 1024 * 1024 + 1)

    if len(text) > 20 * 1024 * 1024:
        raise ValueError("Discovery response exceeds 20 MB")

    hosts = set()

    for line in text.decode("utf-8", errors="replace").splitlines():
        host = line.strip().lower().rstrip(".")

        if host.startswith("*."):
            host = host[2:]

        if HOSTNAME_RE.fullmatch(host):
            if host == domain or host.endswith("." + domain):
                hosts.add(host)

    return sorted(hosts)


def main():
    parser = argparse.ArgumentParser(
        description="Discover subdomains from crt.name"
    )
    parser.add_argument("domain", help="Root domain, e.g. example.com")
    parser.add_argument(
        "-o", "--output",
        default="discovered-hosts.txt",
        help="Output filename"
    )

    args = parser.parse_args()

    hosts = discover(args.domain)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(hosts) + ("\n" if hosts else ""),
        encoding="utf-8"
    )

    print(f"[+] Root domain: {args.domain}")
    print(f"[+] Unique hostnames: {len(hosts)}")
    print(f"[+] Saved: {output}")


if __name__ == "__main__":
    main()
