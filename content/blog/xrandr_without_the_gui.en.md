+++
title = "Set Your Screens With xrandr Once and Never Open the Display Dialog Again"
date = 2012-09-30

[taxonomies]
tags = ["linux", "command-line"]
+++

Every desktop environment has a display settings dialog, and every one of them has the same failing: it forgets. You plug the laptop into the projector, the dialog guesses wrong, you fix it by hand, you unplug, and next week you do it all again. The layout you want is the same every time. The tool that sets it should be a command, not a conversation.

**Everything the dialog does, `xrandr` does from the shell, and a command can be saved.** Here is enough of it to stop touching the dialog.

## See What You Have

```bash
xrandr --query
```

The output lists every output the graphics card knows about, whether something is connected to it, and the modes each connected screen supports, with the current one marked by an asterisk and the preferred one by a plus sign. A typical laptop shows something like:

```text
LVDS1 connected 1366x768+0+0 (normal left inverted right x axis y axis) 344mm x 194mm
   1366x768       60.0*+
   1024x768       60.0
VGA1 connected 1920x1080+1366+0 (normal left inverted right x axis y axis) 510mm x 287mm
   1920x1080      60.0*+
   1280x1024      60.0
HDMI1 disconnected (normal left inverted right x axis y axis)
```

The names on the left (`LVDS1`, `VGA1`, `HDMI1`) are what every other command refers to. They are stable for a given machine, which is what makes a saved script possible.

## Set a Mode

To put one output at a specific resolution:

```bash
xrandr --output VGA1 --mode 1920x1080
```

To let it pick the mode the monitor reports as preferred, which is nearly always right:

```bash
xrandr --output VGA1 --auto
```

To turn an output off, which is what you want for the laptop panel when the lid is closed:

```bash
xrandr --output LVDS1 --off
```

## Arrange Them

Position is relative to another output:

```bash
xrandr --output VGA1 --auto --right-of LVDS1
```

The alternatives are `--left-of`, `--above` and `--below`. For a presentation you usually want the projector to mirror the laptop instead:

```bash
xrandr --output VGA1 --auto --same-as LVDS1
```

Mirroring works cleanly only when both screens run the same mode, so it may be worth forcing a common one with `--mode` on both. And when a monitor is mounted the wrong way up:

```bash
xrandr --output VGA1 --rotate left
```

All of these combine into one command, and one command is better than several because the X server reconfigures once instead of flickering through intermediate states:

```bash
xrandr --output LVDS1 --auto --output VGA1 --auto --right-of LVDS1 --output HDMI1 --off
```

## Save the Layouts You Use

Now the point of the exercise. Put the layouts you actually use into a script, one function per situation:

```bash
#!/bin/bash
# screens.sh - set a known display layout

set -e

home() {
	xrandr --output LVDS1 --auto \
	       --output VGA1 --auto --right-of LVDS1 \
	       --output HDMI1 --off
}

laptop() {
	xrandr --output LVDS1 --auto \
	       --output VGA1 --off \
	       --output HDMI1 --off
}

projector() {
	xrandr --output LVDS1 --mode 1024x768 \
	       --output VGA1 --mode 1024x768 --same-as LVDS1
}

case "$1" in
	home|laptop|projector) "$1" ;;
	*) echo "usage: $0 home|laptop|projector" >&2; exit 1 ;;
esac
```

Make it executable and put it on your path. From then on the whole ritual is:

```bash
screens.sh projector
```

Bind the common cases to keys in your window manager and you will not need the terminal either.

## Why Not Let the Desktop Handle It

Because it cannot know what you want. A desktop environment sees a new monitor and has to guess: mirror or extend, which side, which resolution. Its guess is a default, and defaults are for people who have not decided. You have decided. You have three or four layouts and you know which one you want by looking at the room.

**A decision you have already made should be one command, and a command is something you can name, store, version and bind to a key.** The dialog offers none of that. It offers a fresh guess every time, and asks you to correct it with the mouse.

The script above is about twenty lines. It has saved me more minutes than anything else of its size.
