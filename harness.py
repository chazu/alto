"""
tui_harness.py — PTY-based TUI test harness
Drives any terminal process (tcell, ncurses, etc.) via a real PTY,
parses rendered output with a VT100 emulator, and provides helpers
for input, assertions, and screen snapshots.

Dependencies:
    pip install pexpect pyte

Usage:
    from tui_harness import TUIHarness

    with TUIHarness("./my-tui", cols=120, rows=40) as tui:
        tui.wait_for("Welcome")
        tui.send_key("j")
        tui.send_key("ENTER")
        tui.assert_contains("Selected item")
        tui.snapshot("after_select.txt")
"""

import time
import pexpect
import pyte
from typing import Optional


# --- Named key sequences (tcell-friendly) ---
KEYS = {
    "ENTER":     "\r",
    "ESC":       "\x1b",
    "TAB":       "\t",
    "BACKSPACE": "\x7f",
    "UP":        "\x1b[A",
    "DOWN":      "\x1b[B",
    "RIGHT":     "\x1b[C",
    "LEFT":      "\x1b[D",
    "HOME":      "\x1b[H",
    "END":       "\x1b[F",
    "PGUP":      "\x1b[5~",
    "PGDN":      "\x1b[6~",
    "F1":        "\x1bOP",
    "F2":        "\x1bOQ",
    "F3":        "\x1bOR",
    "F4":        "\x1bOS",
    "CTRL_C":    "\x03",
    "CTRL_D":    "\x04",
    "CTRL_L":    "\x0c",
    "CTRL_Z":    "\x1a",
}


class TUIHarness:
    """
    Context manager that spawns a TUI process in a PTY, maintains a
    pyte VT100 screen model, and exposes test helpers.

    Args:
        cmd:        Command string or list to launch the TUI binary.
        cols:       Terminal width  (default 120).
        rows:       Terminal height (default 40).
        timeout:    Default wait timeout in seconds (default 5).
        encoding:   Terminal encoding (default utf-8).
        env:        Optional dict of environment variables to pass.
    """

    def __init__(
        self,
        cmd: str | list,
        cols: int = 120,
        rows: int = 40,
        timeout: float = 5.0,
        encoding: str = "utf-8",
        env: Optional[dict] = None,
    ):
        self.cmd = cmd if isinstance(cmd, str) else " ".join(cmd)
        self.cols = cols
        self.rows = rows
        self.timeout = timeout
        self.encoding = encoding
        self.env = env

        self._screen = pyte.Screen(cols, rows)
        self._stream = pyte.ByteStream(self._screen)
        self._proc: Optional[pexpect.spawn] = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        """Spawn the TUI process in a PTY."""
        self._proc = pexpect.spawn(
            self.cmd,
            dimensions=(self.rows, self.cols),
            timeout=self.timeout,
            encoding=None,  # raw bytes — we decode through pyte
            env=self.env,
        )

    def stop(self):
        """Terminate the TUI process."""
        if self._proc and self._proc.isalive():
            self._proc.sendcontrol("c")
            try:
                self._proc.expect(pexpect.EOF, timeout=2)
            except Exception:
                self._proc.terminate(force=True)

    # ------------------------------------------------------------------
    # Screen sync
    # ------------------------------------------------------------------

    def _drain(self, settle: float = 0.05):
        """
        Read all available output from the PTY into the pyte screen.
        Waits `settle` seconds for the TUI to finish rendering.
        """
        time.sleep(settle)
        while True:
            try:
                chunk = self._proc.read_nonblocking(size=4096, timeout=0.1)
                self._stream.feed(chunk)
            except (pexpect.TIMEOUT, pexpect.EOF):
                break

    def screen_text(self) -> list[str]:
        """Return the current screen as a list of row strings."""
        self._drain()
        return [self._screen.buffer[y] for y in range(self._screen.lines)]

    def screen_str(self) -> str:
        """Return the full rendered screen as a single string."""
        rows = self.screen_text()
        lines = []
        for row in rows:
            line = "".join(char.data for char in (row[x] for x in range(self._screen.columns)))
            lines.append(line.rstrip())
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def send(self, text: str):
        """Send raw text to the TUI."""
        self._proc.send(text.encode(self.encoding))

    def send_key(self, key: str):
        """
        Send a named key (e.g. 'ENTER', 'UP', 'CTRL_C') or a literal
        character. Named keys are resolved via the KEYS table above.
        """
        seq = KEYS.get(key.upper(), key)
        self._proc.send(seq.encode(self.encoding))

    def send_keys(self, *keys: str, delay: float = 0.05):
        """Send multiple keys with a small delay between each."""
        for key in keys:
            self.send_key(key)
            time.sleep(delay)

    def type_text(self, text: str, delay: float = 0.03):
        """Type a string character by character."""
        for ch in text:
            self.send(ch)
            time.sleep(delay)

    # ------------------------------------------------------------------
    # Waiting
    # ------------------------------------------------------------------

    def wait_for(self, text: str, timeout: Optional[float] = None, poll: float = 0.1):
        """
        Block until `text` appears anywhere on the rendered screen.
        Raises TimeoutError if it doesn't appear within `timeout` seconds.
        """
        deadline = time.monotonic() + (timeout or self.timeout)
        while time.monotonic() < deadline:
            if text in self.screen_str():
                return
            time.sleep(poll)
        raise TimeoutError(
            f"Timed out waiting for {text!r}\n\nCurrent screen:\n{self.screen_str()}"
        )

    def wait_for_stable(self, settle: float = 0.3, polls: int = 3, poll_interval: float = 0.1):
        """
        Wait until the screen stops changing (useful after animations or
        loading spinners).
        """
        prev = None
        stable = 0
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            current = self.screen_str()
            if current == prev:
                stable += 1
                if stable >= polls:
                    return
            else:
                stable = 0
                prev = current
            time.sleep(poll_interval)

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def assert_contains(self, text: str, msg: str = ""):
        """Assert that `text` appears somewhere on the current screen."""
        screen = self.screen_str()
        if text not in screen:
            raise AssertionError(
                f"Expected {text!r} on screen. {msg}\n\nCurrent screen:\n{screen}"
            )

    def assert_not_contains(self, text: str, msg: str = ""):
        """Assert that `text` does NOT appear on the current screen."""
        screen = self.screen_str()
        if text in screen:
            raise AssertionError(
                f"Expected {text!r} to be absent. {msg}\n\nCurrent screen:\n{screen}"
            )

    def assert_at(self, row: int, col: int, text: str):
        """
        Assert that `text` starts at a specific (row, col) position.
        Both row and col are 0-indexed.
        """
        self._drain()
        for i, ch in enumerate(text):
            cell = self._screen.buffer[row][col + i]
            if cell.data != ch:
                raise AssertionError(
                    f"Expected {text!r} at ({row},{col}), "
                    f"got {cell.data!r} at offset {i}.\n\nCurrent screen:\n{self.screen_str()}"
                )

    def assert_cursor_at(self, row: int, col: int):
        """Assert the cursor is at (row, col) (0-indexed)."""
        self._drain()
        actual = (self._screen.cursor.y, self._screen.cursor.x)
        if actual != (row, col):
            raise AssertionError(f"Cursor at {actual}, expected ({row}, {col})")

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    def snapshot(self, path: str):
        """Save the current rendered screen to a text file."""
        content = self.screen_str()
        with open(path, "w", encoding=self.encoding) as f:
            f.write(content)
        print(f"[snapshot] → {path}")
        return content

    def diff_snapshot(self, path: str) -> Optional[str]:
        """
        Compare the current screen to a saved snapshot.
        Returns None if identical, or a unified diff string if different.
        """
        import difflib, os
        current = self.screen_str().splitlines(keepends=True)
        if not os.path.exists(path):
            self.snapshot(path)
            print(f"[snapshot] created baseline: {path}")
            return None
        with open(path, encoding=self.encoding) as f:
            baseline = f.read().splitlines(keepends=True)
        diff = list(difflib.unified_diff(baseline, current, fromfile=path, tofile="current"))
        return "".join(diff) if diff else None


# ------------------------------------------------------------------
# Example / smoke test — replace cmd with your actual binary
# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "python3 -m curses_demo"

    print(f"Launching: {cmd}\n")
    with TUIHarness(cmd, cols=120, rows=40, timeout=8) as tui:
        # Give the TUI a moment to draw its initial frame
        tui.wait_for_stable()

        print("=== Initial screen ===")
        print(tui.screen_str())
        print()

        tui.snapshot("/tmp/tui_initial.txt")

        # Example interactions — adapt these to your TUI:
        # tui.wait_for("some prompt")
        # tui.send_key("DOWN")
        # tui.send_key("ENTER")
        # tui.assert_contains("expected text")
        # diff = tui.diff_snapshot("/tmp/tui_after_select.txt")
        # if diff:
        #     print("Screen changed from baseline:\n", diff)
