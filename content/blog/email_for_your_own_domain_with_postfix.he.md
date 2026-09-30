+++
title = "דואר אלקטרוני לדומיין שלכם עם Postfix"
date = 2011-10-02

[taxonomies]
tags = ["לינוקס", "ניהול-מערכות", "אחסון-עצמי"]
+++

הפעלת דואר לדומיין שלכם מסתורית פחות משהיא נראית, כל עוד אתם שומרים על מטרה צנועה: לקבל דואר הממוען
לדומיין שלכם, למסור אותו למשתמש מקומי אמיתי, ולדחות כל מה שמיועד לאנשים שאינם קיימים. זו התצורה שאני
משתמש בה, עם Postfix כשרת הדואר ו-SpamAssassin המסנן. אני לא אכסה כאן מוניטין שליחה, DKIM ו-SPF,
שהם נושא בפני עצמם; זה צד הקבלה.

## התקנה

```bash
sudo apt-get install postfix spamassassin spamass-milter
```

כשמתקין Postfix שואל, בחרו "Internet Site" ותנו לו את הדומיין שלכם.

## ליבת main.cf

כל ההתנהגות חיה ב-`/etc/postfix/main.cf`. השורות החשובות:

```text
myhostname = mail.example.com
mydomain = example.com
myorigin = $mydomain
mydestination = $myhostname, $mydomain, localhost

# מסירה למשתמשי יוניקס מקומיים.
local_recipient_maps = proxy:unix:passwd.byname $alias_maps

# דחו דואר למשתמשים לא ידועים בדלת, לא אחרי קבלתו.
smtpd_recipient_restrictions =
    permit_mynetworks,
    reject_unauth_destination,
    reject_unknown_recipient_domain
```

ההחלטה החשובה היא הבלוק האחרון. **דחו דואר למשתמשים לא קיימים במהלך שיחת ה-SMTP, לפני שקיבלתם אותו.**
אם אתם מקבלים קודם ומגלים שהמשתמש אינו קיים אחר כך, אתם מחויבים או לשלוח החזרה (מה שעבור דואר זבל
עם שולח מזויף פירושו שאתם שולחים זבל לצד שלישי חף מפשע) או להשמיט אותו בשקט (מה שמאבד דואר אמיתי
שנשלח לשגיאת הקלדה). דחייה מראש גורמת לשרת השולח להתמודד עם הטעות שלו.

## כינויים: תיבת דואר אמיתית אחת מאחורי שמות רבים

אינכם רוצים חשבון יוניקס לכל כתובת. אתם רוצים שכתובות התפקיד הסטנדרטיות ינחתו בתיבה שלכם. לזה נועד
`/etc/aliases`:

```text
root:       mark
postmaster: mark
webmaster:  mark
abuse:      mark
hostmaster: mark
mark:       mark
```

כל הודעה ל-`root@`, ל-`postmaster@`, ל-`webmaster@` ולשאר מנותבת למשתמש הניהולי האמיתי, שאינו שורש.
אחרי עריכת הקובץ אתם חייבים להדר אותו לבסיס הנתונים ש-Postfix באמת קורא:

```bash
sudo newaliases
```

שכחת `newaliases` היא הטעות הקלאסית: אתם עורכים את `/etc/aliases`, שום דבר אינו משתנה, מפני
ש-Postfix קורא את `/etc/aliases.db`, ש-`newaliases` מחולל מחדש. מוסכמת ה-RFC דורשת ש-`postmaster`
ו-`abuse` יעבדו בכל דומיין ששולח דואר, אז קבעו את שני אלה גם אם לא קבעתם דבר אחר.

## SpamAssassin

`spamass-milter` מוסר כל הודעה נכנסת ל-SpamAssassin לפני המסירה. הפעילו אותו ב-`/etc/default/spamassassin`
והצביעו את Postfix אל המילטר ב-`main.cf`:

```text
smtpd_milters = unix:/var/spool/postfix/spamass/spamass.sock
```

SpamAssassin מנקד כל הודעה ומתייג או דוחה אותה מעל סף שאתם קובעים. תנו לו ללמוד מהדואר שלכם עם
`sa-learn` והוא משתפר.

## בדקו זאת

```bash
echo "test" | mail -s "hello" mark@example.com
sudo tail -f /var/log/mail.log
```

צפו ביומן כשההודעה מגיעה, מנוקדת ונמסרת. אחר כך שלחו לכתובת שאינה קיימת וודאו שהיא נדחית בשלב ה-SMTP
ולא מתקבלת ומוחזרת.

זו כל תצורת הקבלה: דומיין שמקבל דואר למשתמשיו האמיתיים, מנתב את חשבונות התפקיד אליכם, ומסובב את
טעויותיהם של זרים בדלת במקום לקבל אותן פנימה ולנקות אחר כך.
