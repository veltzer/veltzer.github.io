+++
title = "Raising the WordPress Upload Limit Means Finding Which of Four Limits You Hit"
date = 2011-02-20

[taxonomies]
tags = ["wordpress", "php", "sysadmin"]
+++

"The uploaded file exceeds the upload_max_filesize directive in php.ini." Every WordPress administrator meets this message the first time someone tries to upload a video. The fix is a one-line setting. The trouble is that there are four places the setting can live, they override each other, and WordPress adds a fifth limit of its own on multisite installations. Here is how to find out which one is stopping you and how to change it.

## First, See What You Have

Do not guess. Put a file called `info.php` in the web root with one line in it:

```php
<?php phpinfo();
```

Open it in a browser and search the page for `upload_max_filesize`. The table shows two columns, local value and master value. The master value is what the system `php.ini` says; the local value is what applies to this directory after every override. Note also `post_max_size`, `memory_limit`, and `max_execution_time`, because an upload has to fit through all of them:

- `upload_max_filesize` is the size of one uploaded file.
- `post_max_size` is the size of the whole request, so it must be at least as large as the file, and a little more.
- `memory_limit` should be larger than `post_max_size`, or PHP runs out of memory handling the request.
- `max_execution_time` and `max_input_time` decide whether a slow upload is cut off before it finishes.

Delete `info.php` when you are done. It tells the world your exact PHP configuration, and there is no reason to publish that.

## Option One: The System php.ini

If you own the server, the honest fix is the system file. On Debian and Ubuntu with Apache it is `/etc/php5/apache2/php.ini`; the `phpinfo` page names the exact path under "Loaded Configuration File". Change these lines:

```ini
upload_max_filesize = 64M
post_max_size = 72M
memory_limit = 128M
max_execution_time = 300
max_input_time = 300
```

and restart the web server:

```bash
sudo /etc/init.d/apache2 restart
```

This applies to every site on the machine, which is either exactly what you want or exactly what you do not.

## Option Two: A Local php.ini

On shared hosting you cannot touch the system file, but many hosts run PHP as CGI or FastCGI, and then PHP reads a `php.ini` from the directory of the script being run. Put a file with just the changed lines in the WordPress root:

```ini
upload_max_filesize = 64M
post_max_size = 72M
memory_limit = 128M
```

Two traps. First, the file applies to the directory it is in, not to subdirectories; the upload is actually handled by `wp-admin/async-upload.php`, so you may need a copy in `wp-admin/` too. Second, on some hosts the file must be called `php5.ini` or `.user.ini`. The `phpinfo` page tells you whether your change took: if the local value did not move, PHP is not reading your file.

## Option Three: .htaccess

If PHP runs as an Apache module rather than CGI, a local `php.ini` is ignored and the equivalent is Apache directives in `.htaccess`:

```apache
php_value upload_max_filesize 64M
php_value post_max_size 72M
php_value memory_limit 128M
php_value max_execution_time 300
php_value max_input_time 300
```

If PHP is *not* running as a module, these lines cause a 500 error on the whole site, because Apache does not know the `php_value` directive. That is the quick way to find out which mode you are in: try it, and if the site dies, remove the lines and use option two. Only one of options two and three will work on a given host, never both.

## Option Four: WordPress Multisite

You have raised every PHP limit, `phpinfo` confirms it, and uploads still fail at a smaller size. Then you are running multisite, and the network has its own ceiling. It lives in the network admin under Settings, as "Max upload file size", in kilobytes, with a default of 1500. It also lists the allowed file types, which is why a `.mkv` may be refused even when its size is fine. Raise both there. There is additionally a per-site space quota on the same page, which counts total uploads rather than a single file, and it stops uploads with a different and less helpful message when a site fills up.

## The Order to Try

Check `phpinfo` first, so you know whether the limit is PHP's or WordPress's. If it is PHP's, use the system file when you can, a local `php.ini` when PHP is CGI, and `.htaccess` when it is a module. If the PHP limits are already large enough, the answer is on the network settings page. Doing them in this order takes ten minutes; doing them in a random order is how people spend an afternoon on a one-line change.
