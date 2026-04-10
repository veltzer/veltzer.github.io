---
tags:
  - wordpress
  - security
  - linux
date: 2010-06-26
---

# Wordpress and UNIX security

Here is what I found the hard way. Sometime you want Wordpress to install plugins, themes and all and do not want to pass through an ssh or ftp connection in order to achieve this. Maybe you have your own machine and do not want to run or configure an ssh or ftp server (which is my situation). In that case you can choose to either install plugins and themes by hand (just unzip them to $WORDPRESS/wp-content/[plugins|themes]) or you can give wordpress permissions so it can do it for you. The disadvantage of giving Wordpress permissions is ofcourse security since any one hacking into your server could have write access to the wordpress files themselves. In order to avoid this you can keep all your wordpress files owned as root.root (maximum security) and only change permissions for the duration of the installation of the plugin or theme.

Here is how to do this for a completely safe install:

	- Turn off your world access to your web server. This can be done by bringing down your external network link by `ifdown eth0`. This step is only necessary if you are a security freak.
	- `chown -R [webuser].[webgroup] [wordpress]/wp-content/{plugins,themes}`. Substitute webuser and webgroup for your web servers user and group. These are usually www-data on Debian based systems or could be gotten from ps -ef.
        - Now perform your installation of plugins or themes from the local machine or from a remote machine if you have not followed the security step above.
        - `chown -R root.root [wordpress]/wp-content/{plugins,themes}`. This will clamp down on security once again.

Please note that some weird Wordpress plugins write to the web folder due to their regular operation. If you have such plugins and are worried about security then I urge you to dump them and find substitute plugins. If you cannot dump them then you probably cannot use any sane security practice for your blog.
