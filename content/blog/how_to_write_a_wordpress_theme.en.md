+++
title = "A WordPress Theme Is Two Files and a Loop"
date = 2010-10-24

[taxonomies]
tags = ["wordpress", "php", "programming"]
+++

The themes people download are large because they are trying to look like everything at once. The minimum WordPress will accept as a theme is two files, and understanding those two makes every large theme readable. Here is a theme built from the ground up, with the one idea that everything else in a theme is built on.

## The Two Required Files

Create `wp-content/themes/bare/` and put in it a `style.css` that starts with a comment block. As with plugins, the comment is what WordPress reads; the rest of the file is ordinary CSS:

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

The second file is `index.php`, and it is the fallback for every page the site can show. With only these two files present, the theme appears under Appearance and can be activated.

## The Loop

Everything a theme does revolves around one construct. Before your template runs, WordPress has already worked out which posts this request is for: one post, a page, the latest ten, a tag's worth, a month's worth. Your job is to walk through them. That walk is called the loop, and this is it:

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

`have_posts()` asks whether anything is left, `the_post()` loads the next one, and every function beginning with `the_` prints something about the post that is currently loaded. That is the entire model. A theme that shows a single post and a theme that shows an archive run the same loop; the difference is only which posts WordPress handed it.

## Header and Footer

`get_header()` includes `header.php` and `get_footer()` includes `footer.php`. Keeping them separate lets every template share them:

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

and the footer:

```php
<?php wp_footer(); ?>
</body>
</html>
```

`wp_head()` and `wp_footer()` are not decoration. Plugins attach to those moments to insert their scripts and stylesheets, so a theme that omits them breaks half the plugins on the site.

## The Template Hierarchy

You now have a theme, and it shows everything with `index.php`. To treat some requests differently, add a file with the right name and WordPress picks it over `index.php` automatically:

- `single.php` for one post, `page.php` for one static page
- `archive.php` for date, category and tag archives; `category.php` and `tag.php` when you want them apart
- `home.php` for the front page listing, `front-page.php` when the front page is a static page
- `search.php` and `404.php` for what their names say

Each of them contains the same loop. The hierarchy is a naming convention, not a programming model, and you can add files one at a time as you need them.

## functions.php

If the theme directory has a `functions.php`, WordPress loads it before anything else, and it behaves exactly like a plugin that is bundled with the theme. Use it to turn on features and to load stylesheets properly:

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

With the stylesheet enqueued this way you can drop the `<link>` line from `header.php`; `wp_head()` prints it. Anything that changes behaviour rather than appearance belongs in a plugin, not here, because a theme's functions vanish the moment you switch themes.

## Where the Size Comes From

A commercial theme is this skeleton plus a settings page, a dozen template files, widget areas, and a great deal of CSS. None of that changes the model: WordPress chooses the posts, the template hierarchy chooses the file, the file runs the loop, and the `the_` functions print. Read any theme with that in mind and it stops being intimidating.

Serve the whole directory read-only to the web server, as with everything else under `wp-content`; I described why in [an earlier post](@/blog/wordpress-and-unix-security-part-2.en.md).
