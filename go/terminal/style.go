package terminal

import (
	"github.com/gdamore/tcell/v2"
)

// Style wraps tcell.Style as a concrete struct for mag wrap.
type Style struct {
	S tcell.Style
}

// NewWrappedStyle returns a default style wrapper.
func NewWrappedStyle() *Style {
	return &Style{S: tcell.StyleDefault}
}

// Reverse returns a new Style with reverse attribute toggled.
func (s *Style) Reverse(on bool) *Style {
	return &Style{S: s.S.Reverse(on)}
}

// Bold returns a new Style with bold attribute toggled.
func (s *Style) Bold(on bool) *Style {
	return &Style{S: s.S.Bold(on)}
}

// Italic returns a new Style with italic attribute toggled.
func (s *Style) Italic(on bool) *Style {
	return &Style{S: s.S.Italic(on)}
}

// Dim returns a new Style with dim attribute toggled.
func (s *Style) Dim(on bool) *Style {
	return &Style{S: s.S.Dim(on)}
}

// Foreground returns a new Style with the given foreground color.
func (s *Style) Foreground(c tcell.Color) *Style {
	return &Style{S: s.S.Foreground(c)}
}

// Background returns a new Style with the given background color.
func (s *Style) Background(c tcell.Color) *Style {
	return &Style{S: s.S.Background(c)}
}

// ForegroundColor sets the foreground using an int32 color value (wrapper-friendly).
func (s *Style) ForegroundColor(c int32) *Style {
	return &Style{S: s.S.Foreground(tcell.Color(c))}
}

// BackgroundColor sets the background using an int32 color value (wrapper-friendly).
func (s *Style) BackgroundColor(c int32) *Style {
	return &Style{S: s.S.Background(tcell.Color(c))}
}

// PostEventKey posts a synthetic key event to the screen (wrapper-friendly).
func (s *Screen) PostEventKey(k, ch, mod int32) {
	ev := tcell.NewEventKey(tcell.Key(k), rune(ch), tcell.ModMask(mod))
	s.screen.PostEvent(ev)
}

// Equals returns true if two styles have the same underlying tcell.Style.
func (s *Style) Equals(other *Style) bool {
	return s.S == other.S
}
