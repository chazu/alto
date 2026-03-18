#!/usr/bin/env python3
"""Minimal test — just capture raw output from Alto."""

import fcntl, os, pty, select, struct, sys, termios, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

child_pid, master_fd = pty.fork()

if child_pid == 0:
    winsize = struct.pack("HHHH", 35, 80, 0, 0)
    fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, winsize)
    os.environ["TERM"] = "xterm-256color"
    os.execvp("./alto", ["./alto"])
    sys.exit(1)

# Parent — read for 5 seconds
print(f"pid={child_pid}")
deadline = time.time() + 5.0
raw = b""
while time.time() < deadline:
    ready, _, _ = select.select([master_fd], [], [], 0.1)
    if ready:
        try:
            data = os.read(master_fd, 4096)
            if data:
                raw += data
            else:
                break
        except OSError:
            break

print(f"Got {len(raw)} bytes")
print("=== RAW (repr, first 500) ===")
print(repr(raw[:500]))
print()
print("=== RAW (decoded, first 500) ===")
print(raw[:500].decode("utf-8", errors="replace"))

# Kill
os.write(master_fd, b"\x1b")
time.sleep(0.5)
try:
    os.kill(child_pid, 9)
    os.waitpid(child_pid, 0)
except:
    pass
os.close(master_fd)
