+++
title = "Reading Your Browser's Saved Passwords From the Command Line"
date = 2014-05-20

[taxonomies]
tags = ["linux", "security", "command-line"]
+++

Every browser offers to remember your passwords, and most people accept. It is worth knowing exactly where those passwords go and how little stands between them and anyone who can run a command as you. This post shows how to read the saved passwords of Firefox and Chrome from a shell on Linux. The point is partly practical, since a script that reads them is a fine way to migrate between browsers or to audit what you have saved, and partly a warning.

## Where Firefox Keeps Them

Firefox stores logins in your profile directory, under `~/.mozilla/firefox/<profile>/`. Two files matter:

- `logins.json` holds the site, the username and the password, with the last two encrypted.
- `key4.db` (older profiles: `key3.db`) is an SQLite database holding the key that decrypts them.

The encryption is real, but the key sits next to the data. Unless you set a master password, the key itself is protected by an empty password, which means the whole arrangement is obfuscation rather than protection.

The cleanest way to read them is the `firefox_decrypt` script, a small Python program that reads both files and uses the NSS library Firefox itself ships:

```bash
git clone https://github.com/unode/firefox_decrypt.git
cd firefox_decrypt
python firefox_decrypt.py
```

It lists your profiles, asks for the master password if you have one, and prints every saved login. To get machine-readable output for a migration:

```bash
python firefox_decrypt.py --format csv > ~/firefox-logins.csv
```

If you prefer to see the raw pieces, the plain-text half is just JSON:

```bash
python -m json.tool ~/.mozilla/firefox/*.default/logins.json | grep -E 'hostname|encryptedUsername'
```

## Where Chrome Keeps Them

Chrome stores logins in an SQLite database:

```text
~/.config/google-chrome/Default/Login Data
```

The usernames and URLs are in the clear. The passwords are encrypted with a key that Chrome hands to the desktop keyring through libsecret, so on a GNOME or KDE desktop the key lives in your keyring and is unlocked when you log in. Copy the database first, because Chrome keeps it locked while it runs:

```bash
cp ~/.config/google-chrome/Default/Login\ Data /tmp/login-data.db
sqlite3 /tmp/login-data.db 'select origin_url, username_value from logins;'
```

To get the passwords too, you need the keyring entry. With the `libsecret` tools installed:

```bash
secret-tool lookup application chrome
```

prints the key Chrome uses. Decrypting each `password_value` with it is a few lines of Python with `pycryptodome` (AES in CBC mode, a fixed salt and a fixed iteration count that are documented in Chrome's own source); several small scripts on the net do exactly that, and any of them will work. If Chrome was started with `--password-store=basic`, there is no keyring at all and the passwords are stored in a form any script can open directly.

## What This Tells You

Read the two sections again and notice what they have in common. **The passwords are protected against a stranger who steals the disk, and against nobody who can run a command as you.** Any program you launch, any script a website tricks you into running, any colleague who sits at your unlocked desk, can print the lot in a second.

Three consequences:

- Set a master password in Firefox if the machine is ever unattended and unlocked. It is the only thing that turns the obfuscation into encryption.
- Lock the screen. This is the whole defence for Chrome on a running desktop.
- Treat the saved-password store as a convenience with the same security as a text file in your home directory, because that is what it is. A proper password manager, with its own passphrase and its database locked when idle, is a different category of thing.

The commands above are the same ones an attacker would use. Knowing them is the reason to take the three points seriously.
