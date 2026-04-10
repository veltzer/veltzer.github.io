---
tags:
  - mysql
  - database
  - linux
date: 2010-08-12
---

# Altering the character set of a MySQL database

It happens often that I forget to change the default character set of a database to utf8 and so find out late in the development cycle that many of my fields are based on non utf8 character sets (mostly latin1). Then I go in and modify each field in turn using `ALTER TABLE [table] MODIFY [field name] [field type] CHARACTER SET [charset]`. After some digging I found the `ALTER TABLE $TABLE CONVERT TO CHARSET [charset]` syntax which converted all fields in a table to a certain character set. I looked for a similar syntax to convert the entire database and found `ALTER DATABASE` which, unfortunately, only changes the default character set and collation but does not affect the existing tables, fields or data.

So here is a script that repeats `ALTER TABLE / CONVERT TO` on each table in your database:

```bash
#!/bin/bash

# parameters...
USER='[your db user name]'
PASS='[your db password]'
DB='[your db]'
CHARSET='[character set (utf8?)]'
COLLATION='[collation (utf8_unicode_ci?)]'

# here we go...
QUERY="SELECT table_name FROM information_schema.TABLES WHERE table_schema = '$DB';"
TABLES=$(mysql -u $USER --password=$PASS $DB --batch --skip-column-names --execute="$QUERY")
for TABLE in $TABLES; do
        echo "ALTER TABLE $TABLE ......"
        mysql -u $USER --password=$PASS $DB -e "ALTER TABLE $TABLE CONVERT TO CHARSET $CHARSET"
        #mysql -u $USER --password=$PASS $DB -e "ALTER TABLE $TABLE CONVERT TO CHARSET $CHARSET COLLATE $COLLATION"
done
```
