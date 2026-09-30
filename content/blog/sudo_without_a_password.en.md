+++
title = "Running sudo Without a Password, and What You Give Up"
date = 2013-05-05

[taxonomies]
tags = ["linux", "sysadmin", "security"]
+++

Typing a password every time you run `sudo` is a drag. It is also the point: the password is what stands between a program running as you and a program running as root. If you understand exactly what you are giving up and still want to give it up, here is how, and here is the honest accounting of the trade.

## When This Is Reasonable

There is a real case. A single-user laptop, with full disk encryption, that only you ever sit at, where a login already required a password and the screen locks when you leave. On such a machine an attacker who can run commands as you is already sitting at your unlocked session, and the `sudo` prompt is a speed bump rather than a wall.

There is also a bad case that looks like the good one: a shared machine, a server, anything reachable from the network, or any machine where you sometimes run software you did not write and did not read. Skip to the last section before deciding.

## The Setup

First, confirm you are in the `sudo` group, which is the group Debian and Ubuntu grant administrative rights to:

```bash
groups
```

If `sudo` is not in the list, add yourself, then log out and back in; group membership is read at login:

```bash
sudo adduser mark sudo
```

Now create a file in `/etc/sudoers.d/`. Do not edit `/etc/sudoers` itself; the drop-in directory exists so that package upgrades and your changes never fight, and so that one bad file cannot lock everyone out. Use `visudo`, which checks the syntax before saving, because a syntax error in a sudoers file can leave you with no working `sudo` at all:

```bash
sudo visudo -f /etc/sudoers.d/nopasswd
```

Put this in it:

```text
# Allow members of group sudo to run any command without a password
%sudo ALL=(ALL) NOPASSWD: ALL
```

Save. `visudo` sets the permissions correctly, but if you created the file some other way, fix them; `sudo` refuses to read a world-readable sudoers file:

```bash
sudo chmod 0440 /etc/sudoers.d/nopasswd
```

The next `sudo` command will not ask for anything. If it still does, check that the file name has no dot in it; files with a `.` or ending in `~` in `sudoers.d` are ignored, by design, so that editor backup files never become policy.

## A Narrower Version

You do not have to go all the way. The most common irritant is a handful of commands you run many times a day, and you can exempt only those:

```text
%sudo ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/bin/systemctl, /bin/mount, /bin/umount
```

Everything else still asks. This keeps most of the convenience and much less of the exposure, and it is what I would recommend to anyone who hesitates at the full version.

## What You Actually Gave Up

Be precise about it. Before the change, code running with your privileges could read and delete your files, send mail as you, and install anything into your home directory, but it could not touch the system without your password. After the change, **any process running as you is root whenever it wants to be.** A browser exploit, a malicious `make install`, a script pasted from a web page, a `pip install` of the wrong package: each of them now owns the machine, not just your account.

The other thing you gave up is the pause. The password prompt is the last moment at which you look at the command and ask whether you meant it. `sudo rm -rf` with a typo in the path is a different experience with and without that pause.

That is the whole trade. Convenience on one side, the distance between your account and root on the other. On my own laptop I have made it, with the narrow list rather than the blanket rule. On anything anyone else can reach, I have not, and I would not.
