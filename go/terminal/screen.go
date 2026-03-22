// Package terminal wraps tcell.Screen as a concrete struct so mag wrap
// can generate Maggie bindings for the interface methods.
package terminal

import (
	"fmt"
	"os"
	"runtime/pprof"

	"github.com/gdamore/tcell/v2"
)

// DebugLog writes a message to a log file for debugging.
func DebugLog(msg string) {
	f, err := os.OpenFile("/tmp/alto-debug.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err == nil {
		fmt.Fprintln(f, msg)
		f.Close()
	}
}

// Screen wraps tcell.Screen, exposing interface methods as struct methods.
type Screen struct {
	screen tcell.Screen
}

// NewScreen creates and returns a new terminal screen.
func NewScreen() *Screen {
	s, err := tcell.NewScreen()
	if err != nil {
		panic("Maggie error: GoError: " + err.Error())
	}
	return &Screen{screen: s}
}

// Init initializes the screen.
func (s *Screen) Init() {
	err := s.screen.Init()
	if err != nil {
		panic("Maggie error: GoError: " + err.Error())
	}
}

// Fini restores the terminal to its original state.
func (s *Screen) Fini() {
	s.screen.Fini()
}

// Clear clears the screen.
func (s *Screen) Clear() {
	s.screen.Clear()
}

// Show flushes changes to the terminal (diff-based, only changed cells).
func (s *Screen) Show() {
	s.screen.Show()
}

// Sync forces a full redraw of the terminal.
func (s *Screen) Sync() {
	s.screen.Sync()
}

// Size returns the screen dimensions as width, height.
func (s *Screen) Size() (int, int) {
	return s.screen.Size()
}

// PollEvent blocks until an event is available and returns it.
func (s *Screen) PollEvent() tcell.Event {
	return s.screen.PollEvent()
}

// StartProfile begins CPU profiling to /tmp/alto-cpu.prof
func StartProfile(dummy int) {
	f, err := os.Create("/tmp/alto-cpu.prof")
	if err != nil {
		return
	}
	pprof.StartCPUProfile(f)
}

// StopProfile stops CPU profiling.
func StopProfile(dummy int) {
	pprof.StopCPUProfile()
}

// PollKeyEvent blocks until a key event is available.
// Returns 4 ints:
//   Key events:    (keyCode, rune, mod, 0)
//   Mouse events:  (-2, buttons, x, y)
//   Resize events: (-3, width, height, 0)
func (s *Screen) PollKeyEvent() (int, int, int, int) {
	for {
		ev := s.screen.PollEvent()
		switch e := ev.(type) {
		case *tcell.EventKey:
			return int(e.Key()), int(e.Rune()), int(e.Modifiers()), 0
		case *tcell.EventMouse:
			x, y := e.Position()
			return -2, int(e.Buttons()), x, y
		case *tcell.EventResize:
			w, h := e.Size()
			return -3, w, h, 0
		default:
			continue
		}
	}
}

// WaitEvent blocks until any event, returns event type as string
// and the event object. Type is "key", "mouse", "resize", or "other".
func (s *Screen) WaitEvent() (string, tcell.Event) {
	ev := s.screen.PollEvent()
	switch ev.(type) {
	case *tcell.EventKey:
		return "key", ev
	case *tcell.EventMouse:
		return "mouse", ev
	case *tcell.EventResize:
		return "resize", ev
	default:
		return "other", ev
	}
}

// PostEvent posts an event into the event queue.
func (s *Screen) PostEvent(ev tcell.Event) {
	s.screen.PostEvent(ev)
}

// SetContent sets a cell at x,y with the given rune and style.
func (s *Screen) SetContent(x, y int, mainc rune, style *Style) {
	s.screen.SetContent(x, y, mainc, nil, style.S)
}


// GetContent returns the rune and style at x,y.
func (s *Screen) GetContent(x, y int) (rune, *Style) {
	mainc, _, style, _ := s.screen.GetContent(x, y)
	return mainc, &Style{S: style}
}

// SetStyle sets the default style for the screen.
func (s *Screen) SetStyle(style *Style) {
	s.screen.SetStyle(style.S)
}

// EnableMouse enables mouse button event reporting (clicks only, no motion).
func (s *Screen) EnableMouse() {
	s.screen.EnableMouse(tcell.MouseButtonEvents)
}

// DisableMouse disables mouse event reporting.
func (s *Screen) DisableMouse() {
	s.screen.DisableMouse()
}

// EnablePaste enables bracketed paste mode.
func (s *Screen) EnablePaste() {
	s.screen.EnablePaste()
}

// DisablePaste disables bracketed paste mode.
func (s *Screen) DisablePaste() {
	s.screen.DisablePaste()
}

// HasMouse returns true if the terminal supports mouse events.
func (s *Screen) HasMouse() bool {
	return s.screen.HasMouse()
}

// Fill fills the entire screen with the given rune and style.
func (s *Screen) Fill(r rune, style *Style) {
	s.screen.Fill(r, style.S)
}

// SetCursorStyle sets the cursor style.
func (s *Screen) SetCursorStyle(style tcell.CursorStyle) {
	s.screen.SetCursorStyle(style)
}

// ShowCursor shows the cursor at x,y.
func (s *Screen) ShowCursor(x, y int) {
	s.screen.ShowCursor(x, y)
}

// HideCursor hides the cursor.
func (s *Screen) HideCursor() {
	s.screen.HideCursor()
}

// DefaultStyle returns the default (zero-value) Style.
func DefaultStyle() *Style {
	return &Style{S: tcell.StyleDefault}
}

// NewStyle returns a fresh default Style (same as DefaultStyle).
func NewStyle() *Style {
	return NewWrappedStyle()
}
