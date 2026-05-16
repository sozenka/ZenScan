"""Interactive TUI for ZenScan using Rich."""
from __future__ import annotations

import asyncio
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt

from .scraper import SozenScraper
from .validator import EndpointResult

console = Console()


def prompt_domains() -> str:
    """Prompt user for authorized domains."""
    console.print(
        "[cyan]Enter authorized domains (comma-separated):[/cyan]\n"
        "  Example: [yellow]example.org,api.example.org[/yellow]"
    )
    return Prompt.ask("[bold]Domains").strip()


def prompt_input_file() -> Path:
    """Prompt user for input URL file."""
    default = "targets/urls.txt"
    path_str = Prompt.ask(
        f"[cyan]Input file with candidate URLs[/cyan]",
        default=default
    )
    return Path(path_str)


def prompt_output_file() -> Path:
    """Prompt user for output file."""
    default = "targets_found.txt"
    path_str = Prompt.ask(
        f"[cyan]Output file for results[/cyan]",
        default=default
    )
    return Path(path_str)


def prompt_concurrency() -> int:
    """Prompt user for concurrency level."""
    default = "20"
    val_str = Prompt.ask(
        "[cyan]Max concurrent requests[/cyan]",
        default=default
    )
    try:
        return int(val_str)
    except ValueError:
        console.print("[red]Invalid number. Using 20.[/red]")
        return 20


def display_results(results: list[EndpointResult]) -> None:
    """Display results in a formatted table."""
    if not results:
        console.print("[yellow]No live endpoints found.[/yellow]")
        return

    table = Table(title="Live Endpoints")
    table.add_column("URL", style="cyan", no_wrap=False)
    table.add_column("Status", style="green")
    table.add_column("Parameters", style="magenta")

    for item in results:
        param_str = ", ".join(item.parameters) if item.parameters else "—"
        table.add_row(item.url, str(item.status), param_str)

    console.print(table)


async def run_tui() -> int:
    """Main TUI entry point."""
    console.print(
        Panel.fit(
            "[bold cyan]ZenScan Endpoint Auditor[/bold cyan]",
            border_style="blue"
        )
    )

    domains_str = prompt_domains()
    if not domains_str:
        console.print("[red]No domains provided. Exiting.[/red]")
        return 1

    input_file = prompt_input_file()
    if not input_file.exists():
        console.print(f"[red]File not found: {input_file}[/red]")
        return 1

    output_file = prompt_output_file()
    concurrency = prompt_concurrency()

    allowed_domains = [d.strip() for d in domains_str.split(",") if d.strip()]

    scraper = SozenScraper(
        allowed_domains=allowed_domains,
        input_file=input_file,
        output_file=output_file,
        concurrency=concurrency,
    )

    console.print("\n[bold]Running scan...[/bold]")
    with Progress() as progress:
        task = progress.add_task("[cyan]Validating endpoints...", total=None)
        results = await scraper.run()
        progress.update(task, completed=True)

    console.print()
    display_results(results)

    console.print(
        f"\n[green]✓ Completed. {len(results)} live endpoints written to [bold]{output_file}[/bold][/green]"
    )
    return 0


def main() -> int:
    """Entry point for TUI CLI."""
    return asyncio.run(run_tui())


if __name__ == "__main__":
    raise SystemExit(main())
