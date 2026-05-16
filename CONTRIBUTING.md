# Contributing to ZenScan

Thank you for interest in contributing to ZenScan! This document outlines guidelines for contributions.

## Code of Conduct

All contributors must adhere to responsible security practices and comply with applicable laws. We do not accept contributions that enable offensive reconnaissance or unauthorized access.

## Getting Started

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`.
3. Install dev dependencies: `pip install -e ".[dev]"`.
4. Write tests for your changes.
5. Ensure tests pass: `pytest tests/`.
6. Submit a pull request with a clear description.

## Coding Standards

- Write Python 3.10+ compatible code.
- Follow PEP 8 style guidelines.
- Use type hints where reasonable.
- Include docstrings for public functions and classes.
- Avoid external dependencies unless absolutely necessary.

## Testing

Run tests locally:

```bash
pytest tests/ -v --cov=src
```

All new features must include corresponding tests.

## Documentation

Update README.md and docstrings if your change affects user-facing behavior.

## Scope Constraints

Contributions must:
- Serve defensive or auditing purposes only.
- Not include dork lists, scrapers, or offensive recon logic.
- Maintain compatibility with the project's responsible-use policy.

## Questions?

Open an issue or email `security@example.com` with questions about contribution scope.
