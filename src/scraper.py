from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Iterable

try:
    from .validator import (
        AsyncEndpointValidator,
        DomainPolicy,
        EASMEndpointInventory,
        EndpointResult,
        UserAgentRotator,
        write_clean_url_list,
    )
except ImportError:
    from validator import (
        AsyncEndpointValidator,
        DomainPolicy,
        EASMEndpointInventory,
        EndpointResult,
        UserAgentRotator,
        write_clean_url_list,
    )


DEFAULT_INPUT_FILE = Path("targets/urls.txt")
DEFAULT_OUTPUT_FILE = Path("targets_found.txt")


def _read_url_lines(source_file: Path) -> list[str]:
    if not source_file.exists():
        return []

    urls: list[str] = []
    for line in source_file.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            urls.append(value)
    return urls


class SozenScraper:
    """Loads authorized URLs and validates them concurrently."""

    def __init__(
        self,
        allowed_domains: Iterable[str],
        input_file: Path = DEFAULT_INPUT_FILE,
        output_file: Path = DEFAULT_OUTPUT_FILE,
        concurrency: int = 20,
        timeout_seconds: int = 10,
    ) -> None:
        self._input_file = input_file
        self._output_file = output_file
        self._inventory = EASMEndpointInventory(
            domain_policy=DomainPolicy(allowed_domains),
            validator=AsyncEndpointValidator(
                UserAgentRotator(),
                concurrency=concurrency,
                timeout_seconds=timeout_seconds,
            ),
        )

    def load_candidates(self) -> list[str]:
        return _read_url_lines(self._input_file)

    async def run(self, candidates: Iterable[str] | None = None) -> list[EndpointResult]:
        urls = list(candidates) if candidates is not None else self.load_candidates()
        if not urls:
            return []

        results = await self._inventory.discover(urls)
        write_clean_url_list(results, str(self._output_file))
        return results


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ZenScan defensive endpoint inventory")
    parser.add_argument(
        "--domains",
        required=True,
        help="Comma-separated list of authorized domains, for example example.org,api.example.org",
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_FILE),
        help="File containing candidate URLs, one per line",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_FILE),
        help="Output file for clean URLs",
    )
    parser.add_argument("--concurrency", type=int, default=20, help="Maximum in-flight requests")
    parser.add_argument("--timeout", type=int, default=10, help="Per-request timeout in seconds")
    return parser.parse_args()


async def _run_cli() -> int:
    args = _parse_args()
    input_file = Path(args.input)
    output_file = Path(args.output)
    allowed_domains = [item.strip() for item in args.domains.split(",") if item.strip()]

    scraper = SozenScraper(
        allowed_domains=allowed_domains,
        input_file=input_file,
        output_file=output_file,
        concurrency=args.concurrency,
        timeout_seconds=args.timeout,
    )

    results = await scraper.run()
    print(f"[+] Completed. {len(results)} live authorized endpoints written to {output_file}")
    for item in results[:5]:
        print(f"[+] {item.url} | params={item.parameters} | status={item.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_run_cli()))