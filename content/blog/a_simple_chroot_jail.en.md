+++
title = "A Simple Chroot Jail for a Single Application"
date = 2011-06-19

[taxonomies]
tags = ["linux", "security", "sysadmin"]
+++

Sometimes you want to run one program in a box, so that if it is compromised it cannot see the rest of the filesystem. The oldest tool for this on Unix is `chroot`, which changes what a process believes the root directory is. It is not a container and it is not a security boundary against a determined attacker with root, but for confining a service to a small world of its own it is simple and it works. Here is how to build one by hand, which is worth doing once so that you understand what the fancier tools are doing for you.

## Pick a Root and Find the Dependencies

Say the program is `/usr/bin/myapp`. The jail is just a directory that will become its `/`:

```bash
sudo mkdir -p /jail/{bin,lib,lib64,etc,dev,usr/bin}
```

The program will not run without the shared libraries it links against. Ask the dynamic linker what they are:

```bash
ldd /usr/bin/myapp
```

That prints each library and its path. Copy the binary and every library it named into the jail, keeping the same paths:

```bash
sudo cp /usr/bin/myapp /jail/usr/bin/
for lib in $(ldd /usr/bin/myapp | grep -o '/[^ ]*'); do
    sudo cp --parents "$lib" /jail/
done
```

`cp --parents` recreates the directory structure under `/jail`, so a library from `/lib/x86_64-linux-gnu/` lands in the matching place inside the jail. This is the whole trick: the jailed program looks for its libraries at the same paths, and now those paths exist inside the box.

## A Shell to Look Around With

While setting the jail up you want a shell inside it to test. A normal shell like bash drags in many libraries. `sash`, the stand-alone shell, is built statically and has common commands compiled in, so it needs nothing outside itself:

```bash
sudo apt-get install sash
sudo cp /bin/sash /jail/bin/
```

Now you can enter the jail and check that the program's world is complete:

```bash
sudo chroot /jail /bin/sash
```

If a command inside complains that a file is missing, that file is a dependency you have not copied in yet.

## Device Nodes

Many programs need at least `/dev/null`, and some need `/dev/zero` and `/dev/urandom`. These are not regular files; recreate them with `mknod`:

```bash
sudo mknod -m 666 /jail/dev/null c 1 3
sudo mknod -m 666 /jail/dev/zero c 1 5
sudo mknod -m 644 /jail/dev/urandom c 1 9
```

The numbers are the character-device major and minor numbers, the same ones the real `/dev` uses.

## Run the Program Jailed

```bash
sudo chroot /jail /usr/bin/myapp
```

The process now sees `/jail` as its root. It cannot open `/etc/passwd` on the host, cannot read your home directory, cannot wander the filesystem, because from inside none of that exists.

## What a Chroot Is Not

Be honest about the limits, because chroot is often trusted for more than it delivers.

- **A process running as root can break out of a chroot.** It is a confinement for reducing accidental exposure and containing an unprivileged service, not a sandbox against a root-level attacker. Run the jailed program as an unprivileged user.
- It shares the host kernel, network, and process table. It hides the filesystem and nothing else.
- Keeping the copied libraries up to date is on you. A security fix to a library on the host does not reach the copy inside the jail until you copy it again.

This is exactly why containers exist: they add namespaces for the network, processes, and users, and a tool that manages the filesystem for you, on top of the same idea. Build the chroot once by hand and the value the container adds becomes obvious, because you will have felt every gap it fills.
