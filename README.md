# ZenScan

[![CI](https://github.com/yourusername/zenscan/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/zenscan/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sozenka Audit Framework (SAF) — A defensive endpoint auditing tool for organizations to inventory and validate their own exposed assets.

## Features

- **Async I/O**: Uses `asyncio` + `aiohttp` for high-throughput concurrent validation.
- **Domain Scoping**: Restricts all scanning to explicitly authorized domains.
- **User-Agent Rotation**: Maintains operational compatibility with standard request patterns.
- **Clean Results**: Outputs only live endpoints with GET parameters for further analysis.
- **TUI & CLI**: Both interactive and command-line interfaces for flexibility.

## Installation

```bash
pip install -e .
```

Or install with dev tools for testing:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Command-Line Interface

Add your authorized URLs to `targets/urls.txt` (one per line), then run:

```bash
python -m src.scraper --domains example.org,api.example.org
```

Options:
- `--domains` (required): Comma-separated list of authorized domains.
- `--input` (optional): Input file path; default `targets/urls.txt`.
- `--output` (optional): Output file path; default `targets_found.txt`.
- `--concurrency` (optional): Max in-flight requests; default `20`.
- `--timeout` (optional): Per-request timeout in seconds; default `10`.

### Interactive TUI

For a guided, interactive experience:

```bash
python -m src.tui
```

The TUI will prompt you for:
- Authorized domains
- Input and output file paths
- Concurrency level

Then display results in a formatted table.

### Offline Sample Generation

To generate sample results without network access:

```bash
python tools/generate_offline_results.py
```

This creates `targets_found.txt` from `targets/urls.txt` by filtering for URLs with query parameters.

### Convenience Runner

Run the sample configuration stored in `targets/domains.txt`:

```bash
python run_sample.py
```

## Architecture

```
src/
  validator.py      Core async endpoint validation engine
  scraper.py        CLI orchestrator and domain-policy application
  tui.py            Interactive terminal UI
tools/
  generate_offline_results.py   Offline sample generator
tests/
  test_validator.py Unit tests for core validator logic
```

## Testing

Run the test suite:

```bash
pytest tests/ -v --cov=src
```

## Scope & Responsible Use

**ZenScan is for authorized asset auditing only.**

- Use only on infrastructure you own or have explicit written permission to test.
- Do not use against third-party systems without authorization.
- See [RESPONSIBLE_DISCLOSURE.md](RESPONSIBLE_DISCLOSURE.md) for full policy.

## Contributing

Contributions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.
