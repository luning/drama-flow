"""Page operations — thin wrappers around opencli_client for common agent actions."""

from pathlib import Path
from typing import Optional

from web.controller import opencli_client as cli


def screenshot(session: str, output_path: str) -> Path:
    """Capture current viewport to PNG. Returns output_path."""
    return cli.screenshot(session, output_path)


def navigate(session: str, url: str, post_delay: float = 0.5):
    """Navigate to URL and wait for page load."""
    cli.open_url(session, url, post_delay=post_delay)


def click(session: str, target: str, post_delay: float = 0.5) -> dict:
    """Click element by ref number (from state) or CSS selector."""
    return cli.click(session, target, post_delay=post_delay)


def click_by_text(session: str, text: str, post_delay: float = 0.5) -> dict:
    """Click first visible element whose text matches."""
    return cli.click_by_text(session, text, post_delay=post_delay)


def type_text(session: str, text: str, post_delay: float = 0.5):
    """Type text into the focused element."""
    cli.type_text(session, text, post_delay=post_delay)


def fill_input(session: str, target: str, text: str, post_delay: float = 0.5):
    """Fill input by ref number or CSS selector."""
    cli.fill_input(session, target, text, post_delay=post_delay)


def scroll(session: str, direction: str, amount: int = 500, post_delay: float = 0.5):
    """Scroll viewport. direction: 'up' | 'down'."""
    cli.scroll(session, direction, amount=amount, post_delay=post_delay)


def go_back(session: str, post_delay: float = 0.5):
    """Browser back navigation."""
    cli.go_back(session, post_delay=post_delay)


def get_state(session: str) -> str:
    """Return page state snapshot with element refs."""
    return cli.get_state(session)


def get_current_url(session: str) -> str:
    """Return the current page URL."""
    return cli.get_url(session)


def get_title(session: str) -> str:
    """Return the current page title."""
    return cli.get_title(session)


def get_dom(session: str) -> Optional[str]:
    """Return serialized DOM HTML. Returns None on failure."""
    return cli.get_dom(session)


def wait_for_text(session: str, text: str, timeout: float = 5.0) -> bool:
    """Wait until page contains the given text."""
    return cli.wait_for_text(session, text, timeout=timeout)


def wait_for_selector(session: str, selector: str, timeout: float = 5.0) -> bool:
    """Wait until CSS selector matches."""
    return cli.wait_for_selector(session, selector, timeout=timeout)
