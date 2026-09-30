+++
title = "USB Autosuspend Is Why Your Mouse Keeps Falling Asleep"
date = 2012-06-10

[taxonomies]
tags = ["linux", "ubuntu", "hardware"]
+++

Here is a symptom that will make you doubt your hardware. You stop moving the mouse for a few seconds, you move it again, and for a moment nothing happens. Then the pointer jumps to catch up. Sometimes a keyboard does the same: the first keystroke after a pause is swallowed. You will suspect the mouse, the cable, the USB port, the kernel. It is none of them.

**It is a power-saving feature doing exactly what it was told to do, to a device it should have left alone.**

This was written for Ubuntu 12.04, where the culprit is a package called `laptop-mode-tools`. Other distributions and other years have the same mechanism under different names, and the diagnosis transfers.

## What Is Happening

The Linux kernel can put an idle USB device into a low-power state, and wake it when it is needed again. This is called USB autosuspend. For a webcam or a printer it is harmless and saves a little battery. For an input device it is a disaster, because the thing that wakes the device is the very input you were trying to give it, and the wake-up takes long enough to notice.

The kernel has a sensible default here. It is `laptop-mode-tools` that overrides the default in the name of battery life, and it does so for every USB device it can find, unless you tell it otherwise. If you installed the package deliberately, you already know it is there. If you did not, check anyway, because it comes along with some laptop setups and you may have it without ever having asked for it:

```bash
dpkg -l laptop-mode-tools
```

If it is installed, it is almost certainly your problem.

## The Fix

The package keeps its USB policy in one file:

```text
/etc/laptop-mode/conf.d/usb-autosuspend.conf
```

Open it as root and find the line that decides whether the tool manages USB autosuspend at all. It ships as:

```bash
CONTROL_USB_AUTOSUSPEND="auto"
```

Change it to:

```bash
CONTROL_USB_AUTOSUSPEND="0"
```

That tells the package to keep its hands off USB power management entirely and leave the kernel's own defaults in place. Then restart the service so the change takes effect:

```bash
sudo /etc/init.d/laptop-mode restart
```

Move the mouse. The lag is gone, and it stays gone across reboots, because the configuration file is what the service reads on every start.

## The Gentler Alternative

If you want to keep autosuspend for everything except your input devices, the same file has a blacklist. Find the vendor and product identifiers of the offending devices:

```bash
lsusb
```

Each line ends with an `ID` of the form `046d:c52b`. Add the ones you want protected to the blacklist variable in the same configuration file, separated by spaces:

```bash
AUTOSUSPEND_USBID_BLACKLIST="046d:c52b 04f2:0402"
```

and restart the service as above. I do not bother. The battery saving from suspending a mouse is negligible, and the cost of the feature misfiring on a device I have not blacklisted yet is another afternoon like the one that produced this post.

## Why I Am Writing This Down

Not because the fix is hard. Because the symptom is so misleading. Nothing about a sluggish mouse says power management. It says broken hardware, and people replace hardware over it.

**A feature that is invisible when it works and looks like a hardware fault when it does not is a badly designed feature**, however good its intentions. The right default for anything the human touches directly is never to sleep. The package got that wrong, and until it is fixed upstream, the two lines above are the workaround.
