+++
title = "שינוי מערכת התווים של מסד נתונים MySQL"
date = 2010-08-12

[taxonomies]
tags = ["mysql", "בסיסי-נתונים", "linux"]
+++

קורה לי לא פעם שאני שוכח לשנות את מערכת התווים המוגדרת כברירת מחדל של מסד נתונים ל־utf8, ואז
מגלה מאוחר במחזור הפיתוח שהרבה מהשדות שלי מבוססים על מערכות תווים שאינן utf8 (בעיקר latin1).
אז אני נכנס ומשנה כל שדה בתורו באמצעות
`ALTER TABLE [table] MODIFY [field name] [field type] CHARACTER SET [charset]`.
אחרי קצת חפירה מצאתי את התחביר `ALTER TABLE $TABLE CONVERT TO CHARSET [charset]`, שהמיר את כל
השדות בטבלה למערכת תווים מסוימת. חיפשתי תחביר דומה להמרת מסד הנתונים כולו ומצאתי את
`ALTER DATABASE`, שלרוע המזל משנה רק את מערכת התווים ואת סדר המיון המוגדרים כברירת מחדל, אך
אינו משפיע על הטבלאות, השדות או הנתונים הקיימים.

אז הנה סקריפט שחוזר על `ALTER TABLE / CONVERT TO` עבור כל טבלה במסד הנתונים שלכם:

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
