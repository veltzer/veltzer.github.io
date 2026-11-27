+++
date = 2010-08-12
description = "ALTER DATABASE меняет только кодировку по умолчанию, но не существующие таблицы. Короткий скрипт на bash вместо этого выполняет ALTER TABLE CONVERT TO CHARSET для каждой таблицы."
slug = "mysql-database-character-set"
title = "Смена кодировки базы данных MySQL"

[taxonomies]
tags = ["mysql", "базы-данных", "linux"]
+++

Часто бывает, что я забываю поменять кодировку базы данных по умолчанию на utf8 и поздно, уже на поздней стадии разработки, обнаруживаю, что многие мои поля основаны на кодировках, отличных от utf8 (в основном latin1). Тогда я иду и изменяю каждое поле по очереди командой `ALTER TABLE [table] MODIFY [field name] [field type] CHARACTER SET [charset]`. Покопавшись, я нашёл синтаксис `ALTER TABLE $TABLE CONVERT TO CHARSET [charset]`, который преобразует все поля таблицы в заданную кодировку. Я поискал аналогичный синтаксис для преобразования всей базы данных и нашёл `ALTER DATABASE`, который, к сожалению, меняет лишь кодировку и правило сортировки по умолчанию, но не затрагивает существующие таблицы, поля и данные.

Вот скрипт, который повторяет `ALTER TABLE / CONVERT TO` для каждой таблицы вашей базы данных:

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
