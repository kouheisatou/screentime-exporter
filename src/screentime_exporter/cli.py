"""CLI module for Screen Time Exporter."""

import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

import click

from .automation import (
    bring_window_to_front,
    click_previous_day,
    close_system_settings,
    get_screen_time_window_bounds,
    open_screen_time_settings,
)
from .exporter import export_to_csv
from .ocr import extract_text_lines
from .parser import DailyScreenTime, parse_screen_time_text
from .screenshot import capture_screen_region


def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


@click.command()
@click.option(
    "--start-date",
    required=True,
    type=str,
    help="Start date in YYYY-MM-DD format",
)
@click.option(
    "--end-date",
    required=True,
    type=str,
    help="End date in YYYY-MM-DD format",
)
@click.option(
    "--output",
    "-o",
    default="screentime.csv",
    type=click.Path(),
    help="Output CSV file path",
)
@click.option(
    "--keep-screenshots",
    is_flag=True,
    help="Keep screenshot files after processing",
)
@click.option(
    "--screenshot-dir",
    type=click.Path(),
    help="Directory to save screenshots",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    start_date: str,
    end_date: str,
    output: str,
    keep_screenshots: bool,
    screenshot_dir: str | None,
    verbose: bool,
) -> None:
    """Export macOS Screen Time data to CSV.
    
    This tool automatically captures screenshots of the Screen Time settings,
    navigates through dates, and extracts usage data using OCR.
    
    Example:
        screentime-export --start-date 2026-03-01 --end-date 2026-03-20 -o data.csv
    """
    try:
        start = parse_date(start_date)
        end = parse_date(end_date)
    except ValueError as e:
        click.echo(f"Error: Invalid date format. Use YYYY-MM-DD. ({e})", err=True)
        sys.exit(1)
    
    if start > end:
        click.echo("Error: Start date must be before or equal to end date.", err=True)
        sys.exit(1)
    
    if end > date.today():
        click.echo("Error: End date cannot be in the future.", err=True)
        sys.exit(1)
    
    # Setup screenshot directory
    if screenshot_dir:
        ss_dir = Path(screenshot_dir)
        ss_dir.mkdir(parents=True, exist_ok=True)
    else:
        ss_dir = Path(tempfile.mkdtemp(prefix="screentime_"))
    
    if verbose:
        click.echo(f"Screenshot directory: {ss_dir}")
    
    click.echo("Opening Screen Time settings...")
    open_screen_time_settings()
    
    try:
        bring_window_to_front()
        
        # Get window bounds for capturing
        x, y, width, height = get_screen_time_window_bounds()
        if verbose:
            click.echo(f"Window bounds: {x}, {y}, {width}x{height}")
        
        all_data: list[DailyScreenTime] = []
        
        # Navigate to end date first, then go backwards
        days_from_today = (date.today() - end).days
        click.echo(f"Navigating to {end}...")
        
        for _ in range(days_from_today):
            click_previous_day()
        
        # Process each date from end to start
        current = end
        total_days = (end - start).days + 1
        processed = 0
        
        with click.progressbar(length=total_days, label="Processing dates") as bar:
            while current >= start:
                if verbose:
                    click.echo(f"\nProcessing {current}...")
                
                # Capture screenshot
                ss_path = ss_dir / f"screentime_{current.isoformat()}.png"
                capture_screen_region(x, y, width, height, ss_path)
                
                # Perform OCR
                lines = extract_text_lines(ss_path)
                
                if verbose:
                    click.echo(f"  OCR found {len(lines)} text lines")
                
                # Parse the data
                day_data = parse_screen_time_text(lines, current)
                all_data.append(day_data)
                
                if verbose:
                    click.echo(f"  Found {len(day_data.apps)} apps, total: {day_data.total_minutes} min")
                
                # Clean up screenshot if not keeping
                if not keep_screenshots:
                    ss_path.unlink(missing_ok=True)
                
                # Navigate to previous day
                if current > start:
                    click_previous_day()
                
                current -= timedelta(days=1)
                processed += 1
                bar.update(1)
        
        # Export to CSV
        output_path = Path(output)
        export_to_csv(all_data, output_path)
        
        click.echo(f"\nExported {len(all_data)} days of data to {output_path}")
        
        # Show summary
        total_apps = sum(len(d.apps) for d in all_data)
        total_minutes = sum(d.total_minutes for d in all_data)
        click.echo(f"Total: {total_apps} app entries, {total_minutes} minutes ({total_minutes / 60:.1f} hours)")
        
    finally:
        click.echo("Closing Screen Time settings...")
        close_system_settings()
        
        # Clean up temp directory if not keeping screenshots
        if not keep_screenshots and not screenshot_dir:
            import shutil
            shutil.rmtree(ss_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
