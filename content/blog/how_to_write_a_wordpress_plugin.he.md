+++
title = "תוסף וורדפרס הוא קובץ אחד ושתי פונקציות"
date = 2010-09-12

[taxonomies]
tags = ["וורדפרס", "php", "תכנות"]
+++

אנשים חוששים לכתוב תוספים לוורדפרס מפני שאלה שהם רואים במאגר הם באורך אלפי שורות. המנגנון שמתחת
זעיר. תוסף הוא קובץ PHP עם הערה בראשו, וכל מה שהוא עושה נעשה בכך שהוא מבקש מוורדפרס לקרוא
לפונקציות שלכם ברגעים בעלי שם. הנה כל העניין, בנוי מאפס.

## הכותרת

צרו ספרייה `wp-content/plugins/hello-tags/` ובתוכה קובץ `hello-tags.php`. וורדפרס מזהה תוסף לפי
בלוק ההערה בראש הקובץ הזה, ולא לפי שום דבר אחר:

```php
<?php
/*
Plugin Name: Hello Tags
Description: Shows how little a plugin needs.
Version: 0.1
Author: Mark Veltzer
License: GPL2
*/

if (!defined('ABSPATH')) {
    exit;
}
```

שמרו אותו והוא כבר מופיע תחת Plugins במסך הניהול, מוכן להפעלה. הוא עדיין אינו עושה דבר. הבדיקה של
`ABSPATH` מונעת מהקובץ לעשות דבר אם מישהו מבקש אותו ישירות מהרשת ולא דרך וורדפרס.

## פעולות: לעשות משהו ברגע מסוים

וורדפרס עוברת רצף ארוך של רגעים בעלי שם בזמן בניית עמוד, ו-`add_action` מצמידה את הפונקציה שלכם
לאחד מהם. כדי להוסיף שורה לכותרת התחתונה של כל עמוד:

```php
function hello_tags_footer() {
    echo '<p class="hello-tags">Rendered by Hello Tags.</p>';
}
add_action('wp_footer', 'hello_tags_footer');
```

הארגומנט הראשון הוא שם הרגע, השני הוא הפונקציה שלכם. `wp_footer` מופעל במקום שבו ערכת העיצוב
קוראת ל-`wp_footer()`, מה שכל ערכה הגונה עושה ממש לפני `</body>`. רגעים אחרים שתשתמשו בהם כל
הזמן: `init` (וורדפרס נטענה, עדיין לא נפלט דבר), `wp_enqueue_scripts` (המקום הנכון להוסיף גיליונות
סגנון וסקריפטים), `admin_menu` (הוספת עמוד הגדרות).

## מסננים: לשנות משהו בדרכו

`add_filter` הוא אותו רעיון, אלא שהפונקציה שלכם מקבלת ערך, משנה אותו, וחייבת להחזיר אותו. כדי
לצרף את התגיות של הפוסט לסוף כל גוף פוסט:

```php
function hello_tags_append($content) {
    if (!is_single()) {
        return $content;
    }
    $tags = get_the_tag_list('<p>Tags: ', ', ', '</p>');
    return $content . $tags;
}
add_filter('the_content', 'hello_tags_append');
```

לשכוח לעשות `return` לערך הוא באג המסננים הקלאסי: גוף הפוסט נעלם בשקט. שמות המסננים שתפגשו הכי
הרבה הם `the_content`, `the_title`, `the_excerpt` ו-`wp_title`.

## קוד קצר

קוד קצר (shortcode) הוא מסנן עם פנים ידידותיות יותר. הוא מאפשר למחבר להקליד `[hello_tags]` בתוך
פוסט ולגרום לפונקציה שלכם להחליף אותו:

```php
function hello_tags_shortcode($atts) {
    $atts = shortcode_atts(array('prefix' => 'Tags: '), $atts);
    return get_the_tag_list('<span>' . esc_html($atts['prefix']), ', ', '</span>');
}
add_shortcode('hello_tags', 'hello_tags_shortcode');
```

`shortcode_atts` ממזגת את מה שהמחבר הקליד, למשל `[hello_tags prefix="Filed under: "]`, עם ברירות
המחדל שלכם. תמיד בצעו escape לכל דבר שהגיע מבן אדם לפני שאתם מדפיסים אותו; `esc_html` הוא
המינימום.

## הפעלה וכיבוי

אם התוסף שלכם צריך להגדיר משהו פעם אחת, רשמו hook להפעלה. כאן הוא שומר אופציית ברירת מחדל; בכיבוי
הוא מסיר אותה:

```php
function hello_tags_activate() {
    add_option('hello_tags_enabled', 1);
}
register_activation_hook(__FILE__, 'hello_tags_activate');

function hello_tags_deactivate() {
    delete_option('hello_tags_enabled');
}
register_deactivation_hook(__FILE__, 'hello_tags_deactivate');
```

טבלת האופציות היא המקום שבו חיות הגדרות התוספים. `get_option('hello_tags_enabled')` קוראת אותה
בחזרה בכל מקום.

## הרגלים שכדאי לסגל מהשורה הראשונה

- **הוסיפו קידומת לכל שם פונקציה ואופציה.** כל התוספים באתר משתפים מרחב שמות PHP אחד. שני תוספים
  ששניהם מגדירים `footer()` מפילים את כל האתר בשגיאה פטאלית.
- **לעולם אל תדפיסו, תמיד החזירו, בתוך מסנן.** הדפסה מתוך מסנן שמה טקסט בראש העמוד במקום במקום שהוא
  שייך אליו.
- **בצעו escape בפלט.** `esc_html`, `esc_attr`, `esc_url`. וורדפרס אינה עושה זאת בשבילכם.
- **השאירו את הקובץ לקריאה בלבד עבור שרת הרשת.** תוסף ששרת הרשת יכול לכתוב אליו הוא תוסף שתוקף יכול
  לשכתב. כתבתי על [איך זה נראה בפועל](@/blog/wordpress-and-unix-security.he.md).

זהו המנגנון השלם. כל תוסף גדול שהתקנתם הוא התבנית הזו, חוזרת על עצמה: כותרת, פונקציות מוצמדות
לרגעים, ערכים משתנים בדרכם. הגודל בא מלעשות דברים רבים, לא מכך שאחד מהם קשה.
