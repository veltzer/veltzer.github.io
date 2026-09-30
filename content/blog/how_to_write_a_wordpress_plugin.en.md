+++
title = "A WordPress Plugin Is One File and Two Functions"
date = 2010-09-12

[taxonomies]
tags = ["wordpress", "php", "programming"]
+++

People are frightened of writing WordPress plugins because the ones they see in the directory are thousands of lines. The mechanism underneath is tiny. A plugin is a PHP file with a comment at the top, and everything it does is done by asking WordPress to call your functions at named moments. Here is the whole thing, built up from nothing.

## The Header

Create a directory `wp-content/plugins/hello-tags/` and inside it a file `hello-tags.php`. WordPress recognises a plugin by the comment block at the top of that file, nothing else:

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

Save it and it already appears under Plugins in the admin screen, ready to activate. It does nothing yet. The `ABSPATH` check stops the file from doing anything if someone requests it directly from the web instead of through WordPress.

## Actions: Do Something at a Moment

WordPress runs through a long sequence of named moments while building a page, and `add_action` attaches your function to one of them. To add a line to the footer of every page:

```php
function hello_tags_footer() {
    echo '<p class="hello-tags">Rendered by Hello Tags.</p>';
}
add_action('wp_footer', 'hello_tags_footer');
```

The first argument is the name of the moment, the second is your function. `wp_footer` fires where the theme calls `wp_footer()`, which every decent theme does just before `</body>`. Other moments you will use constantly: `init` (WordPress is loaded, nothing is output yet), `wp_enqueue_scripts` (the right place to add stylesheets and scripts), `admin_menu` (add a settings page).

## Filters: Change Something on Its Way Through

`add_filter` is the same idea, except your function receives a value, changes it, and must return it. To append the post's tags to the end of every post body:

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

Forgetting to `return` the value is the classic filter bug: the post body silently disappears. The filter names you will meet most are `the_content`, `the_title`, `the_excerpt`, and `wp_title`.

## A Shortcode

A shortcode is a filter with a friendlier face. It lets an author type `[hello_tags]` into a post and have your function replace it:

```php
function hello_tags_shortcode($atts) {
    $atts = shortcode_atts(array('prefix' => 'Tags: '), $atts);
    return get_the_tag_list('<span>' . esc_html($atts['prefix']), ', ', '</span>');
}
add_shortcode('hello_tags', 'hello_tags_shortcode');
```

`shortcode_atts` merges what the author typed, such as `[hello_tags prefix="Filed under: "]`, with your defaults. Always escape anything that came from a human before printing it; `esc_html` is the minimum.

## Activation and Deactivation

If your plugin needs to set something up once, register an activation hook. Here it stores a default option; on deactivation it removes it:

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

The options table is where plugin settings live. `get_option('hello_tags_enabled')` reads it back anywhere.

## Habits Worth Forming From the First Line

- **Prefix every function and option name.** Every plugin on the site shares one PHP namespace. Two plugins that both define `footer()` take the whole site down with a fatal error.
- **Never print, always return, inside a filter.** Printing from a filter puts text at the top of the page instead of where it belongs.
- **Escape on output.** `esc_html`, `esc_attr`, `esc_url`. WordPress does not do it for you.
- **Keep the file read-only for the web server.** A plugin that the web server can write to is a plugin an attacker can rewrite. I have written about [what that looks like in practice](@/blog/wordpress-and-unix-security.en.md).

That is the complete mechanism. Every large plugin you have installed is this pattern, repeated: a header, functions attached to moments, values changed on their way through. The size comes from doing many things, not from any one of them being hard.
