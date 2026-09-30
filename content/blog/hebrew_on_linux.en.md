+++
title = "Hebrew on Linux: A Practical Tour"
date = 2012-02-26

[taxonomies]
tags = ["linux", "hebrew"]
+++

Hebrew on Linux works, and has worked for years, but the pieces live in different places and nobody hands you the list. This is the list I wish I had been handed: the keyboard, the fonts, right-to-left text in places that were never designed for it, and spelling.

## The Keyboard

You want two layouts, a key to switch between them, and an indicator so you know which one you are in. On any modern desktop that is a settings dialog, but it is also a single command, which is useful in a window manager that has no dialog:

```bash
setxkbmap -layout "us,il" -option "grp:alt_shift_toggle,grp_led:scroll"
```

Alt+Shift toggles the layout and the Scroll Lock light tells you when you are in Hebrew. Put it in your X startup file and it survives logins. If you prefer a different switch key, `man xkeyboard-config` lists the `grp:` options; the Caps Lock variant is popular with people who never use Caps Lock.

The standard Israeli layout puts the letters where a Hebrew typewriter put them. The `il` layout also has a `phonetic` variant for people who never learned that arrangement and would rather have alef under A.

## Fonts

The default fonts on most distributions include DejaVu, which has Hebrew, so text renders. It does not render beautifully. For anything you will read at length, install the Culmus collection, which is the free Hebrew font family made for exactly this:

```bash
sudo apt-get install culmus
```

You get David, Frank Ruehl, Miriam, Nachlieli and others, covering the serif and sans and monospace cases. Then run `fc-cache -f` and pick them in whatever application you are using. Frank Ruehl is the one that looks like a printed book.

## Right-to-Left in Terminals

Here is the part that is genuinely awkward. A terminal is a grid of cells filled left to right, and it has no notion of bidirectional text. Hebrew comes out reversed: the letters are right but the order is backwards, and mixed lines of Hebrew and English are scrambled.

The fix is a filter that applies the Unicode bidirectional algorithm to each line and emits the characters in visual order, so a dumb left-to-right display shows them correctly. The tool is `fribidi`:

```bash
sudo apt-get install fribidi
cat hebrew_file.txt | fribidi
```

For a whole session you can wrap things you read often:

```bash
alias hcat='fribidi'
alias hless='fribidi | less'
```

This is a display trick, not a fix. If you copy text out of the terminal it will be in visual order and wrong. For editing Hebrew, use an editor that understands bidi: Vim with `set rightleft` for pure Hebrew files, Emacs with its bidi support, or any graphical editor, all of which do it properly. **The terminal is for looking at Hebrew; do the writing somewhere that knows what direction it is going.**

## Spelling

The Hebrew spell checker is Hspell, a morphological analyser that actually understands the language rather than matching a word list. It plugs into everything that speaks the Hunspell interface:

```bash
sudo apt-get install hspell hunspell-he
```

After that LibreOffice, Firefox and any editor using Enchant or Hunspell can check Hebrew. On the command line `hspell` itself takes a file and lists what it does not recognise, which is useful in scripts.

## LibreOffice

Enable complex text layout under Tools, Options, Language Settings, Languages: tick the CTL box and set Hebrew as the CTL language. This unlocks the right-to-left paragraph buttons on the toolbar and lets you set a separate CTL font, which is where your Culmus choice goes. Word documents from Hebrew-speaking senders then open with their direction intact.

One habit worth acquiring: set the paragraph direction rather than fighting the cursor. A right-to-left paragraph handles embedded English numbers and words correctly on its own; a left-to-right paragraph with Hebrew typed into it does not.

## What Still Hurts

Mixed-direction text in file names and shell commands is unpleasant and I mostly avoid it. Some applications still render Hebrew with the wrong font weight or ignore the CTL font. And the bidi algorithm gets the neutral characters, punctuation and brackets, wrong often enough that you learn to check.

None of this is a reason not to work in Hebrew on Linux. It is a reason to spend the hour setting it up properly, once, instead of fighting each piece as you meet it.
