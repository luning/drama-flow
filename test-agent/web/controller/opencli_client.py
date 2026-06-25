"""
OpenCLI browser controller — subprocess wrapper around `opencli browser <session> ...`.

All functions raise OpenCLIError on non-zero exit or invalid JSON response.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Union

OPENCLI = "opencli"


class OpenCLIError(Exception):
    """Raised when an opencli command exits with non-zero status."""


def _run(session: str, args: list[str], timeout: int = 30) -> str:
    """Run `opencli browser <session> <args>` and return stdout as text."""
    cmd = [OPENCLI, "browser", session] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        raise OpenCLIError("opencli not found — check that @jackwener/opencli is installed and in PATH")
    except subprocess.TimeoutExpired:
        raise OpenCLIError(f"opencli command timed out after {timeout}s: {' '.join(cmd)}")
    if r.returncode != 0:
        err = r.stderr.strip() or r.stdout.strip() or f"exit code {r.returncode}"
        raise OpenCLIError(f"opencli {' '.join(args[:2])} failed: {err}")
    return r.stdout


def _run_json(session: str, args: list[str], timeout: int = 30) -> dict:
    """Run a command and parse its JSON stdout."""
    raw = _run(session, args, timeout=timeout)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


# --- Navigation ---

def open_url(session: str, url: str, post_delay: float = 0.5) -> str:
    """Navigate to URL. Returns stdout."""
    out = _run(session, ["open", url])
    if post_delay:
        time.sleep(post_delay)
    return out


def go_back(session: str, post_delay: float = 0.5) -> str:
    out = _run(session, ["back"])
    if post_delay:
        time.sleep(post_delay)
    return out


# --- Page state ---

def get_state(session: str) -> str:
    """Return page state snapshot (URL, title, interactive elements with [N] refs)."""
    return _run(session, ["state"])


def get_url(session: str) -> str:
    """Return current page URL via JS eval."""
    raw = _run(session, ["eval", "location.href"])
    return raw.strip().strip('"')


def get_title(session: str) -> str:
    """Return current page title."""
    raw = _run(session, ["eval", "document.title"])
    return raw.strip().strip('"')


# --- Screenshot ---

def screenshot(session: str, output_path: Union[str, Path]) -> Path:
    """Capture current viewport to PNG. Returns output_path."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    _run(session, ["screenshot", str(out.resolve())])
    return out


# --- Interaction ---

def click(session: str, target: str, post_delay: float = 0.5) -> dict:
    """Click element by ref number, CSS selector, or --text/--role flags.

    target can be a numeric ref ("12"), CSS selector (".btn"), or
    a semantic string for --text ("登录") — callers that want semantic
    matching should use click_by_text() instead.
    """
    out = _run_json(session, ["click", target])
    if post_delay:
        time.sleep(post_delay)
    return out


def click_by_text(session: str, text: str, post_delay: float = 0.5) -> dict:
    """Click first element whose visible text contains the given string."""
    out = _run_json(session, ["click", "--text", text])
    if post_delay:
        time.sleep(post_delay)
    return out


def click_by_role(session: str, role: str, name: str = "", post_delay: float = 0.5) -> dict:
    """Click by ARIA role and optional accessible name."""
    args = ["click", "--role", role]
    if name:
        args += ["--name", name]
    out = _run_json(session, args)
    if post_delay:
        time.sleep(post_delay)
    return out


def type_text(session: str, text: str, post_delay: float = 0.5) -> dict:
    """Type text into the currently focused element."""
    out = _run_json(session, ["type", text])
    if post_delay:
        time.sleep(post_delay)
    return out


def fill_input(session: str, target: str, text: str, post_delay: float = 0.5) -> dict:
    """Fill an input/textarea by ref, CSS selector, or --label text."""
    out = _run_json(session, ["fill", target, text])
    if post_delay:
        time.sleep(post_delay)
    return out


def scroll(session: str, direction: str, amount: int = 500, post_delay: float = 0.5) -> str:
    """Scroll viewport. direction: 'up' | 'down'."""
    out = _run(session, ["scroll", direction, "--amount", str(amount)])
    if post_delay:
        time.sleep(post_delay)
    return out


def press_key(session: str, key: str, post_delay: float = 0.3) -> str:
    """Press a keyboard key (e.g. 'Enter', 'Tab', 'Escape')."""
    out = _run(session, ["keys", key])
    if post_delay:
        time.sleep(post_delay)
    return out


# --- Element finding ---

def find_by_text(session: str, text: str, limit: int = 20) -> dict:
    """Find elements whose visible text contains the string. Returns JSON."""
    return _run_json(session, ["find", "--text", text, "--limit", str(limit)])


def find_by_css(session: str, selector: str, limit: int = 20) -> dict:
    """Find elements by CSS selector. Returns JSON."""
    return _run_json(session, ["find", "--css", selector, "--limit", str(limit)])


def find_by_role(session: str, role: str, name: str = "", limit: int = 20) -> dict:
    """Find elements by ARIA role and optional accessible name."""
    args = ["find", "--role", role, "--limit", str(limit)]
    if name:
        args += ["--name", name]
    return _run_json(session, args)


def find_inputs(session: str) -> dict:
    """Find all input/textarea fields."""
    return _run_json(session, ["find", "--role", "textbox", "--limit", "30"])


# --- Error / monitoring ---

def get_console_errors(session: str, since: str = "5m") -> str:
    """Return recent console error messages."""
    return _run(session, ["console", "--level", "error", "--since", since])


def get_network_errors(session: str, since: str = "5m") -> str:
    """Return failed network requests (status 0 or >= 400)."""
    return _run(session, ["network", "--failed", "--since", since])


# --- DOM ---

def get_dom(session: str) -> Optional[str]:
    """Return page DOM HTML via JS eval. Returns None on failure."""
    try:
        return _run(session, ["eval", "document.documentElement.outerHTML"])
    except OpenCLIError:
        return None


def wait_for_text(session: str, text: str, timeout: float = 5.0) -> bool:
    """Wait until the page contains the given text. Returns True on success."""
    try:
        _run(session, ["wait", "text", text], timeout=int(timeout) + 5)
        return True
    except OpenCLIError:
        return False


def wait_for_selector(session: str, selector: str, timeout: float = 5.0) -> bool:
    """Wait until a CSS selector matches. Returns True on success."""
    try:
        _run(session, ["wait", "selector", selector], timeout=int(timeout) + 5)
        return True
    except OpenCLIError:
        return False


# --- Session lifecycle ---

def close_session(session: str):
    """Release the browser session tab lease."""
    try:
        _run(session, ["close"])
    except OpenCLIError:
        pass
