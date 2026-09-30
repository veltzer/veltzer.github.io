+++
title = "Serving a File Out of a MySQL Blob, and Why You Probably Should Not"
date = 2010-06-27

[taxonomies]
tags = ["php", "mysql", "programming"]
+++

Sooner or later a web application has to store files: images uploaded by users, PDFs, attachments. There are two places they can go, the filesystem or the database, and the database is the one people reach for when they want everything in one place, backed up by one command, protected by one set of permissions. MySQL has a `BLOB` type for exactly this. Here is how to serve a file out of it correctly, and then an argument for not doing it.

## The Table

```sql
CREATE TABLE files (
    id        INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    mime      VARCHAR(127) NOT NULL,
    size      INT UNSIGNED NOT NULL,
    modified  DATETIME NOT NULL,
    data      LONGBLOB NOT NULL
);
```

Store the MIME type and the size alongside the bytes. Working them out at serving time is possible but wasteful, and the size is needed for a header before the data is read. `LONGBLOB` holds up to four gigabytes; `BLOB` alone stops at 64 kilobytes, which is the first surprise everyone hits.

## The Script

```php
<?php
$id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
if ($id <= 0) {
    header('HTTP/1.1 404 Not Found');
    exit;
}

$db = new PDO('mysql:host=localhost;dbname=site;charset=utf8', 'user', 'password');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$stmt = $db->prepare('SELECT name, mime, size, modified, data FROM files WHERE id = ?');
$stmt->execute(array($id));
$row = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$row) {
    header('HTTP/1.1 404 Not Found');
    exit;
}

$etag     = '"' . md5($id . $row['modified'] . $row['size']) . '"';
$modified = gmdate('D, d M Y H:i:s', strtotime($row['modified'])) . ' GMT';

if ((isset($_SERVER['HTTP_IF_NONE_MATCH']) && $_SERVER['HTTP_IF_NONE_MATCH'] === $etag) ||
    (isset($_SERVER['HTTP_IF_MODIFIED_SINCE']) && $_SERVER['HTTP_IF_MODIFIED_SINCE'] === $modified)) {
    header('HTTP/1.1 304 Not Modified');
    exit;
}

header('Content-Type: ' . $row['mime']);
header('Content-Length: ' . $row['size']);
header('Content-Disposition: inline; filename="' . addslashes($row['name']) . '"');
header('Last-Modified: ' . $modified);
header('ETag: ' . $etag);
header('Cache-Control: public, max-age=86400');
echo $row['data'];
```

Four things in this script matter and are routinely left out.

**Cast the id.** `(int)` turns anything hostile in the query string into a number. The prepared statement would protect you anyway, but a request for `id=abc` should be a 404, not a query.

**Send the real content type.** Without it the browser guesses, and its guess for a PDF is sometimes a download dialogue and sometimes a screen of garbage. The type was recorded at upload; use it.

**Send the length.** Browsers show progress and can reuse the connection only when they know how much is coming. You have the size in the table; there is no reason to make them wait for the connection to close.

**Support conditional requests.** Files are the most cacheable thing a site serves. Emitting `Last-Modified` and `ETag`, and answering a repeat request with a `304`, means the second view costs a single small query instead of moving the whole blob out of the database again.

Note also what is not in the script: no `ob_start()`, no output before the headers, and no closing `?>` tag, which would risk sending a newline after the bytes.

## Why the Filesystem Is Usually Better

Now the argument against. Everything above works, and I have run it in production. It is still, in most cases, the wrong design.

A file in the database passes through the database's memory, the wire protocol, PHP's memory, and the web server before it reaches the client. A file on disk is handed to the kernel with `sendfile()` by a web server that has spent a decade being optimised for exactly that, and PHP is never invoked. For anything larger than a thumbnail the difference is not a few percent; it is the difference between a site that serves images and a site whose database is busy serving images.

Backups get worse, not better. A database dump that includes gigabytes of blobs takes correspondingly longer to make, to transfer and to restore, and a restore of the small important data now has to drag the large unimportant data with it. Replication carries every byte of every upload to every replica.

And the operational tools do not fit. You cannot `ls` a blob column, `rsync` it, or hand a directory to a CDN.

The right pattern is the one every large system ended up with: **store the bytes on disk under a name derived from the record, and store only the metadata in the database.** The table above loses its `data` column and gains a `path`. The script above becomes a permission check followed by `X-Sendfile` or a redirect. Everything else, including the caching headers, stays the same.

Keep the blob approach for the cases it genuinely suits: files that are tiny, files that must be transactional with the row they belong to, or a deployment where you truly have one process and no filesystem to speak of. Otherwise the database is for data about the files, and the disk is for the files.
