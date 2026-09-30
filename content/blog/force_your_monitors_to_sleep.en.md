+++
title = "Put Your Monitors to Sleep From the Command Line"
date = 2013-07-21

[taxonomies]
tags = ["linux", "command-line"]
+++

The screen saver timeout is the wrong tool for a common situation. You are leaving the desk for an hour, you know it, and you do not want to wait for the idle timer to notice. You also do not want to lock the screen, because there is a compile or a download running and you want to glance at it when you come back without typing a password. You just want the monitors dark, now.

X has had the answer for a very long time, and it is one line.

## The Command

```bash
xset dpms force suspend
```

That is the whole trick. DPMS is the display power management standard, `xset` is the X server's settings tool, and `force` tells the server to enter a power state immediately instead of waiting for the idle timer. The monitors go dark within a second or two. Move the mouse or touch a key and they come back.

There are three power states you can force, and which one you want depends on the monitor:

```bash
xset dpms force standby
xset dpms force suspend
xset dpms force off
```

`standby` is the lightest: the monitor blanks but keeps its electronics warm and wakes instantly. `suspend` goes deeper and saves more power. `off` is what the name says, and some monitors take a few seconds to come back from it, sometimes with an annoying re-sync flicker. **On modern flat panels the three are nearly indistinguishable**, so I use `suspend` as the middle ground and stop thinking about it.

## Seeing What Is Configured

`xset q` prints the current state of everything `xset` controls, including the DPMS timers:

```bash
xset q | grep -A 3 DPMS
```

You will see three numbers: the idle times, in seconds, after which the server enters standby, suspend and off on its own. If DPMS shows as disabled, the force command still works, but nothing will happen automatically. To turn the automatic behaviour on with timers of your choosing:

```bash
xset dpms 600 900 1200
xset +dpms
```

That is standby after ten minutes, suspend after fifteen, off after twenty. `xset -dpms` disables it again, which is what you want while watching a film.

## A Small Wrinkle

If you run the command from a terminal and the screen does not go dark, the most likely reason is that releasing the Enter key counted as activity and woke the screen up again a few milliseconds after it went to sleep. The fix is to give yourself a moment to let go of the keyboard:

```bash
sleep 1; xset dpms force suspend
```

You will find this exact incantation in a lot of people's shell aliases, and now you know why.

## Binding It to a Key

Typing the command is fine, but the point was not to think about it. Every desktop environment has a way to bind a shell command to a key. In GNOME it is under keyboard shortcuts, custom shortcuts; in KDE it is a custom shortcut under input actions; in any window manager that reads a configuration file it is one line in that file. Bind this:

```bash
sh -c 'sleep 1; xset dpms force suspend'
```

I use a key I never otherwise press, one of the spare function keys most keyboards carry. One tap, the monitors sleep, the machine keeps working, and nothing is locked.

## Why Bother

Two reasons, and neither is virtue.

The first is money and heat. A pair of large monitors draws a noticeable amount of power and warms the room, and there is no reason to pay for light nobody is looking at.

The second is that this is exactly the kind of thing a graphical interface is bad at. There is a screen saver dialog, and a power settings dialog, and a lock screen, and none of them does the plain thing of turning the monitors off right now. The command line does, in a line, and it did so long before the dialogs existed. **The old tools did not become obsolete when the settings panels appeared; they just stopped being advertised.**
