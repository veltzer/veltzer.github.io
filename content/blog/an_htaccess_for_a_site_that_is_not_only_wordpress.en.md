+++
title = "WordPress Wants to Own Your Whole Site, and Your .htaccess Should Say No"
date = 2011-04-03

[taxonomies]
tags = ["wordpress", "sysadmin", "self-hosting"]
+++

The `.htaccess` that WordPress writes for itself assumes it is the only thing on the domain. Every request that does not match an existing file is handed to `index.php`, and WordPress decides what it means. If your site is also a photo gallery, a few static pages, a couple of scripts you wrote yourself, and a blog, that assumption is wrong, and the symptoms are strange: a typo in a URL to your gallery produces a WordPress "not found" page in the blog's theme, and a directory you meant to protect answers with a blog post. Here is the file I run instead, block by block.

## The Layout It Assumes

```text
/var/www/site/            document root
    .htaccess             this file
    index.html            the front page, static
    gallery/              a photo gallery, its own application
    scripts/              my own PHP scripts
    blog/                 WordPress, installed in a subdirectory
    blog/.htaccess        WordPress's own file, left alone
```

The point of the layout is that WordPress lives in `blog/` and its rules live in `blog/.htaccess`, where they can only affect URLs under `/blog/`. The root file handles everything else.

## The Root File

```apache
# Nothing in this file mentions WordPress. That is deliberate.

Options -Indexes
ServerSignature Off

# Deny access to files that should never be served.
<FilesMatch "^(\.htaccess|\.htpasswd|\.git.*|.*\.(bak|old|sql|log))$">
    Order allow,deny
    Deny from all
</FilesMatch>

# The blog moved from the root to /blog/ in 2010; keep the old links alive.
RewriteEngine On
RewriteRule ^([0-9]{4})/([0-9]{2})/(.*)$ /blog/$1/$2/$3 [R=301,L]
RewriteRule ^feed/?$ /blog/feed/ [R=301,L]

# Protect the scripts directory with a password.
<IfModule mod_auth.c>
</IfModule>

# Sensible defaults for static content.
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType text/css "access plus 1 week"
</IfModule>

AddDefaultCharset UTF-8
```

## Block by Block

**No directory listings, no version banner.** `Options -Indexes` stops Apache from showing the contents of any directory that lacks an index file, which on a mixed site is most of them. `ServerSignature Off` removes the Apache version from error pages. Neither has anything to do with WordPress, which is the point: these apply to the whole site, so they belong at the root.

**Files that must never be served.** Editors leave `.bak` files behind, database dumps get left in the web root, and a `.git` directory at the root of a site is a complete copy of the source and its history for anyone who asks for it. The `FilesMatch` block denies them all wherever they are. WordPress's own file does not do this for the directories outside `blog/`, because it does not know they exist.

**Redirects for old URLs.** When the blog was at the root, its posts lived at `/2009/07/some-title/`. Those links are in other people's pages and in search engines, and a URL that once worked should keep working. The two rewrite rules send the old shapes to their new home under `/blog/` with a permanent redirect. This is the one place the root file knows the blog exists, and it knows only where it moved to.

**The scripts directory.** The empty `mod_auth` block is a placeholder: the actual password protection lives in `scripts/.htaccess`, where a `Require valid-user` and an `AuthUserFile` outside the web root belong. I keep the stub here so that anyone reading the root file sees that the directory is protected somewhere.

**Caching and charset.** Long expiry for images, a week for stylesheets, and a default charset so that a plain text file with Hebrew in it is not shown as garbage. Again, site-wide, so root.

## What Is Missing, on Purpose

There is no `RewriteRule . /index.php` here. That line is what makes WordPress the owner of every unknown URL, and it stays in `blog/.htaccess`, where WordPress wrote it and where it only catches URLs under `/blog/`. A misspelled gallery URL now gets Apache's own 404, as it should, and a request for `/scripts/` gets a password prompt instead of a blog post.

There is also nothing that touches PHP settings. Those are per-application and belong next to the application; raising the upload limit for the blog is [a separate exercise](@/blog/increasing_wordpress_upload_size.en.md) with its own file.

## Why This Matters Beyond Tidiness

A rewrite rule that catches everything is a security decision as much as a routing one. Every request your other applications do not answer becomes a request WordPress answers, with WordPress's attack surface, running WordPress's code, in a directory you may have secured on the assumption that only blog URLs reach it. Scoping the rules to the subdirectory means the exposure of each application is the exposure of its own URLs, and nothing more. I have written about [locking down the WordPress directory itself](@/blog/wordpress-and-unix-security.en.md); this is the outer layer of the same idea.
