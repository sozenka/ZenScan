"""
Small runner for convenience: reads `targets/domains.txt` and runs the CLI
with those authorized domains against the sample `targets/urls.txt`.

This is intentionally conservative: it only runs against the bundled sample
files and is intended to verify the command-line flow prior to publishing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DOMAINS_FILE = ROOT / "targets" / "domains.txt"
INPUT_FILE = ROOT / "targets" / "urls.txt"


def _read_domains(path: Path) -> str:
    if not path.exists():
        return ""
    items = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().startswith("#")]
    return ",".join(items)


if __name__ == "__main__":
    domains = _read_domains(DOMAINS_FILE)
    if not domains:
        print("No domains in targets/domains.txt — add at least one domain to run sample.")
        raise SystemExit(1)

    cmd = [sys.executable, "-m", "src.scraper", "--domains", domains, "--input", str(INPUT_FILE)]
    print("Running sample command:\n", " ".join(cmd))
    subprocess.run(cmd, check=True)
