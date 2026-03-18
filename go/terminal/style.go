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
