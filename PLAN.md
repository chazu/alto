# Alto — TUI Framework for Maggie

A terminal UI framework built on tcell, following the Smalltalk-80 MVC architecture.
Character-cell based display with overlapping windows, mouse support, and the classic
ST-80 tool suite (browser, inspector, workspace, transcript).

## Architecture

```
┌─────────────────────────────────────┐
│  ST-80 Tools (Browser, Inspector,   │  Maggie
│  Workspace, Transcript, Debugger)   │
├─────────────────────────────────────┤
│  Widgets (Window, TextEditor, List, │  Maggie
│  Menu, ScrollBar, Label, Button)    │
├─────────────────────────────────────┤
│  MVC Framework (Model, View,        │  Maggie
│  Controller, Display compositor)    │
├─────────────────────────────────────┤
│  Cell Buffer & Compositor           │  Maggie
│  (CellBuffer, blit, clip, styles)   │
├─────────────────────────────────────┤
│  Terminal Primitives                │  Go (VM primitives)
│  (tcell Screen, Events, Colors)     │
└─────────────────────────────────────┘
```

## Phase 1: Terminal Primitives (Go)

Add Go primitives to the Maggie VM wrapping tcell. These are registered in the VM
as primitive methods on Maggie classes.

### Terminal class
```
Terminal new           → init tcell screen, enter raw mode
Terminal close         → restore terminal
Terminal size          → Point (width @ height)
Terminal sync          → full redraw
Terminal show          → flush changes (diff-based)
Terminal pollEvent     → blocks, returns Event subclass
Terminal pollEventTimeout: ms → returns Event or nil
Terminal clear
Terminal putChar: ch x: x y: y
Terminal putString: str x: x y: y
Terminal setStyle: style x: x y: y  → set fg/bg/attrs at cell
```

### Event hierarchy
```
Event
  KeyEvent        → key, rune, modifiers
  MouseEvent      → x, y, button, modifiers
  ResizeEvent     → width, height
```

### Style / Color
```
Style fg: color bg: color attrs: attrs
Color black, red, green, yellow, blue, magenta, cyan, white
Color rgb: r g: g b: b    → true color
```

**Deliverable:** A Maggie program can init a terminal, draw text, read key/mouse
events, and exit cleanly. ~300-400 lines of Go.

## Phase 2: CellBuffer & Compositor (Maggie)

### CellBuffer
A 2D array of cells (char + style). The fundamental drawing surface.
```
buf := CellBuffer width: 80 height: 24.
buf putChar: $A x: 5 y: 3 style: aStyle.
buf putString: 'Hello' x: 10 y: 5 style: aStyle.
buf drawBox: (0@0 extent: 20@10) style: aStyle.        → box-drawing chars
buf blit: targetBuf at: destPoint clip: clipRect.       → compositing
buf clear.
buf clearRect: aRect.
```

### Compositor (Display)
Manages the global screen buffer and window z-order.
```
Display current
Display addWindow: aWindow
Display removeWindow: aWindow
Display bringToFront: aWindow
Display invalidate: aRect         → mark region for redraw
Display render                    → composite all windows, flush to terminal
```

Rendering: iterate windows back-to-front, blit each window's buffer onto
the screen buffer clipped to the window's frame. Then flush to terminal.

**Deliverable:** Windows can be drawn on screen with proper z-ordering and clipping.

## Phase 3: MVC Framework (Maggie)

### Model
```
Model subclass: Object
  method: changed               → notify all dependents
  method: changed: aspect       → notify with aspect symbol
  method: addDependent: obj
  method: removeDependent: obj
```

### View
```
View subclass: Object
  instanceVars: model bounds buffer
  method: model: aModel         → register as dependent
  method: displayOn: aCellBuffer → subclasses override to render
  method: invalidate             → mark for redraw
  method: update: aspect         → called when model changes
  method: bounds                 → Rectangle
```

### Controller
```
Controller subclass: Object
  instanceVars: model view
  method: handleEvent: anEvent   → process input
  method: isActive               → has focus?
  method: wantsEvent: anEvent    → can handle this event?
```

**Deliverable:** A working MVC triad — model changes trigger view updates,
controllers dispatch input.

## Phase 4: Widgets (Maggie)

### Window
Frame with title bar (drag to move), close box, resize handle.
Contains a content view/controller pair.
```
Window new title: 'Browser' content: aBrowserView.
Window open.
Window close.
Window moveTo: aPoint.
Window resize: anExtent.
```

### TextEditor
Scrollable, editable text with cursor and selection.
```
TextEditor new text: 'hello world'.
TextEditor selection.
TextEditor insert: 'foo'.
TextEditor doIt.              → evaluate selected text (for Workspace)
TextEditor printIt.           → evaluate and show result
```

### ListView
Selectable list with scroll.
```
ListView new items: #('one' 'two' 'three') onSelect: [:item | ...].
```

### Menu
Popup menu triggered by mouse.
```
Menu new items: #('Do It' 'Print It' 'Inspect') action: [:sel | ...].
```

### Other: Label, Button, ScrollBar, Divider

**Deliverable:** Reusable widget library sufficient to build the ST-80 tools.

## Phase 5: ST-80 Tools (Maggie)

### SystemBrowser
4-pane class browser: categories | classes | protocols | methods + code editor.
Reads from the Maggie image/source.

### Workspace
Scratch pad with do-it (Cmd-D), print-it (Cmd-P), inspect-it (Cmd-I).

### Inspector
Shows an object's instance variables and their values. Drill-down navigation.

### Transcript
System log / output stream. Read-only scrolling text.

### Debugger
Stack frame list + code view + variable inspector. Step/proceed/restart.

## File Structure

```
src/
  Main.mag                    → entry point, launches Display
  terminal/
    Terminal.mag              → Maggie wrapper for Go primitives
    Event.mag                 → Event, KeyEvent, MouseEvent, ResizeEvent
    Color.mag                 → Color, Style
  display/
    CellBuffer.mag            → 2D cell array with drawing ops
    Display.mag               → global compositor, event loop
    Rectangle.mag             → geometry
    Point.mag                 → geometry (may already exist in Maggie)
  mvc/
    Model.mag                 → change/update protocol
    View.mag                  → base view
    Controller.mag            → base controller
  widgets/
    Window.mag                → framed window with title bar
    TextEditor.mag            → editable text
    ListView.mag              → selectable list
    Menu.mag                  → popup menu
    Label.mag                 → static text
    Button.mag                → clickable button
    ScrollBar.mag             → scroll indicator
  tools/
    SystemBrowser.mag         → 4-pane class browser
    Workspace.mag             → do-it scratch pad
    Inspector.mag             → object viewer
    Transcript.mag            → system log
```

## Implementation Order

1. Terminal primitives (Go) — must be done in the Maggie VM repo
2. CellBuffer + basic rendering — can verify with a simple demo
3. MVC framework — Model/View/Controller base classes
4. Window + Display compositor — overlapping windows working
5. TextEditor + ListView — the two critical widgets
6. Menu — popup menus
7. SystemBrowser — the flagship tool, proves the framework
8. Workspace + Inspector + Transcript — remaining tools

## Design Principles

- **Faithful to ST-80 MVC** — triadic Model/View/Controller, not merged widgets
- **Cell-based BitBlt** — compositing via cell buffer blitting with clip rects
- **Mouse-driven** — click to focus, drag to move/resize, right-click for menus
- **Keyboard shortcuts** — Cmd-D do-it, Cmd-P print-it, Cmd-I inspect-it
- **Live system** — changes take effect immediately, no compile step
- **Minimal Go surface** — only terminal I/O in Go, everything else in Maggie
