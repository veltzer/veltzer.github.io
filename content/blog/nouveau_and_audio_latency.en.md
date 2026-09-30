+++
title = "The Open Nouveau Driver Was Causing My Audio Latency"
date = 2013-01-13

[taxonomies]
tags = ["linux", "audio", "hardware"]
+++

This is a short note recording a diagnosis, because it took me a while to arrive at it and the cause was not where I was looking.

## The Symptom

Low latency audio on Linux means running JACK with a small buffer, so that the time between a key press on a MIDI keyboard and the sound coming out of the speakers is a few milliseconds rather than a noticeable delay. When the machine cannot keep up, JACK reports an xrun: a buffer that was not filled in time, which you hear as a click or a dropout.

I was getting xruns. Not a storm of them, but a steady trickle, and a trickle is enough to make recording impossible. The usual suspects were all checked: a real-time capable kernel, the audio group with the right limits in `/etc/security/limits.d/`, the right frame and period settings in `qjackctl`, no swapping, no CPU frequency scaling. Nothing helped.

## Finding the Culprit

The tool that pointed the way was `latencytop`, which shows which kernel paths are holding up processes and for how long. Running it as root while JACK was going:

```bash
sudo latencytop
```

The top offender was not the sound card, the disk or the network. It was the graphics driver. The open source `nouveau` driver for NVIDIA cards was spending long stretches inside the kernel with interrupts effectively blocked, and the audio thread was waiting behind it.

You can see the same thing from the other side by watching the xrun count in JACK while you do things on screen. Moving windows around or scrolling a web page produced clicks. A perfectly still desktop did not. **The audio was fine; the graphics driver was stealing the time it needed.**

## The Fix

Replace `nouveau` with the proprietary NVIDIA driver. On Ubuntu of that era it is one package:

```bash
sudo apt-get install nvidia-current
sudo reboot
```

Make sure `nouveau` is not loaded afterwards; the package should blacklist it, but check:

```bash
lsmod | grep nouveau
```

If that prints nothing, the open driver is gone. The xruns went with it. Same kernel, same JACK settings, same card, zero xruns during an afternoon of playing.

## What to Take From This

I am an open source person and I would rather run the open driver. But for this particular job, in this particular year, the proprietary driver was the difference between a usable audio workstation and a toy, and pretending otherwise would have cost me the workstation.

Two more general points.

First, when a real-time process is late, do not assume the problem is in its own subsystem. Anything that holds the kernel for too long delays everything else, and the graphics driver is a prime candidate because it does a lot of work in interrupt context and is written by people who care about frame rates rather than about your audio buffer.

Second, `latencytop` is the tool for exactly this question. It does not tell you your program is slow; it tells you what your program was waiting for. That is the question you actually have when you are chasing xruns, and I wish I had reached for it first.
