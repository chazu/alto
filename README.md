# Alto

A terminal UI framework for [Maggie](https://github.com/chazu/maggie), inspired by the Smalltalk-80 programming environment. Alto provides overlapping windows, mouse support, an MVC architecture, and a widget library — all running in your terminal.

Alto can be used in two ways:

1. **As an IDE** — a Smalltalk-80-style programming environment with a System Browser, Workspace, Inspector, Transcript, and Debugger.
2. **As a library** — pull Alto into your own Maggie project to build terminal UIs.

## Quick Start

```sh
mag wrap
mag build --full -o alto
./alto
```

Or use the thin build (no REPL/formatter, smaller binary):

```sh
make thin
./alto-thin
```

## The IDE

Alto ships with a Smalltalk-80-style programming environment. Right-click the desktop (or click empty space) to open tools from the desktop menu.

### Tools

- **Workspace** — scratch pad for evaluating Maggie expressions.
- **System Browser** — four-pane class browser for navigating and editing code. Categories | Classes | Methods | Source.
- **Inspector** — drill-down object viewer. Select a field and press Enter to open a new Inspector on that value.
- **Transcript** — system log. `Transcript show: 'hello'` prints here.
- **Debugger** — three-pane post-mortem debugger with stack frames, source code, and variables. Opens automatically on errors.

### Keyboard Shortcuts

**Workspace:**

| Key | Action |
|-----|--------|
| Ctrl-D | Do it (evaluate selection) |
| Ctrl-R | Print it (evaluate and insert result) |
| Ctrl-O | Inspect it (evaluate and open Inspector) |
| Tab | Autocomplete |
| Escape | Close window |

**Text Editing (Emacs-style):**

| Key | Action |
|-----|--------|
| Ctrl-A | Beginning of line |
| Ctrl-E | End of line |
| Ctrl-K | Kill to end of line |
| Ctrl-Y | Yank (paste) |
| Ctrl-W | Kill region |
| Ctrl-Space | Set/toggle mark |
| Ctrl-G | Cancel mark |
| Ctrl-N | Next line |
| Ctrl-P | Previous line |

**Global:**

| Key | Action |
|-----|--------|
| Ctrl-C | Quit |
| Click desktop | Open desktop menu |
| Drag title bar | Move window |
| Drag corner | Resize window |
| Click [X] | Close window |

## Examples

Alto ships with example apps in the `examples/` directory. Build once, then run any example:

```sh
make build
```

| Example | Command | Description |
|---------|---------|-------------|
| Hello World | `./alto -m Alto::HelloApp.start` | Minimal app — one window, one label |
| Counter | `./alto -m Alto::CounterApp.start` | Interactive counter with styled text and key handling |
| Todo List | `./alto -m Alto::TodoApp.start` | Editable todo list using SplitPane, ListView, TextEditor, and MVC |
| Dashboard | `./alto -m Alto::DashboardApp.start` | Multi-pane layout with nested SplitPanes, status panel, and scrollable log |

Or use Make targets:

```sh
make example-hello
make example-counter
make example-todo
make example-dashboard
```

## Using Alto as a Library

Add Alto as a dependency in your project's `maggie.toml`:

```toml
[dependencies]
alto = { path = "../alto" }
```

Then resolve:

```sh
mag deps resolve
```

### Hello World

```smalltalk
namespace: 'MyApp'
import: 'Alto'

Main subclass: Object
  classMethod: start [
    | app label |
    label := Alto::Label text: 'Hello from Alto!'.
    app := Alto::App new.
    app openWindow: 'Hello' content: label controller: label.
    app run
  ]
```

### Layouts

Use `SplitPane`, `VBox`, and `HBox` to compose views.

**Split pane** — two resizable panes with a draggable divider:

```smalltalk
| sidebar content split app |

sidebar := Alto::ListView items: #('Users' 'Settings' 'Logs')
  onSelect: [:item | Alto::Transcript show: item].
content := Alto::TextEditor new.

split := Alto::SplitPane horizontal: sidebar and: content.
split ratio: 0.25.

app := Alto::App new.
app openWindow: 'Admin' content: split controller: split.
app run.
```

**Vertical stack** with weighted children:

```smalltalk
| box |
box := Alto::VBox new.
box addChild: (Alto::Label text: 'Header').
box addChild: myListView weight: 5.
box addChild: (Alto::Label text: 'Status: Ready').
```

**Horizontal stack:**

```smalltalk
| box |
box := Alto::HBox new.
box addChild: navList weight: 1.
box addChild: mainContent weight: 3.
```

### Styling

Use `Color` and `Style` to customize appearance:

```smalltalk
| style button |
style := (Alto::Style fg: Alto::Color white bg: Alto::Color darkBlue) bold.
button := Alto::Button label: 'Save' action: [Alto::Transcript show: 'Saved'].
button style: style.
```

Named colors: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `darkRed`, `darkGreen`, `darkBlue`, `darkCyan`, `grey`, `darkGrey`, `orange`, `pink`, `purple`.

RGB and hex: `Color rgb: 255 g: 128 b: 0`, `Color hex: 16rFF8000`.

### Widgets

| Widget | Description |
|--------|-------------|
| `Label` | Static text display |
| `Button` | Clickable button with action block |
| `TextEditor` | Multi-line text editor with Emacs keybindings |
| `ListView` | Selectable scrollable list with `onSelect:` callback |
| `Menu` | Popup menu |
| `ScrollBar` | Vertical or horizontal scroll indicator |
| `Divider` | Horizontal or vertical separator line |
| `SplitPane` | Two-pane split with draggable divider |
| `VBox` | Vertical layout container with weighted children |
| `HBox` | Horizontal layout container with weighted children |
| `Window` | Framed window with title bar, close box, resize handle |

### Custom Views

Subclass `View` and override `displayOn:` and `handleEvent:`:

```smalltalk
CounterView subclass: Alto::View
  instanceVars: counter style

  method: initialize [
    super initialize.
    counter := 0.
    style := Go::Terminal newStyle
  ]

  method: displayOn: aCellBuffer [
    aCellBuffer putString: 'Count: ', counter printString x: 0 y: 0 style: style.
    aCellBuffer putString: 'Press Enter to increment' x: 0 y: 1 style: style
  ]

  method: handleEvent: evt [
    (evt at: 'type' ifAbsent: ['']) = 'key' ifFalse: [^self].
    (evt at: 'key') = 13 ifTrue: [
      counter := counter + 1.
      self invalidate
    ]
  ]
```

### MVC

Alto follows the Smalltalk-80 Model-View-Controller pattern:

```smalltalk
"Model notifies dependents on change"
myModel := Alto::Model new.
myModel addDependent: myView.
myModel changed: #data.

"View re-renders when model changes"
method: update: aspect [
  aspect = #data ifTrue: [self invalidate]
]
```

## Architecture

```
+-------------------------------------+
|  Tools (Browser, Inspector,         |  Optional — IDE layer
|  Workspace, Transcript, Debugger)   |
+---------+---------------------------+
|  Widgets (Window, TextEditor, List, |  Composable UI components
|  Menu, Button, ScrollBar, Label,    |
|  SplitPane, VBox, HBox, Divider)    |
+---------+---------------------------+
|  MVC Framework (Model, View)        |  Change notification
+---------+---------------------------+
|  Display + CellBuffer + Color/Style |  Compositor, event loop
+---------+---------------------------+
|  Terminal Primitives (Go/tcell)     |  Screen, input, styles
+-------------------------------------+
```

## Known Limitations

- **Inspector cannot drill into Class objects.** Inspecting a value like `42` works, and drilling into its fields works, but selecting the "class" field and pressing Enter is a no-op. This is caused by a VM-level issue where `isKindOf:` returns `nil` for metaclasses, which cascades into render errors.
- **Ctrl-I is Tab.** Terminals cannot distinguish Ctrl-I from Tab (both send ASCII 9). Inspect-it uses Ctrl-O instead.
- **Debugger stepping is untested.** The Resume, Step Over, Step Into, and Step Out buttons are wired to the VM's `Debugger` class but have not been verified in a live stepping session.
- **No Controller base class.** Views handle events directly rather than through a formal Controller triad. This works in practice but deviates from the Smalltalk-80 MVC spec.
- **No terminal wrapper layer.** Go primitives (`Go::Terminal`, `Go::V2`) are used directly rather than through Maggie wrapper classes.
- **Absolute window positioning.** Windows use fixed coordinates. There is no automatic tiling or cascading.
- **Single-threaded event loop.** Long-running operations in event handlers freeze the UI.

## Profiling

Use Maggie's built-in wall-clock sampling profiler to find performance bottlenecks:

```sh
mag --profile -m Main.start
```

Use the app normally, then quit. A `profile.folded` file appears in the current directory. View it with [speedscope](https://www.speedscope.app/) (drag and drop) or generate a flamegraph:

```sh
# Brendan Gregg's flamegraph.pl
flamegraph.pl profile.folded > profile.svg

# inferno (Rust)
cat profile.folded | inferno-flamegraph > profile.svg
```

Tune the sample rate:

```sh
mag --profile --profile-rate 100 -m Main.start   # less overhead
mag --profile --profile-rate 5000 -m Main.start   # more detail
```

For Go-side profiling (tcell, syscalls, GC):

```sh
mag --profile --pprof -m Main.start
go tool pprof -http=:8080 cpu.pprof
```

## File Structure

```
src/
  Main.mag                  Entry point — launches the IDE
  display/
    App.mag                 Library entry point for custom apps
    CellBuffer.mag          2D cell grid with drawing operations
    Color.mag               Color constants, RGB/hex, Style builder
    Display.mag             Global compositor and event loop
    Rectangle.mag           Geometry
  mvc/
    Model.mag               Change/update notification
    View.mag                Base view with buffer and invalidation
  widgets/
    Window.mag              Framed window with title bar
    TextEditor.mag          Multi-line text editor
    ListView.mag            Selectable list
    Menu.mag                Popup menu
    Button.mag              Clickable button
    ScrollBar.mag           Scroll indicator
    Label.mag               Static text
    Divider.mag             Separator line
    SplitPane.mag           Two-pane split view
    VBox.mag                Vertical layout
    HBox.mag                Horizontal layout
  tools/
    SystemBrowser.mag       Four-pane class browser
    Workspace.mag           Do-it scratch pad
    Inspector.mag           Object viewer with drill-down
    Transcript.mag          System log
    Debugger.mag            Post-mortem debugger
```

## License

MIT
