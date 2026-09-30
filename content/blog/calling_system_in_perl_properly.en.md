+++
title = "How to Call system() in Perl Without Getting Burned"
date = 2011-08-14

[taxonomies]
tags = ["programming", "perl"]
+++

Every Perl script that has been around long enough eventually shells out to something. And almost every one of them does it wrong in the same three ways: it builds a command string, it ignores the return value, and it lets the shell interpret data it never meant to interpret. Here is the version that does not bite.

## The List Form, Not the String

`system` has two calling conventions, and the difference is the whole story.

```perl
# Wrong: one string, handed to /bin/sh
system("cp $src $dst");

# Right: a list, executed directly
system("cp", $src, $dst);
```

The string form passes the whole line to the shell. The shell then splits on whitespace, expands globs, interprets quotes, and honours every metacharacter it knows. If `$src` is `my file.txt` you copy two files that do not exist. If it is `; rm -rf ~` you have a much worse afternoon.

The list form skips the shell entirely. Perl calls `execvp` with the arguments exactly as you gave them. A filename with a space is one argument. A filename with a semicolon is one argument. Nothing is interpreted, because nothing is parsed.

**The rule is simple: if you have more than one element, use the list form.** The only time the string form is defensible is when you genuinely want the shell, for a pipe or a redirection, and even then it is better to do the redirection in Perl.

## Check the Return Value, and Check It Correctly

`system` does not die on failure. It returns, and the return value is not what people expect.

```perl
my $rc = system("make", "all");
```

`$rc` is the raw wait status, the same value that lands in `$?`. It packs three things: the exit code in the high byte, the signal that killed the child in the low seven bits, and a core-dump flag. A child that exited with status 1 gives you 256. A child that was killed by SIGSEGV gives you 11. A child that could not be started at all gives you -1.

So unpack it:

```perl
my $rc = system("make", "all");
if ($rc == -1) {
    die "failed to execute make: $!";
}
elsif ($rc & 127) {
    die sprintf("make died with signal %d%s",
        ($rc & 127), ($rc & 128) ? ", core dumped" : "");
}
elsif ($rc >> 8) {
    die sprintf("make exited with status %d", $rc >> 8);
}
```

That is verbose, which is why nobody writes it, which is why scripts silently continue after the compile failed. Wrap it once:

```perl
sub run {
    my @cmd = @_;
    my $rc = system(@cmd);
    return if $rc == 0;
    my $desc = join(" ", @cmd);
    die "failed to execute [$desc]: $!\n" if $rc == -1;
    die sprintf("[%s] died with signal %d\n", $desc, $rc & 127) if $rc & 127;
    die sprintf("[%s] exited with status %d\n", $desc, $rc >> 8);
}

run("make", "all");
run("cp", $src, $dst);
```

Now a failed command stops the script with a message that says what failed and how. **A shell-out that is not checked is a shell-out that has been declared irrelevant**, and if it were irrelevant you would not be running it.

## Capturing Output

`system` returns the status and lets the child write to your stdout. When you want the output itself, the reflex is backticks:

```perl
my $out = `ls $dir`;
```

Backticks have the string-form problem exactly: the whole thing goes through the shell. Newer Perls accept a list form for `readpipe`, but the portable answer is to open a pipe from a list:

```perl
open(my $fh, "-|", "ls", "-l", $dir)
    or die "cannot run ls: $!";
my @lines = <$fh>;
close($fh) or die "ls failed with status " . ($? >> 8);
```

The three-argument `open` with `-|` as the mode runs the command with a list, no shell, and gives you a filehandle on its output. The `close` returns false if the child failed, and `$?` holds the status, so you get the check for free.

For anything more involved, both stdout and stderr, feeding stdin, timeouts, use `IPC::Open3` from the core distribution or `IPC::Run` from CPAN. Do not build a pipeline string and hand it to the shell.

## Quoting Is Not a Solution

Someone will say: just quote the variables.

```perl
system("cp '$src' '$dst'");   # still wrong
```

What if `$src` contains a single quote? You escape it. What if it contains a newline, or a backslash, or a dollar sign in double quotes? The rules for shell quoting are intricate and differ between shells, and every layer of escaping you add is another place to get it wrong. `String::ShellQuote` does it properly if you must, but you must not: the list form makes the whole problem disappear, and disappearing problems beat solved problems.

## The Summary

- Use the list form of `system` unless you are deliberately invoking the shell.
- Always check the return value, and unpack it: -1 means could not start, low bits mean a signal, high byte means exit status.
- Wrap the check once and call the wrapper everywhere.
- To capture output, `open` a pipe with a list, and check `close`.
- Do not try to quote your way out of the string form.

None of this is clever. It is what `perldoc -f system` has said for twenty years. It is just that the wrong way is one line and the right way is five, and five loses to one until the first time a filename has a space in it.
