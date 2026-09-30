+++
title = "A Ten-Line PHP Template Function Is All a Small Site Needs"
date = 2010-04-11

[taxonomies]
tags = ["php", "programming"]
+++

Every PHP project eventually reaches the point where HTML and logic have to be separated, and at that point most people reach for a templating library. Smarty, Twig, and their relatives are fine pieces of software. They are also a second language to learn, a compilation step, a cache directory to keep writable, and a few thousand lines of code between you and the page. For a small site none of that is needed, because PHP already is a template language. All that is missing is a function that uses it as one.

## The Function

```php
<?php
function render($template, array $vars = array())
{
    extract($vars, EXTR_SKIP);
    ob_start();
    include $template;
    return ob_get_clean();
}
```

That is the whole thing. It does three jobs.

`extract()` turns the keys of the array into local variables, so a template can say `$title` instead of `$vars['title']`. The `EXTR_SKIP` flag means a key called `template` cannot overwrite the function's own parameter.

`ob_start()` switches on output buffering, so that everything the template echoes is captured instead of sent to the browser.

`include` runs the template file as ordinary PHP with those variables in scope, and `ob_get_clean()` returns the captured output as a string and turns buffering off.

## A Template

Templates are plain PHP files that contain mostly HTML:

```php
<h1><?php echo htmlspecialchars($title); ?></h1>
<ul>
<?php foreach ($items as $item): ?>
    <li><?php echo htmlspecialchars($item); ?></li>
<?php endforeach; ?>
</ul>
```

The alternative syntax for control structures (`foreach ... endforeach`, `if ... endif`) exists precisely for this use. It reads as a template rather than as code, and the closing keywords keep the nesting visible when tags are interleaved with markup.

## Using It

```php
<?php
$page = render('templates/list.php', array(
    'title' => 'Things I own',
    'items' => array('a bicycle', 'a piano', 'too many books'),
));

echo render('templates/layout.php', array(
    'title' => 'Things I own',
    'body'  => $page,
));
```

Templates nest by rendering the inner one to a string and passing it to the outer one as a variable. A layout template prints `$body` where the content goes. That gives you the one feature people actually want from a template engine, a shared page frame, with no engine.

## Escaping

The one thing a template engine gives you that this function does not is automatic escaping, and it is the one thing you must not forget. **Every value that came from outside the program goes through `htmlspecialchars()` before it is printed.** Typing that is tedious, so define a short alias:

```php
<?php
function e($s)
{
    return htmlspecialchars($s, ENT_QUOTES, 'UTF-8');
}
```

and write `<?php echo e($title); ?>`. The template above becomes shorter and the rule becomes easy to audit: any `echo` without an `e()` around it is a bug unless the variable is known to be HTML you produced yourself, such as `$body` in the layout.

## Why This Is Enough

A template engine earns its weight when designers who do not know PHP edit the templates, when templates come from an untrusted source and must be sandboxed, or when the same templates are rendered by something other than PHP. Small sites have none of these problems. The person editing the template is the person who wrote the function.

What the ten lines give you is exactly what the engine gives you in the common case: HTML in its own files, logic in its own files, variables passed explicitly across the boundary, and layouts by nesting. What they cost you is nothing. There is no syntax to learn beyond the language you are already using, no cache to invalidate, and when something goes wrong the stack trace points at a line in a file you can read.

I have used this function, or one indistinguishable from it, on every small PHP site I have built. I have never once needed to replace it.
