#!/usr/bin/env python3
"""
Lightweight README link checker for Awesome Learn repositories.

Usage:
    python scripts/check_links.py
"""

from __future__ import annotations

import re
import urllib.request
import urllib.error
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"
LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)]+)\)")
USER_AGENT = "awesome-learn-link-checker/1.0"


def extract_links(text: str) -> list[str]:
    return [m.group(1).strip() for m in LINK_RE.finditer(text)]


def check_url(url: str, timeout: int = 15) -> tuple[bool, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            return (200 <= status < 400, f"HTTP {status}")
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return False, f"URL error: {exc.reason}"
    except Exception as exc:
        return False, f"Error: {exc}"


def main() -> int:
    if not README.exists():
        print("README.md not found.")
        return 1

    links = extract_links(README.read_text(encoding="utf-8"))
    if not links:
        print("No HTTP/HTTPS links found.")
        return 0

    failed = []
    for url in links:
        ok, info = check_url(url)
        print(f"{'OK' if ok else 'FAIL'}  {url}  [{info}]")
        if not ok:
            failed.append((url, info))

    if failed:
        print(f"\n{len(failed)} link(s) failed.")
        return 1

    print(f"\nAll {len(links)} link(s) passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
