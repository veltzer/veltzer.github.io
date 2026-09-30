+++
title = "Ripping CDs on Linux Without Losing Anything"
date = 2012-11-04

[taxonomies]
tags = ["linux", "audio", "command-line"]
+++

I did a small survey of the CD ripping tools on Linux, because I wanted to convert a shelf of discs once and never do it again, and I wanted the result to be a faithful copy rather than a convenient one. The tools divide cleanly into two questions: how accurately they read the disc, and how much of the tagging and encoding they do for you.

## The Accuracy Question

A CD does not read back perfectly. Scratches and drive quirks mean a naive read can drop or misread samples, and you will not hear the difference until the quiet passage where you do. The tool that solves this is `cdparanoia`, which re-reads uncertain sectors until it is confident, and it is the engine most of the good rippers use underneath.

On its own it just extracts audio:

```bash
cdparanoia -B
```

The `-B` writes one WAV per track. It is slow, because being careful is slow, and that is the point.

## The Convenience Question

Nobody wants a folder of `track01.wav`. You want FLAC files, tagged with artist, album and title, in sensibly named directories. Several tools wrap `cdparanoia` and add that:

- **abcde** ("A Better CD Encoder") is a shell script that does the whole pipeline: read, look up the metadata, encode, tag, name. It is configured by a text file and is my recommendation for the command line.
- **whipper** (formerly morituri) is the accuracy purist's choice. It compares its rip against the AccurateRip database, so you get told whether your copy matches what thousands of other people extracted from the same pressing. If you care about a provably correct rip, this is the one.
- **Sound Juicer** is the GNOME graphical ripper: insert, click, done. Fine for casual use, less configurable.
- **Asunder** is a light graphical ripper with no desktop dependencies, good on a minimal system.

## Lossless or Lossy

Rip to FLAC. It is lossless, so it is a true copy of the disc, it tags cleanly, and disk is cheap. You can always transcode FLAC down to a lossy format for a phone later; you can never recover what a lossy encode threw away. Ripping straight to MP3 or AAC means doing the slow, careful read once and then discarding most of what it recovered, which defeats the effort.

## The Pipeline I Settled On

```bash
sudo apt-get install abcde flac cd-discid
# edit ~/.abcde.conf: set OUTPUTTYPE=flac and a naming scheme
abcde -o flac
```

`abcde` reads the disc through `cdparanoia`, looks the album up for tags, encodes each track to FLAC, and files them under `Artist/Album/`. One command per disc, a faithful copy at the end, and nothing to redo when you replace your phone or your player. Set it up once in `~/.abcde.conf` and the shelf empties itself an insert at a time.

If a disc is precious and scratched, run `whipper` on that one and check it against AccurateRip. For everything else, `abcde` to FLAC is the sweet spot between careful and effortless.
