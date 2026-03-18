// Package terminal wraps tcell.Screen as a concrete struct so mag wrap
// can generate Maggie bindings for the interface methods.
package terminal

import (
	"github.com/gdamore/tcell/v2"
)

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

// PostEvent posts an event into the event queue.
func (s *Screen) PostEvent(ev tcell.Event) {
	s.screen.PostEvent(ev)
}

// SetContent sets a cell at x,y with the given rune and style.
func (s *Screen) SetContent(x, y int, mainc rune, style tcell.Style) {
	s.screen.SetContent(x, y, mainc, nil, style)
}

// GetContent returns the rune and style at x,y.
func (s *Screen) GetContent(x, y int) (rune, tcell.Style) {
	mainc, _, style, _ := s.screen.GetContent(x, y)
	return mainc, style
}

// SetStyle sets the default style for the screen.
func (s *Screen) SetStyle(style tcell.Style) {
	s.screen.SetStyle(style)
}

// EnableMouse enables mouse event reporting.
func (s *Screen) EnableMouse() {
	s.screen.EnableMouse()
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
func (s *Screen) Fill(r rune, style tcell.Style) {
	s.screen.Fill(r, style)
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
