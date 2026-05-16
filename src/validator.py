from __future__ import annotations

import asyncio
from dataclasses import dataclass
from itertools import cycle
from typing import Iterable
from urllib.parse import parse_qs, urlparse

import aiohttp

DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


class UserAgentRotator:
    """Returns a different User-Agent string on each request."""

    def __init__(self, user_agents: Iterable[str] | None = None) -> None:
        # If caller passed None, use defaults; if caller passed an explicit
        # iterable (including empty), respect it and validate non-empty.
        if user_agents is None:
            values = list(DEFAULT_USER_AGENTS)
        else:
            values = list(user_agents)

        if not values:
            raise ValueError("User-Agent list cannot be empty")
        self._agents = cycle(values)

    def next(self) -> str:
        return next(self._agents)


class DomainPolicy:
    """Restricts scanning to explicitly authorized domains."""

    def __init__(self, allowed_domains: Iterable[str]) -> None:
        self._allowed = {d.lower().strip() for d in allowed_domains if d.strip()}
        if not self._allowed:
            raise ValueError("Provide at least one authorized domain")

    def is_allowed(self, url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return any(host == domain or host.endswith(f".{domain}") for domain in self._allowed)


@dataclass(slots=True)
class EndpointResult:
    url: str
    status: int
    parameters: list[str]


class AsyncEndpointValidator:
    """Validates candidate URLs concurrently and keeps only live GET endpoints."""

    def __init__(
        self,
        user_agent_rotator: UserAgentRotator,
        concurrency: int = 50,
        timeout_seconds: int = 10,
    ) -> None:
        self._ua_rotator = user_agent_rotator
        self._concurrency = max(1, concurrency)
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async def _check_one(self, session: aiohttp.ClientSession, url: str) -> EndpointResult | None:
        headers = {"User-Agent": self._ua_rotator.next()}
        try:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status < 200 or response.status >= 400:
                    return None

                parsed = urlparse(str(response.url))
                params = sorted(parse_qs(parsed.query).keys())
                if not params:
                    return None

                return EndpointResult(url=str(response.url), status=response.status, parameters=params)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

    async def run(self, urls: Iterable[str]) -> list[EndpointResult]:
        connector = aiohttp.TCPConnector(limit=self._concurrency)
        async with aiohttp.ClientSession(connector=connector, timeout=self._timeout) as session:
            tasks = [self._check_one(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]


class EASMEndpointInventory:
    """High-level orchestration class for defensive endpoint inventory."""

    def __init__(self, domain_policy: DomainPolicy, validator: AsyncEndpointValidator) -> None:
        self._domain_policy = domain_policy
        self._validator = validator

    async def discover(self, candidate_urls: Iterable[str]) -> list[EndpointResult]:
        authorized = [url for url in candidate_urls if self._domain_policy.is_allowed(url)]
        return await self._validator.run(authorized)


def write_clean_url_list(results: Iterable[EndpointResult], output_file: str = "targets_found.txt") -> None:
    with open(output_file, "w", encoding="utf-8") as handle:
        for item in results:
            handle.write(f"{item.url}\n")


async def main() -> None:
    allowed_domains = {"example.org"}
    candidate_urls = [
        "https://www.example.org/products?id=10",
        "https://www.example.org/about",
        "https://blog.example.org/posts?category=security",
        "https://unrelated-site.test/page?x=1",
    ]

    inventory = EASMEndpointInventory(
        domain_policy=DomainPolicy(allowed_domains),
        validator=AsyncEndpointValidator(UserAgentRotator()),
    )

    results = await inventory.discover(candidate_urls)
    write_clean_url_list(results)

    for item in results:
        print(f"[+] Live endpoint: {item.url} | params={item.parameters} | status={item.status}")

    print(f"\n[!] Completed. {len(results)} authorized GET endpoints saved to targets_found.txt")


if __name__ == "__main__":
    asyncio.run(main())