"""GUI automation module for navigating Screen Time settings."""

import subprocess
import time
from datetime import date, timedelta

import pyautogui


# Disable pyautogui fail-safe for automation
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


def open_screen_time_settings() -> None:
    """Open System Settings and navigate to Screen Time."""
    # Open System Settings directly to Screen Time
    subprocess.run(
        ["open", "x-apple.systempreferences:com.apple.Screen-Time-Settings.extension"],
        check=True,
    )
    # Wait for the window to open
    time.sleep(2)


def close_system_settings() -> None:
    """Close System Settings application."""
    subprocess.run(
        ["osascript", "-e", 'quit app "System Settings"'],
        check=False,
    )


def click_previous_day() -> None:
    """Click the previous day button in Screen Time.
    
    The button is typically a '<' chevron on the left side of the date display.
    """
    # Use AppleScript to click the previous day button
    script = '''
    tell application "System Events"
        tell process "System Settings"
            -- Find and click the previous day button
            -- The button is typically in the Screen Time content area
            click button 1 of group 1 of scroll area 1 of group 1 of group 2 of splitter group 1 of group 1 of window 1
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=False)
    time.sleep(1)


def click_next_day() -> None:
    """Click the next day button in Screen Time."""
    script = '''
    tell application "System Events"
        tell process "System Settings"
            -- Find and click the next day button
            click button 2 of group 1 of scroll area 1 of group 1 of group 2 of splitter group 1 of group 1 of window 1
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=False)
    time.sleep(1)


def navigate_to_date(target_date: date) -> None:
    """Navigate to a specific date in Screen Time.
    
    Args:
        target_date: The date to navigate to
    """
    today = date.today()
    days_diff = (today - target_date).days
    
    if days_diff < 0:
        raise ValueError("Cannot navigate to future dates")
    
    # Click previous day button for each day we need to go back
    for _ in range(days_diff):
        click_previous_day()


def navigate_date_range(start_date: date, end_date: date, callback) -> None:
    """Navigate through a date range and call callback for each date.
    
    Args:
        start_date: Start date (earliest)
        end_date: End date (latest, usually today or recent)
        callback: Function to call for each date, receives the current date
    """
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")
    
    # First navigate to end_date
    navigate_to_date(end_date)
    
    # Process end_date
    callback(end_date)
    
    # Then navigate backwards to start_date
    current_date = end_date
    while current_date > start_date:
        click_previous_day()
        current_date -= timedelta(days=1)
        callback(current_date)


def get_screen_time_window_bounds() -> tuple[int, int, int, int]:
    """Get the bounds of the System Settings window.
    
    Returns:
        Tuple of (x, y, width, height)
    """
    script = '''
    tell application "System Events"
        tell process "System Settings"
            set win to window 1
            set winPos to position of win
            set winSize to size of win
            return (item 1 of winPos) & "," & (item 2 of winPos) & "," & (item 1 of winSize) & "," & (item 2 of winSize)
        end tell
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=True,
    )
    parts = result.stdout.strip().split(",")
    return int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])


def bring_window_to_front() -> None:
    """Bring System Settings window to front."""
    subprocess.run(
        ["osascript", "-e", 'tell app "System Settings" to activate'],
        check=True,
    )
    time.sleep(0.5)


def scroll_down_in_screen_time() -> None:
    """Scroll down in the Screen Time content area to see more apps."""
    script = '''
    tell application "System Events"
        tell process "System Settings"
            set frontmost to true
            -- Scroll in the scroll area
            scroll scroll area 1 of group 1 of group 2 of splitter group 1 of group 1 of window 1 by -3
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=False)
    time.sleep(0.5)
