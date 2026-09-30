+++
title = "A LilyPond Cheat Sheet: Everything I Look Up, on One Page"
date = 2014-08-03

[taxonomies]
tags = ["music", "reference"]
+++

LilyPond is to sheet music what LaTeX is to documents: you describe the music in a text file and a compiler produces beautiful engraving. The price is the same as with LaTeX. The syntax is compact, there is a lot of it, and I forget the parts I use rarely. This is the page I wish I had had, kept deliberately short: the constructs that cover nearly every piece I set, and nothing else.

**Everything below goes in a plain text file ending in `.ly`, and `lilypond file.ly` turns it into `file.pdf`.**

## The Skeleton

```lilypond
\version "2.18.2"

\header {
  title = "Example"
  composer = "Anonymous"
}

\relative c' {
  \clef treble
  \key g \major
  \time 3/4
  d4 g b | a2. | \bar "|."
}
```

The `\version` line is mandatory and lets the `convert-ly` tool update your file when the syntax changes. The braces after `\relative` hold the music.

## Pitches and Accidentals

Notes are lowercase letters `c d e f g a b`. Sharps and flats are suffixes: `cis` is C sharp, `bes` is B flat, `cisis` and `beses` are double sharp and double flat. `r` is a rest, `s` is a silent spacer that takes up time without printing anything.

Octaves are marked with `'` (up) and `,` (down). In absolute mode `c'` is middle C, `c''` the octave above, `c` the octave below.

## Relative Mode

Almost everyone writes in relative mode, because it removes most octave marks. Inside `\relative c' { ... }` each note is placed in the octave that makes it closest to the previous note, within a fourth. When the interval is a fifth or more you add `'` or `,` to say which way to jump:

```lilypond
\relative c' { c d e f g a b c }      % one rising scale, no marks needed
\relative c' { c g' c, }              % g a fifth up, then c a fourth down
```

The argument after `\relative` sets the reference for the first note only.

## Durations

A number after the note is the duration: `c1` whole, `c2` half, `c4` quarter, `c8` eighth, `c16` sixteenth. A dot lengthens by half: `c4.`. A duration sticks until you write a new one, so `c4 d e f` is four quarter notes.

Ties use `~`, tuplets use `\tuplet`:

```lilypond
c4~ c8 d8 | \tuplet 3/2 { e8 f g } a4
```

Bar checks with `|` are optional but catch counting mistakes: LilyPond warns when a bar line falls in the wrong place.

## Key, Time, Clef

```lilypond
\key d \minor
\time 6/8
\clef bass
```

Clefs: `treble`, `bass`, `alto`, `tenor`, `percussion`. A key signature is `\key` followed by a pitch and `\major` or `\minor`. Changing any of these mid-piece is just writing it again where the change happens.

## Chords

Simultaneous notes go in angle brackets, with the duration after the closing bracket:

```lilypond
<c e g>4 <d f a>4 <e g c'>2
```

For chord symbols above the staff, use chord mode, where a letter and a suffix name the chord:

```lilypond
\chords { c1 f2 g2:7 a1:m }
```

## Dynamics, Articulation, Tempo

Dynamics attach to a note with a backslash: `c4\p d\mf e\f f\ff`. Crescendo and diminuendo are `\<` and `\>`, ended with `\!`:

```lilypond
c4\< d e f\! g4\> f e d\!
```

Articulation marks are suffixes: `c4-.` staccato, `c4->` accent, `c4-^` marcato, `c4\fermata`. Slurs are parentheses around the phrase: `c4( d e f)`. Phrasing slurs use `\(` and `\)`.

Tempo goes at the top of the music:

```lilypond
\tempo "Allegro" 4 = 120
```

## Lyrics

Write the melody, then attach words with one syllable per note; hyphens join syllables of a word and `__` extends a syllable over several notes:

```lilypond
\relative c' {
  \time 4/4
  c4 d e f | g2 g
}
\addlyrics {
  Twin -- kle twin -- kle lit -- tle star
}
```

`\addlyrics` follows the music expression it belongs to. For more than one verse, repeat it.

## Several Voices and Staves

Two independent voices on one staff:

```lilypond
\relative c'' {
  << { e4 f g a } \\ { c4 d e f } >>
}
```

The `<<` and `>>` say simultaneous, and `\\` splits the contents into voices with stems pointing opposite ways.

Several staves are a `\new StaffGroup` or, for piano, a `\new PianoStaff`, each containing `\new Staff` blocks:

```lilypond
\new PianoStaff <<
  \new Staff = "right" \relative c'' { c4 d e f | g1 }
  \new Staff = "left"  \relative c  { \clef bass c4 e g e | c1 }
>>
```

## Repeats

```lilypond
\repeat volta 2 { c4 d e f }
\alternative { { g2 g } { g2 c } }
```

`volta` prints repeat bar lines and the alternative endings; `\repeat unfold 2 { ... }` writes the music out twice instead.

## Compiling

```bash
lilypond piece.ly           # produces piece.pdf and piece.midi if \midi is present
lilypond --png piece.ly     # a PNG instead
convert-ly -e piece.ly      # update the file to the installed version's syntax
```

Add a `\layout { }` block for engraving and a `\midi { }` block for sound inside a `\score { ... }` when you want both from one file.

## Why a Sheet This Short

Because the manual is excellent and enormous, and I do not want the manual. I want the twenty things that cover a hymn, a folk tune, a two-part exercise and a lead sheet. That is what is above. **When a piece needs something not on this page, that is the signal to open the manual, and not before.**
