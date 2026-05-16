"""
Offline generator: reads `targets/urls.txt` and writes `targets_found.txt` by
including only URLs that contain GET query parameters. This is a safe,
deterministic way to produce a sample `targets_found.txt` for demos and CI.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent.parent
INPUT = ROOT / "targets" / "urls.txt"
OUTPUT = ROOT / "targets_found.txt"


def main() -> int:
    if not INPUT.exists():
        print("No targets/urls.txt found.")
        return 1

    kept = []
    for line in INPUT.read_text(encoding="utf-8").splitlines():
        u = line.strip()
        if not u or u.startswith("#"):
            continue
        parsed = urlparse(u)
        qs = parse_qs(parsed.query)
        if qs:
            kept.append(u)

    OUTPUT.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    print(f"Wrote {len(kept)} URLs to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
