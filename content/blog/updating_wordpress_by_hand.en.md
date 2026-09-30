+++
title = "Update WordPress by Hand, Because the Button Requires a Hole"
date = 2011-07-10

[taxonomies]
tags = ["wordpress", "security", "self-hosting"]
+++

WordPress offers to update itself with one click, and every security guide tells you to keep it updated. Both are right about the goal. The problem is what the one click requires: the web server must be allowed to overwrite the code it runs. I have argued before that [the web server should not be able to write to the blog's directory at all](@/blog/wordpress-and-unix-security.en.md), and I still think so, which leaves the question of how to update. The answer is by hand, and it takes ten minutes.

## Why the Button Is the Problem

For the automatic updater to work, the user the web server runs as, usually `www-data`, must own or be able to write every PHP file in the installation. That same user runs every request that reaches the site. So a single exploitable plugin, a single upload form with a bug, and the attacker is a user who can rewrite `wp-login.php`. The convenience of the update button and the ability of an attacker to replace your code are the same permission. **You cannot have the first without granting the second.**

The alternative WordPress suggests is to give it FTP credentials so it can write as you. That is a password to your account, stored where PHP can read it, on a machine you are trying to protect. It is not an improvement.

## The Manual Update

The steps assume the blog is at `/var/www/blog`, owned by root, readable by the web server, with only `wp-content/uploads` writable by `www-data`.

**Back up first.** The database and the files, every time, however small the update:

```bash
mysqldump -u blog -p blog > ~/backup/blog-$(date +%F).sql
sudo tar czf ~/backup/blog-files-$(date +%F).tar.gz -C /var/www blog
```

**Fetch and verify the release.** WordPress publishes an MD5 checksum next to each archive; check it before trusting the file:

```bash
cd /tmp
wget https://wordpress.org/latest.tar.gz
wget https://wordpress.org/latest.tar.gz.md5
md5sum -c latest.tar.gz.md5
tar xzf latest.tar.gz
```

**Put the site in maintenance mode.** A file named `.maintenance` in the root makes WordPress show a holding page instead of running half-replaced code:

```bash
echo '<?php $upgrading = time(); ?>' | sudo tee /var/www/blog/.maintenance
```

**Replace the core, and only the core.** Everything of yours lives in `wp-content` and `wp-config.php`; the rest is WordPress's and is replaced wholesale. Delete the old core directories first so that files removed in the new release do not linger:

```bash
cd /var/www/blog
sudo rm -rf wp-admin wp-includes
sudo cp -a /tmp/wordpress/wp-admin /tmp/wordpress/wp-includes .
sudo cp -a /tmp/wordpress/*.php .
sudo rm -f wp-config-sample.php
```

The `cp -a` of `*.php` overwrites the root files (`index.php`, `wp-login.php`, `wp-settings.php`, and the rest) but not `wp-config.php`, because the fresh archive does not contain one. Do not copy `/tmp/wordpress/wp-content`; it would overwrite the default theme and plugins, which is harmless, but it is also the one directory you have reason to be careful with.

**Restore ownership, then run the database step.** The new files are owned by whoever unpacked them; make them root's and readable:

```bash
sudo chown -R root:root /var/www/blog
sudo chown -R www-data:www-data /var/www/blog/wp-content/uploads
sudo find /var/www/blog -type d -exec chmod 755 {} \;
sudo find /var/www/blog -type f -exec chmod 644 {} \;
sudo rm /var/www/blog/.maintenance
```

Now open `/wp-admin/upgrade.php` in a browser. If the release changed the database schema, that page applies the change; if not, it says so. Either way the update is done.

## Plugins and Themes the Same Way

The same reasoning applies to `wp-content/plugins` and `wp-content/themes`, and the same method works: download the archive from the plugin's page, verify what you can, unpack it over the old directory as root, and reset ownership. I described the permission dance for this in [the second security post](@/blog/wordpress-and-unix-security-part-2.en.md). It is slower than the button. It is also the only way to update a plugin without first granting the web server the right to install any code it likes.

## Make It a Script

Everything above is deterministic, so it belongs in a script that takes the archive as its argument, and after the second time you will have one. The parts to keep out of the script are the two that need a human: reading the release notes to see whether anything you rely on changed, and checking the site afterwards. Both take a minute. The permission model you keep in exchange is the difference between a compromised plugin being an incident and being a takeover.

## When to Do It

Immediately for a security release, which WordPress marks as such; within the week for anything else. A blog that is a year behind is a blog whose known holes are documented in public with working exploits attached. Updating by hand does not make that slower to fix. What it removes is the standing invitation to have the fix done for you by someone else.
