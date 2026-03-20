"""Screenshot module for capturing Screen Time window."""

import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


def capture_screen_region(
    x: int, y: int, width: int, height: int, output_path: Path | None = None
) -> Path:
    """Capture a specific region of the screen.
    
    Args:
        x: X coordinate of the top-left corner
        y: Y coordinate of the top-left corner
        width: Width of the region
        height: Height of the region
        output_path: Output file path. If None, creates a temp file.
        
    Returns:
        Path to the screenshot file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(tempfile.gettempdir()) / f"screentime_{timestamp}.png"
    
    # Use macOS screencapture command with region
    subprocess.run(
        [
            "screencapture",
            "-x",  # No sound
            "-R", f"{x},{y},{width},{height}",
            str(output_path),
        ],
        check=True,
    )
    
    return output_path


def capture_full_screen(output_path: Path | None = None) -> Path:
    """Capture the full screen.
    
    Args:
        output_path: Output file path. If None, creates a temp file.
        
    Returns:
        Path to the screenshot file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(tempfile.gettempdir()) / f"screentime_{timestamp}.png"
    
    subprocess.run(
        [
            "screencapture",
            "-x",  # No sound
            str(output_path),
        ],
        check=True,
    )
    
    return output_path


def capture_window(window_name: str, output_path: Path | None = None) -> Path:
    """Capture a specific window by name using screencapture interactive mode.
    
    Note: This requires the window to be visible and will capture it directly.
    
    Args:
        window_name: Name of the window (used for naming only, actual capture is interactive)
        output_path: Output file path. If None, creates a temp file.
        
    Returns:
        Path to the screenshot file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = window_name.replace(" ", "_").replace("/", "_")
        output_path = Path(tempfile.gettempdir()) / f"{safe_name}_{timestamp}.png"
    
    # Capture the frontmost window
    subprocess.run(
        [
            "screencapture",
            "-x",  # No sound
            "-l",  # Capture window by ID (we'll use -w for interactive)
            str(output_path),
        ],
        check=True,
    )
    
    return output_path
