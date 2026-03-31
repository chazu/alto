# Epic: Alto Codebase Quality Improvements

Based on the Smalltalk PL Expert review of 2026-03-30.

## Task 1: Extract EventConstants class

**Priority:** Tier 1 — highest leverage
**Dependencies:** None
**Estimated scope:** New file + edits to ~12 files

### Description

Create `src/EventConstants.mag` — a class with class methods returning named constants for all magic key codes and modifier masks used throughout the codebase.

### Constants to define

From the codebase audit, these magic numbers appear across 12+ files:

**Key codes:**
- `keyTab` → 9
- `keyEnter` → 13
- `keyEscape` → 27
- `keyBackspace` → 8
- `keyDelete` → 127
- `keySpace` → 32
- `keyUp` → 257
- `keyDown` → 258
- `keyRight` → 259
- `keyLeft` → 260
- `keyRune` → 256

**Event type sentinels (from Display.mag):**
- `eventMouse` → -2
- `eventResize` → -3

**Modifier masks:**
- `modCtrl` → 2

**Ctrl key helpers (the letter's ASCII code, used with mod check):**
- `ctrlA` → 65, `ctrlC` → 67, `ctrlD` → 68, `ctrlE` → 69, `ctrlG` → 71
- `ctrlK` → 75, `ctrlN` → 78, `ctrlO` → 79, `ctrlP` → 80, `ctrlR` → 82
- `ctrlS` → 83, `ctrlW` → 87, `ctrlY` → 89

**Helper methods:**
- `isCtrl: mod` → `(mod bitAnd: 2) > 0` — replaces the raw bitAnd pattern

### Files to update

Replace magic numbers with EventConstants calls in:
- `src/widgets/TextEditor.mag` (lines 79–232 — handleKey:rune:mod:)
- `src/widgets/Menu.mag` (handleEvent:)
- `src/widgets/Button.mag` (handleEvent:)
- `src/widgets/ListView.mag` (handleEvent:)
- `src/widgets/HBox.mag` (handleEvent:)
- `src/widgets/VBox.mag` (handleEvent:)
- `src/widgets/SplitPane.mag` (handleEvent:)
- `src/widgets/Window.mag` (handleEvent:)
- `src/tools/SystemBrowser.mag` (handleEvent:, handleCodeKey:rune:mod:)
- `src/tools/Workspace.mag` (handleEvent:)
- `src/tools/Inspector.mag` (handleEvent:)
- `src/tools/Debugger.mag` (handleEvent:)
- `src/display/Display.mag` (run method, lines 139, 149)

### Verification

- `mag build` compiles
- All existing tests pass (`mag test`)
- Grep for raw key code numbers — should only appear in EventConstants.mag

---

## Task 2: Unify HBox/VBox into BoxLayout

**Priority:** Tier 1
**Dependencies:** Task 1 (EventConstants — both files reference key code 9 for Tab)
**Estimated scope:** 1 new file, 2 deleted files, edits to all files referencing HBox/VBox

### Description

`src/widgets/HBox.mag` (153 lines) and `src/widgets/VBox.mag` (154 lines) are 95% identical — same instanceVars (`children weights focusedIndex childBufs`), same methods. The only difference is the axis: HBox divides width, VBox divides height.

Create `src/widgets/BoxLayout.mag` with an `orientation` instance variable (`:horizontal` or `:vertical`). All layout math uses orientation to pick the axis.

### Implementation

```
BoxLayout subclass: View
  instanceVars: children weights focusedIndex childBufs orientation
```

- Constructor: `BoxLayout horizontal` / `BoxLayout vertical`
- In `displayOn:`, use orientation to decide whether to divide `buf width` or `buf height`
- In `handleEvent:`, Tab cycling logic is identical
- In `handleMouseLocalX:y:buttons:`, hit testing checks the appropriate axis

### Compatibility

Add class aliases or factory methods so existing code doesn't break:
- `HBox new` → `BoxLayout horizontal`
- `VBox new` → `BoxLayout vertical`

### Files to update

- Delete `src/widgets/HBox.mag` and `src/widgets/VBox.mag`
- Create `src/widgets/BoxLayout.mag`
- Update all references: grep for `HBox` and `VBox` across the codebase (Main.mag, examples, tests, tools)
- Update `maggie.toml` if source dirs need adjustment

### Verification

- `mag build` compiles
- All existing tests pass
- Examples using HBox/VBox still render correctly

---

## Task 3: Extract Theme class

**Priority:** Tier 1
**Dependencies:** None
**Estimated scope:** 1 new file + edits to ~15 files

### Description

`Go::Terminal newStyle` appears 30+ times. Every widget independently creates `normalStyle` and `reverseStyle` in its `initialize` method, producing identical styles. Extract a `Theme` singleton that provides standard named styles.

### Implementation

Create `src/display/Theme.mag`:

```
Theme subclass: Object

  classMethod: normalStyle    → Go::Terminal newStyle
  classMethod: reverseStyle   → Go::Terminal newStyle reverse: true
  classMethod: selectedStyle  → (same as reverseStyle)
  classMethod: dimStyle       → Go::Terminal newStyle dim: true
  classMethod: boldStyle      → Go::Terminal newStyle bold: true
  classMethod: borderStyle    → Go::Terminal newStyle
  classMethod: dividerStyle   → Go::Terminal newStyle dim: true
```

### Files to update

Replace `Go::Terminal newStyle` + method chains with `Theme` calls in:
- `src/widgets/TextEditor.mag` (lines 22–23)
- `src/widgets/Menu.mag` (lines 49–50)
- `src/widgets/Button.mag` (lines 41–42)
- `src/widgets/ListView.mag` (lines 21–22)
- `src/widgets/ScrollBar.mag` (lines 53–54)
- `src/widgets/SplitPane.mag` (line 54)
- `src/widgets/Divider.mag` (line 52)
- `src/widgets/Window.mag` (lines 28, 38)
- `src/tools/SystemBrowser.mag` (lines 39–40)
- `src/tools/Inspector.mag` (lines 50–52)
- `src/tools/Debugger.mag` (lines 87–89)
- `src/tools/Transcript.mag` (line 42)
- `src/display/CellBuffer.mag` (line 21)
- `src/display/Display.mag` (lines 49, 291)

Remove the `normalStyle` and `reverseStyle` instance variables where they just cache `Go::Terminal newStyle` / `newStyle reverse: true`.

### Verification

- `mag build` compiles
- All existing tests pass
- Visual appearance unchanged (styles produce same tcell values)

---

## Task 4: Fix SystemBrowser codeDirty bug

**Priority:** Tier 1
**Dependencies:** None
**Estimated scope:** 1 file, ~3 lines

### Description

`src/tools/SystemBrowser.mag` line 204 assigns `codeDirty := false`, but `codeDirty` is not declared in the `instanceVars:` list (line 5). This is either:
- A missing ivar that should be added, or
- A stale reference that should use `codeEditor isDirty` instead

### Investigation steps

1. Read SystemBrowser.mag fully
2. Search for all references to `codeDirty` in the file
3. Check if `codeEditor` has an `isDirty` / `dirty:` protocol
4. Read TextEditor.mag to understand the dirty tracking API

### Likely fix

If TextEditor has `isDirty` / `dirty:`, replace `codeDirty := false` with `codeEditor dirty: false`. If not, add `codeDirty` to instanceVars and ensure it's initialized in `initialize`.

### Verification

- `mag build` compiles
- `mag test` passes (especially test_system_browser.mag)

---

## Task 5: Fix Workspace autocomplete cursor bug

**Priority:** Tier 1
**Dependencies:** None
**Estimated scope:** 1 file, ~5 lines

### Description

`src/tools/Workspace.mag` method `insertCompletion:prefix:` (lines 278–285) inserts a completion but does not update the cursor position afterward. The cursor stays at the old X position, now in the middle of the completed word.

### Current code (lines 278–285)

```
method: insertCompletion: completion prefix: prefix [
  | lineStr beforePrefix afterCursor |
  lineStr := editor lines at: editor cursorY.
  beforePrefix := lineStr copyFrom: 0 to: editor cursorX - prefix size.
  afterCursor := lineStr copyFrom: editor cursorX.
  editor lines at: editor cursorY put: (beforePrefix, completion, afterCursor).
  self invalidate
]
```

### Fix

After the line replacement, add:
```
editor cursorX: beforePrefix size + completion size.
```

Also check if the editor needs `dirty: true` or if `invalidate` is sufficient. Check TextEditor's API for cursor setters (`cursorX:` method).

### Verification

- `mag build` compiles
- Manual test: open workspace, type partial word, trigger completion, verify cursor is after the completed word

---

## Task 6: Factor TextEditor handleKey into KeyMap

**Priority:** Tier 2
**Dependencies:** Task 1 (EventConstants must exist first)
**Estimated scope:** 1 file major refactor

### Description

`src/widgets/TextEditor.mag` method `handleKey:rune:mod:` (lines 79–232) is a 154-line if-chain dispatching key codes to inline editing logic. Factor this into:

1. A `keyMap` Dictionary mapping key bindings to method selectors (or blocks)
2. Small, focused methods for each editing action

### Target structure

```
method: initializeKeyMap [
  keyMap := Dictionary new.
  keyMap at: 'ctrl-space' put: [self toggleMark].
  keyMap at: 'ctrl-g'     put: [self cancelMark].
  keyMap at: 'ctrl-w'     put: [self killRegion].
  keyMap at: 'ctrl-a'     put: [self beginningOfLine].
  keyMap at: 'ctrl-e'     put: [self endOfLine].
  keyMap at: 'ctrl-k'     put: [self killLine].
  keyMap at: 'ctrl-y'     put: [self yank].
  keyMap at: 'ctrl-n'     put: [self nextLine].
  keyMap at: 'ctrl-p'     put: [self previousLine].
  keyMap at: 'enter'      put: [self splitLine].
  keyMap at: 'backspace'  put: [self deleteBack].
  keyMap at: 'up'         put: [self moveCursorUp].
  keyMap at: 'down'       put: [self moveCursorDown].
  keyMap at: 'left'       put: [self moveCursorLeft].
  keyMap at: 'right'      put: [self moveCursorRight].
]
```

### Extracted methods to create

Each should be 5–15 lines, extracted from the current inline logic:
- `toggleMark`, `cancelMark`
- `killRegion`, `killLine`, `yank`
- `beginningOfLine`, `endOfLine`
- `nextLine`, `previousLine`
- `splitLine`, `deleteBack`
- `moveCursorUp`, `moveCursorDown`, `moveCursorLeft`, `moveCursorRight`
- `insertChar:` (for printable characters)

### Key lookup logic

```
method: handleKey: keyCode rune: runeVal mod: mod [
  | key action |
  key := self keyNameFor: keyCode rune: runeVal mod: mod.
  action := keyMap at: key ifAbsent: [nil].
  action notNil ifTrue: [action value. dirty := true. self invalidate. ^true].
  "Printable character fallback"
  keyCode = EventConstants keyRune ifTrue: [self insertChar: runeVal. ^true].
  ^false
]
```

Note: Since Maggie may not support `perform:` (see feedback_no_perform_with.md), use blocks in the keyMap Dictionary rather than selector strings.

### Verification

- `mag build` compiles
- All TextEditor tests pass
- Manual test: all keybindings still work (Ctrl-A/E/K/Y/W/G/N/P, arrows, enter, backspace)

---

## Task 7: Extract common ListWidget

**Priority:** Tier 2
**Dependencies:** Task 1 (EventConstants), Task 3 (Theme)
**Estimated scope:** 1 new file + refactor 4 tools

### Description

SystemBrowser, Inspector, Debugger, and Menu all implement custom scrollable lists with selection, keyboard navigation (up/down/enter), and mouse click handling. Extract a reusable `ListWidget` that encapsulates this pattern.

### Interface

```
ListWidget subclass: View
  instanceVars: items selectedIndex scrollOffset normalStyle reverseStyle onSelect

  method: items: anArray
  method: selectedIndex
  method: selectedItem
  method: onSelect: aBlock     "callback when selection changes"
  method: displayOn: buf
  method: handleEvent: evt      "up/down/enter/mouse"
```

### Where it replaces custom code

- **SystemBrowser.mag**: category list, class list, method list (3 panes, each ~30 lines of scroll/select/render)
- **Inspector.mag**: variable list pane
- **Debugger.mag**: stack frame list, variable list
- **Menu.mag**: menu item list (already close to this — Menu could subclass or delegate to ListWidget)

### Implementation notes

- Start by extracting the pattern from ListView.mag (which already exists but tools don't use it)
- Ensure ListWidget supports: scroll clamping, visible range calculation, selected item highlighting, keyboard nav (up/down/enter/escape), mouse click-to-select
- Use `Theme normalStyle` and `Theme reverseStyle` (from Task 3)
- Use `EventConstants keyUp` etc. (from Task 1)

### Verification

- `mag build` compiles
- All existing tests pass
- SystemBrowser, Inspector, Debugger pane navigation unchanged

---

## Task 8: Add putStringFilled method to CellBuffer

**Priority:** Tier 3
**Dependencies:** None
**Estimated scope:** 1 method added to CellBuffer, ~8 files updated

### Description

The pattern of rendering a string and then padding the rest of a line with spaces (for selection highlighting) appears in 6+ places as manual character-by-character loops. Add `putStringFilled:x:y:style:width:` to `src/display/CellBuffer.mag`.

### Method signature

```
method: putStringFilled: str x: x y: y style: style width: width [
  "Write str at (x,y) with style, then pad remaining width with spaces."
  self putString: str x: x y: y style: style.
  | padStart padEnd |
  padStart := x + str size.
  padEnd := x + width.
  padStart to: padEnd - 1 do: [:i |
    self putChar: ' ' x: i y: y style: style
  ]
]
```

### Files with manual padding loops to replace

Search for patterns like `x to: width - 1 do: [:i | self putChar: ' '` in:
- `src/widgets/ListView.mag`
- `src/widgets/Menu.mag`
- `src/tools/SystemBrowser.mag`
- `src/tools/Inspector.mag`
- `src/tools/Debugger.mag`
- `src/tools/Transcript.mag`

### Verification

- `mag build` compiles
- All tests pass
- Selection highlighting renders identically

---

## Task 9: Normalize classObjectForName: return value

**Priority:** Tier 3
**Dependencies:** None
**Estimated scope:** 1–2 files

### Description

`classObjectForName:` returns `false` on failure instead of `nil`. This violates Smalltalk convention where failed lookups return `nil`. Find all callers and ensure they handle `nil` correctly, then fix the return value.

### Steps

1. Find where `classObjectForName:` is defined (likely SystemBrowser.mag or a Go primitive)
2. Change failure return from `false` to `nil`
3. Update all callers that check `= false` or `ifFalse:` to use `isNil ifTrue:`

### Verification

- `mag build` compiles
- SystemBrowser class selection still works when selecting invalid classes

---

## Task 10: Add proper Model usage to SystemBrowser

**Priority:** Tier 3
**Dependencies:** Task 7 (ListWidget)
**Estimated scope:** Large refactor of SystemBrowser.mag

### Description

SystemBrowser (528 lines) manages its own state and calls `self invalidate` directly instead of using the Model/View change/update protocol that already exists in `src/mvc/Model.mag` and `src/mvc/View.mag`. The todo example properly uses Model — SystemBrowser should follow the same pattern.

### Target

- SystemBrowser's data (selected category, selected class, selected method, class list, method list) should live in a Model subclass
- Selection changes should fire `changed:` notifications
- View panes should register as dependents and respond to `update:`
- This enables future cross-tool coordination (e.g., Inspector observing SystemBrowser's selection)

### Implementation notes

This is a large refactor. Consider:
1. Create `BrowserModel subclass: Model` holding selection state
2. Move category/class/method data into the model
3. Have SystemBrowser's view components register as dependents
4. Fire `changed: #selectedCategory` etc. on selection changes

### Verification

- `mag build` compiles
- All SystemBrowser tests pass
- Navigation behavior unchanged

---

## Dependency Graph

```
Task 1 (EventConstants) ─┬──→ Task 2 (BoxLayout)
                          ├──→ Task 6 (KeyMap)
                          └──→ Task 7 (ListWidget)
Task 3 (Theme) ──────────────→ Task 7 (ListWidget)
Task 4 (codeDirty bug) ──────→ (none)
Task 5 (autocomplete bug) ───→ (none)
Task 7 (ListWidget) ─────────→ Task 10 (Model usage)
Task 8 (putStringFilled) ────→ (none)
Task 9 (normalize return) ───→ (none)
```

**Parallelizable groups:**
- Wave 1: Tasks 1, 3, 4, 5, 8, 9 (all independent)
- Wave 2: Tasks 2, 6 (depend on Task 1)
- Wave 3: Task 7 (depends on Tasks 1, 3)
- Wave 4: Task 10 (depends on Task 7)
