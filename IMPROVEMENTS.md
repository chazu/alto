# Alto — Improvement Plan

Findings from a Smalltalk-expert audit of the codebase, prioritized by impact.

## Priority 1: Quick Wins (Small effort, high impact)

### ~~1.1 Delete duplicate ListView / ListWidget~~ DONE
Deleted ListWidget.mag (~260 lines removed), updated Inspector to use ListView.

### ~~1.2 Cache Theme styles in class variables~~ DONE
Styles cached in class vars with lazy initialization + resetCache method.

### ~~1.3 Replace linear class lookup with Dictionary~~ DONE
SystemBrowser uses Dictionary for classObjects. Debugger uses lazy-built classLookup Dictionary.

### ~~1.4 Fix reversed left/right arrow keys in Debugger~~ DONE
Swapped keyLeft/keyRight handlers.

### ~~1.5 Update counter example to use EventConstants~~ DONE
Key codes replaced with EventConstants keyUp/keyDown.

---

## Priority 2: Architectural Improvements (Medium effort, high impact)

### 2.1 Create Event object hierarchy
**File:** `src/Display.mag` (lines ~138-158), plus 12+ handler sites across codebase
**Problem:** Events are raw Dictionaries with string keys (`'type'`, `'key'`, `'rune'`, `'mod'`, `'buttons'`, `'x'`, `'y'`). Every handler must destructure: `(evt at: 'type' ifAbsent: ['']) = 'mouse'`. This is fragile (typo-prone), non-polymorphic, and violates Smalltalk's core principle that everything is an object.
**Fix:** Create `KeyEvent`, `MouseEvent`, `ResizeEvent` classes with proper accessors and a polymorphic `dispatchTo:` method. Replace dictionary unpacking with `evt dispatchTo: self` → calls `handleKeyEvent:` / `handleMouseEvent:`.
**Effort:** Medium — touches many files, but each change is mechanical.

### 2.2 Decompose Display>>run and Display>>dispatchMouse:
**File:** `src/Display.mag`
**Problem:** `run` is ~63 lines handling event polling, type discrimination, dictionary construction, resize handling, error recovery, and rendering. `dispatchMouse:` is ~83 lines handling drag, resize, menu dismissal, hit-testing, and desktop menus. Smalltalk methods should be 5-7 lines.
**Fix:** Extract: `handleResize:`, `buildEventFrom:`, `dispatchEvent:`, `renderWithErrorRecovery` from `run`. Extract: `handleResizeDrag:`, `handleWindowDrag:`, `dismissMenuIfNeeded:`, `windowHitTest:`, `handleDesktopClick:` from `dispatchMouse:`. Consider extracting drag/resize state into a `WindowDragHandler`.
**Effort:** Medium — pure refactoring, no behavior change.

### 2.3 Fix O(n²) string building
**Files:** `src/widgets/TextEditor.mag` (line ~56-77), `src/tools/AltoDebugger.mag` (line ~191-208), `src/tools/Inspector.mag` (line ~304-328)
**Problem:** Strings built via `current := current, (Character value: code) asString` in loops — creates N intermediate string objects for N characters. Same issue with `result := result copyWith: item` for arrays.
**Fix:** Introduce a `WriteStream` / `StringBuffer` equivalent, or at minimum a `String join:with:` utility. For arrays, use a growable collection.
**Effort:** Medium — depends on what Maggie's runtime supports.

---

## Priority 3: Design Debt (Lower urgency, valuable long-term)

### 3.1 Document or implement the Controller separation
**Files:** `src/mvc/`, all tools in `src/tools/`
**Problem:** PLAN.md describes MVC with a separate Controller class, but in practice View and Controller are merged — tools like `SystemBrowser` subclass `View` but handle all events themselves. `Window>>handleEvent:` delegates to `contentController`, but it's usually the same object as `contentView`.
**Fix:** Either: (a) document the intentional merge as a design decision, or (b) extract keyboard/mouse handling into Controller subclasses for proper MVC.
**Effort:** Large if implementing, small if just documenting.

### 3.2 Standardize new/initialize protocol
**Problem:** Three different patterns coexist: (1) override `new` to call custom init (e.g., `initDisplay`, `initDefaults`), (2) override `new` to call `initialize`, (3) factory class methods. Risk of double-initialization when subclasses chain `new`.
**Fix:** Standardize on `initialize` called by `new`. Remove custom `new` overrides. Rename `initDisplay`/`initDefaults` to `initialize`.
**Effort:** Medium — touches many classes but each change is small.

### 3.3 Replace hardcoded layout dimensions with named methods
**Files:** `src/tools/SystemBrowser.mag`, `src/tools/Inspector.mag`, `src/tools/AltoDebugger.mag`
**Problem:** Magic numbers for pane sizes: `paneHeight := 10`, `paneWidth := 26`, `listWidth := 22`, `leftW := 35`. SystemBrowser computes pane width differently in `displayOn:` vs `handleMouseLocalX:y:`, causing click-target/visual mismatches.
**Fix:** Extract to named methods (`listPaneWidth`, `framePaneHeight`) or compute from available space.
**Effort:** Medium.

### ~~3.4 Add = and hash to Rectangle and Style~~ DONE
Rectangle has = and hash. Style has standard = (keeps equals: as alias). Display updated to use =.

### 3.5 Clarify App vs Display responsibilities
**Problem:** `App` is a thin forwarding wrapper. `Display` owns desktop menu logic, error handling, and the event loop. The boundary is unclear.
**Fix:** Either have `App` absorb Display's higher-level responsibilities, or remove `App` as unnecessary indirection.
**Effort:** Medium.
