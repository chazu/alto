#!/usr/bin/env python3
"""Interactive test for Alto using pty + pyte terminal emulator."""

import fcntl, os, pty, select, signal, struct, sys, termios, time
import pyte

COLS, ROWS = 80, 35

def read_all(fd, timeout=2.0):
    result = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.1)
        if ready:
            try:
                data = os.read(fd, 16384)
                if data:
                    result += data
                    deadline = time.time() + 0.3
                else:
                    break
            except OSError:
                break
    return result

def dump(screen):
    lines = []
    for row in range(screen.lines):
        line = ""
        for col in range(screen.columns):
            char = screen.buffer[row][col]
            line += char.data if char.data else " "
        lines.append(line.rstrip())
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    screen = pyte.Screen(COLS, ROWS)
    stream = pyte.Stream(screen)

    child_pid, master_fd = pty.fork()
    if child_pid == 0:
        winsize = struct.pack("HHHH", ROWS, COLS, 0, 0)
        fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, winsize)
        os.environ["TERM"] = "xterm-256color"
        os.execvp("./alto", ["./alto"])
        sys.exit(1)

    print(f"Alto pid={child_pid}")
    try:
        # Initial render
        # Initial output comes in waves — setup escapes, then render
        time.sleep(2.0)
        raw = read_all(master_fd, timeout=5.0)
        print(f"Initial: {len(raw)} bytes")
        stream.feed(raw.decode("utf-8", errors="replace"))
        rendered = dump(screen)
        print("=== INITIAL ===")
        print(rendered)
        print()

        ok_init = "Workspace" in rendered and "Transcript" in rendered
        print(f"Both windows: {ok_init}")
        if not ok_init:
            return

        # Type "Hello"
        print("\nTyping 'Hello'...")
        for ch in b"Hello":
            os.write(master_fd, bytes([ch]))
            time.sleep(0.05)
        time.sleep(1.0)
        raw = read_all(master_fd, timeout=2.0)
        print(f"After typing: {len(raw)} bytes")
        stream.feed(raw.decode("utf-8", errors="replace"))
        rendered = dump(screen)
        print("=== AFTER TYPING ===")
        print(rendered)
        print(f"\n'Hello' visible: {'Hello' in rendered}")

        # Enter
        print("\nSending Enter...")
        os.write(master_fd, b"\r")
        time.sleep(1.0)
        raw = read_all(master_fd, timeout=2.0)
        stream.feed(raw.decode("utf-8", errors="replace"))

        # Type "World"
        print("Typing 'World'...")
        for ch in b"World":
            os.write(master_fd, bytes([ch]))
            time.sleep(0.05)
        time.sleep(1.0)
        raw = read_all(master_fd, timeout=2.0)
        stream.feed(raw.decode("utf-8", errors="replace"))
        rendered = dump(screen)
        print("=== AFTER ENTER + 'World' ===")
        print(rendered)
        print(f"\nBoth lines visible: {'Hello' in rendered and 'World' in rendered}")

        # Quit
        print("\nSending Escape...")
        os.write(master_fd, b"\x1b")
        time.sleep(1.0)

    finally:
        try:
            os.kill(child_pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            os.waitpid(child_pid, os.WNOHANG)
        except ChildProcessError:
            pass
        os.close(master_fd)

if __name__ == "__main__":
    main()
