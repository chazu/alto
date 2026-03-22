# Alto

A Smalltalk-inspired desktop environment built on the Maggie VM with tcell for terminal rendering.

## Prerequisites

- Go 1.21+
- [Maggie](https://github.com/chazu/maggie) (`mag` CLI on your PATH)

## Running

```bash
mag -m Main.start
```

This loads the project from `maggie.toml`, compiles sources, and starts the Alto desktop.

## Project Structure

```
src/
  Main.mag              # Entry point
  display/              # Terminal display, cell buffer, rectangle math
  mvc/                  # Model-View-Controller framework
  tools/                # Transcript, Workspace, Inspector, SystemBrowser
  widgets/              # Window, Label, ListView
wrap/
  tcell/                # Go-wrapped tcell bindings
  terminal/             # Go-wrapped terminal helpers
```

## Profiling

When tracking down performance issues (slow redraws, laggy input, etc.), use Maggie's built-in wall-clock sampling profiler.

### Quick Start

```bash
# Profile the app at 1000 Hz, write folded-stack output on exit
mag --profile -m Main.start
```

Use the app normally, then quit. A `profile.folded` file appears in the current directory.

### Viewing Results

The easiest option is [speedscope](https://www.speedscope.app/) -- just drag and drop `profile.folded` into the browser. Alternatively:

```bash
# Using Brendan Gregg's flamegraph.pl
flamegraph.pl profile.folded > profile.svg
open profile.svg

# Using inferno (Rust, installable via cargo)
cat profile.folded | inferno-flamegraph > profile.svg
```

### Tuning the Profiler

```bash
# Lower sample rate (less overhead, coarser data)
mag --profile --profile-rate 100 -m Main.start

# Higher sample rate (more detail, slightly more overhead)
mag --profile --profile-rate 5000 -m Main.start

# Custom output file
mag --profile --profile-output alto-profile.folded -m Main.start
```

### Profiling from Maggie Code

You can start/stop the profiler programmatically, useful for profiling specific sections:

```smalltalk
"Profile just the redraw loop"
Compiler startProfiling.
display redrawAll.
result := Compiler stopProfiling.
"result is a String in folded-stack format"
```

### Go-Level Profiling

To also capture Go-side CPU time (tcell rendering, syscalls, GC):

```bash
mag --profile --pprof -m Main.start
```

This produces both `profile.folded` (Maggie stacks) and `cpu.pprof` (Go stacks). View the Go profile with:

```bash
go tool pprof -http=:8080 cpu.pprof
```

### Reading Flamegraphs

In the flamegraph:

- **Wide bars** = methods where the most wall-clock time is spent
- `ClassName>>methodName` = Maggie method calls
- `[block in ClassName>>methodName]` = block evaluations
- `[primitive selectorName]` = time in Go primitive implementations (tcell calls, string ops, etc.)

Look for wide `[primitive ...]` bars to find Go interop bottlenecks, and wide Maggie method bars to find algorithmic issues in your Smalltalk code.
