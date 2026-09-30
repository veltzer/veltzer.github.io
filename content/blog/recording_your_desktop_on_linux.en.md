+++
title = "Recording Your Desktop on Linux: The Tools and the One Command I Use"
date = 2013-11-24

[taxonomies]
tags = ["linux", "video"]
+++

Recording the screen is one of those tasks with too many tools and too little guidance about which to pick. Here is the survey, ranked by how much I actually use each one, and the single command that covers most of what I need.

## The Tools

**recordMyDesktop** was for years the default answer. It records a window or the full screen to an Ogg Theora file, has a small GTK front end, and is easy. Its problems are that it is slow to encode, tends to drop frames on a busy screen, and produces a format that is awkward everywhere except Linux. Fine for a quick demonstration; painful for anything longer.

**ffmpeg with x11grab** is the general-purpose answer. `ffmpeg` can read directly from the X server as an input device, encode to anything, and capture audio at the same time. It has no interface, which is either its main flaw or its main virtue, and it is what most of the friendlier tools call underneath.

**SimpleScreenRecorder** is the tool I recommend to people who want a window with buttons. It is genuinely simple, it records a region or a window or the whole screen, it captures PulseAudio and JACK, it shows you the frame rate it is achieving while recording, and it was written by someone who cared about not dropping frames under load. If you record often and do not want to remember flags, install it and stop reading.

**OBS Studio** is a broadcasting tool that also records. It composes scenes from several sources, a screen, a webcam, an image, a text overlay, and switches between them live. It is the right choice for a lecture with a talking head in the corner, and overkill for showing someone which menu to click.

## Audio

Whatever you record with, the audio question is the same: do you want the microphone, the sound the machine is playing, or both? With PulseAudio, both are sources. Your microphone appears under its own name; the machine's output appears as a *monitor* of the output device. List them:

```bash
pactl list short sources
```

Something like `alsa_output.pci-0000_00_1b.0.analog-stereo.monitor` is the sound the machine is making; the entry without `.monitor` is the microphone. For a narrated demonstration you usually want the microphone alone; for recording a video call or a game, the monitor.

## The Command

This is what I run for a plain full-screen recording with narration:

```bash
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :0.0 \
       -f pulse -i default \
       -c:v libx264 -preset ultrafast -crf 18 \
       -c:a aac -b:a 128k \
       screencast.mkv
```

Line by line. The first input is the X display, at thirty frames a second and the full screen size; to record a region, give a smaller size and add the offset, `-i :0.0+100,200`. The second input is PulseAudio's default source, which is your microphone unless you changed it; put a monitor name there instead to capture the machine's output. Video is encoded with x264 at the fastest preset, which is the important part: **the encoder must keep up with the screen in real time, and quality can be recovered later.** `crf 18` is high quality; the file will be large. Audio is AAC. The container is Matroska because it survives an interrupted recording; an MP4 that is not properly closed is a broken file.

Stop with `q` in the terminal, not with Ctrl-C, so the file is finalised.

## The Second Pass

The fast preset produces big files. Once the recording is done there is no real-time constraint, so re-encode at leisure:

```bash
ffmpeg -i screencast.mkv -c:v libx264 -preset slow -crf 23 -c:a copy screencast.mp4
```

This takes a while and produces something a fraction of the size, in a container every player and every website accepts. Do not try to get there in one step; recording and compressing have opposite requirements and the recording is the one you cannot redo.

## What I Would Tell Someone Starting Out

Install SimpleScreenRecorder if you want buttons. Learn the one `ffmpeg` command if you want something scriptable. Reach for OBS only when you need to compose more than one source. And whatever you use, record fast and compress later, because the frame you drop while encoding beautifully is gone for good.
