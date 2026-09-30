+++
title = "ערכת עיצוב לוורדפרס היא שני קבצים ולולאה"
date = 2010-10-24

[taxonomies]
tags = ["וורדפרס", "php", "תכנות"]
+++

ערכות העיצוב שאנשים מורידים גדולות מפני שהן מנסות להיראות כמו הכול בבת אחת. המינימום שוורדפרס תקבל
כערכת עיצוב הוא שני קבצים, והבנת השניים האלה עושה כל ערכה גדולה לקריאה. הנה ערכה שנבנתה מהיסוד, עם
הרעיון האחד שכל דבר אחר בערכה בנוי עליו.

## שני הקבצים הנדרשים

צרו `wp-content/themes/bare/` ושימו בה `style.css` שמתחיל בבלוק הערה. כמו בתוספים, ההערה היא מה
שוורדפרס קוראת; שאר הקובץ הוא CSS רגיל:

```css
/*
Theme Name: Bare
Description: The smallest theme that works.
Author: Mark Veltzer
Version: 0.1
License: GPL2
*/

body { max-width: 40em; margin: 2em auto; font-family: serif; }
```

הקובץ השני הוא `index.php`, והוא הגיבוי לכל עמוד שהאתר יכול להציג. עם שני הקבצים האלה בלבד הערכה
מופיעה תחת Appearance וניתן להפעילה.

## הלולאה

כל מה שערכת עיצוב עושה סובב סביב מבנה אחד. לפני שהתבנית שלכם רצה, וורדפרס כבר חישבה לאילו פוסטים
הבקשה הזו מיועדת: פוסט אחד, עמוד, העשרה האחרונים, פוסטים של תגית, פוסטים של חודש. תפקידכם הוא
לעבור עליהם. המעבר הזה נקרא הלולאה, והנה היא:

```php
<?php get_header(); ?>

<?php if (have_posts()) : ?>
    <?php while (have_posts()) : the_post(); ?>
        <article>
            <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
            <p><?php the_time('Y-m-d'); ?></p>
            <?php the_content(); ?>
        </article>
    <?php endwhile; ?>
<?php else : ?>
    <p>Nothing here.</p>
<?php endif; ?>

<?php get_footer(); ?>
```

`have_posts()` שואלת אם נותר משהו, `the_post()` טוענת את הבא, וכל פונקציה שמתחילה ב-`the_` מדפיסה
משהו על הפוסט שטעון כרגע. זהו המודל כולו. ערכה שמציגה פוסט יחיד וערכה שמציגה ארכיון מריצות את אותה
לולאה; ההבדל הוא רק אילו פוסטים וורדפרס הגישה לה.

## כותרת עליונה ותחתונה

`get_header()` מכלילה את `header.php` ו-`get_footer()` מכלילה את `footer.php`. שמירתן בנפרד מאפשרת
לכל תבנית לשתף אותן:

```php
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <title><?php wp_title('|', true, 'right'); bloginfo('name'); ?></title>
    <link rel="stylesheet" href="<?php bloginfo('stylesheet_url'); ?>">
    <?php wp_head(); ?>
</head>
<body>
<h1><a href="<?php echo home_url(); ?>"><?php bloginfo('name'); ?></a></h1>
```

והכותרת התחתונה:

```php
<?php wp_footer(); ?>
</body>
</html>
```

`wp_head()` ו-`wp_footer()` אינן קישוט. תוספים נצמדים לרגעים האלה כדי להכניס את הסקריפטים וגיליונות
הסגנון שלהם, ולכן ערכה שמשמיטה אותם שוברת מחצית מהתוספים באתר.

## היררכיית התבניות

עכשיו יש לכם ערכת עיצוב, והיא מציגה הכול באמצעות `index.php`. כדי לטפל בבקשות מסוימות אחרת, הוסיפו
קובץ בשם הנכון ווורדפרס תבחר בו על פני `index.php` אוטומטית:

- `single.php` לפוסט אחד, `page.php` לעמוד סטטי אחד
- `archive.php` לארכיוני תאריך, קטגוריה ותגית; `category.php` ו-`tag.php` כשרוצים להפריד ביניהם
- `home.php` לרשימת העמוד הראשי, `front-page.php` כשהעמוד הראשי הוא עמוד סטטי
- `search.php` ו-`404.php` למה ששמם אומר

כל אחד מהם מכיל את אותה לולאה. ההיררכיה היא מוסכמת שמות, לא מודל תכנות, ואפשר להוסיף קבצים אחד
אחד לפי הצורך.

## functions.php

אם בספריית הערכה יש `functions.php`, וורדפרס טוענת אותו לפני כל דבר אחר, והוא מתנהג בדיוק כמו תוסף
שמצורף לערכה. השתמשו בו כדי להפעיל תכונות ולטעון גיליונות סגנון כמו שצריך:

```php
<?php
function bare_setup() {
    add_theme_support('post-thumbnails');
    add_theme_support('automatic-feed-links');
    register_nav_menu('main', 'Main menu');
}
add_action('after_setup_theme', 'bare_setup');

function bare_styles() {
    wp_enqueue_style('bare', get_stylesheet_uri());
}
add_action('wp_enqueue_scripts', 'bare_styles');
```

כשגיליון הסגנון נטען כך אפשר להשמיט את שורת ה-`<link>` מ-`header.php`; `wp_head()` מדפיסה אותה. כל
דבר שמשנה התנהגות ולא מראה שייך לתוסף, לא לכאן, מפני שהפונקציות של ערכה נעלמות ברגע שמחליפים ערכה.

## מאיפה בא הגודל

ערכה מסחרית היא השלד הזה ועוד עמוד הגדרות, תריסר קובצי תבנית, אזורי ווידג'טים והרבה מאוד CSS. דבר
מזה אינו משנה את המודל: וורדפרס בוחרת את הפוסטים, היררכיית התבניות בוחרת את הקובץ, הקובץ מריץ את
הלולאה, ופונקציות ה-`the_` מדפיסות. קראו כל ערכה מתוך המחשבה הזו והיא מפסיקה להיות מאיימת.

הגישו את הספרייה כולה לקריאה בלבד לשרת הרשת, כמו כל דבר אחר תחת `wp-content`; תיארתי מדוע
ב[פוסט מוקדם יותר](@/blog/wordpress-and-unix-security-part-2.he.md).
