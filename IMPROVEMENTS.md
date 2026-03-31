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

### ~~2.1 Create Event object hierarchy~~ DONE
Created `src/Event.mag` with `KeyEvent` and `MouseEvent` classes. Both have proper accessors
(`key`, `rune`, `mod`, `x`, `y`, `buttons`), `isKey`/`isMouse` type tests, `dispatchTo:` for
polymorphic dispatch, `withX:y:` for coordinate translation, and `at:ifAbsent:` compatibility
so existing handler code continues to work during gradual migration. Display, Window, and
SplitPane updated to create and use typed events. Dictionary construction eliminated from
Display>>run, Window>>handleEvent:, and SplitPane>>handleMouseEvent:.

### ~~2.2 Decompose Display>>run and Display>>dispatchMouse:~~ DONE
`run` decomposed into: `handleResize:height:`, `buildEvent:rune:mod:fourth:`,
`dispatchWithErrorRecovery:`, `dispatchEvent:`. `dispatchMouse:` decomposed into:
`handleResizeDrag:y:buttons:`, `handleWindowDrag:y:buttons:`, `dismissMenuIfOutside:y:`,
`windowHitTest:x:y:buttons:`. Largest method is now ~15 lines (down from 63/83).

### ~~2.3 Fix O(n²) string building~~ DONE
TextEditor>>text: and Debugger>>splitSource: now use `copyFrom:to:` substring extraction
instead of char-by-char concatenation. Inspector>>wrapText:width: also rewritten.
TextEditor>>text uses inject:into: for joining.

---

## Priority 3: Design Debt (Lower urgency, valuable long-term)

### ~~3.1 Controller separation — decided against, formalized instead~~ DONE
After analysis of ST-80 history and modern Smalltalk consensus (Morphic, Spec2, etc.):
Controllers solved input *scheduling* in 1981; modern event dispatch makes them redundant.
Every successor (Self, Squeak, Pharo, Cocoa, React) dropped separate Controllers.

Instead:
- View base class now has `handleEvent:` as a documented no-op — View is both visual and
  input handler, no separate Controller needed.
- All handlers migrated from dictionary protocol to typed event accessors (`evt isKey`,
  `evt key`, `evt isMouse`, `evt x`, `evt buttons`).
- Window gains convenience `title:content:frame:` constructor (view = controller).
- `Window>>contentController:` slot kept for cases like SplitPane where delegation differs.

### ~~3.2 Standardize new/initialize protocol~~ DONE
Display (`initDisplay`), Window (`initDefaults`), and Style (`initDefault`) all renamed to
`initialize`. All classes now follow the standard `new` → `initialize` pattern.
Factory methods (BoxLayout, CellBuffer, ListView) kept as-is — appropriate for parameterized init.

### ~~3.3 Replace hardcoded layout dimensions with named methods~~ DONE
Inspector: `listPaneWidth` method (was hardcoded 22 in two places).
SystemBrowser: `listPaneHeight` and `paneWidthFor:` methods (fixes inconsistency between
`displayOn:` and `handleMouseLocalX:` pane width computation).
Debugger: `framePaneWidth:` and `framePaneHeight:` methods.

### ~~3.4 Add = and hash to Rectangle and Style~~ DONE
Rectangle has = and hash. Style has standard = (keeps equals: as alias). Display updated to use =.

### ~~3.5 Clarify App vs Display responsibilities~~ DONE
Display now delegates desktop menu to a configurable `desktopMenuBlock` (via `onDesktopMenu:`).
Default behavior preserved in `defaultDesktopMenuAt:y:`. App wires its `desktopMenuBlock` to
Display. Boundary is now clear: Display = compositor + event loop, App = user-facing API.
