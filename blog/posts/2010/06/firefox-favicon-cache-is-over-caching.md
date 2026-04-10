---
tags:
  - firefox
  - browser
  - web
date: 2010-06-25
---

# Firefox favicon cache is over caching

I've recently tried setting some sites icon to appear as the small icon you see at the tab you are browsing it. This icon is called `favicon.ico` and is located in your servers root directory which resides in `/var/www` on standard systems. When changing this icon and reloading the page in Chrome the icon got updated promptly. No such luck with Firefox. The only way I found to do it is to go to the Firefox cache which is at `~/.mozilla/firefox/[some instance of firefox]/Cache` and remove the icon. The problem is that the cache folder shows files whose names are hash keys of the cache which means that you need to find the file. Usually something like `file * | grep icon` can help. If you know the exact size of the icon you are looking for this could help also or if you have the actual icon file you are trying to erase from the cache you can just explicitly run a search for it using `cmp(1)`.

Addendum: A much easier way is just to point your browser at the favicon URL which should update it's cache just for this URL. In Firefox this worked even without browser restart.
In addition to all of the above in Firefox the bookmarks tool bar could show a different favicon than the tab. For this you can install "Bookmark Favicon Changer" as an extension and
set the icon yourself.
