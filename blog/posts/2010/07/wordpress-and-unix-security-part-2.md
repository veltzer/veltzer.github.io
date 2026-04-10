---
tags:
  - wordpress
  - security
  - linux
date: 2010-07-09
---

# WordPress and UNIX security (part 2)

In an effort to secure my blog I once again did battle with the mighty Word press. It seems that you can run a perfectly healthy blog with no write permissions by the HTTP server (usually `www-data`) to your service directory.

What do I suggest? Change owner ship to root on your blog area. When you know that you need to upload stuff to Word press then open the permissions on the relevant folders. This happens when you want to add or remove plug-ins, upload media, themes etc. After the relevant operation clamp down on security again. There are plugins (like xLanguage) that write all kinds of junk log files into the upload folder as part of their operation. Obviously you cannot use these if you want better security.

Advantages: better security.
Disadvantages: A little discomfort and the need to write very simple short script to do the chmod for you. The Inability to use certain brain dead plug-ins.
