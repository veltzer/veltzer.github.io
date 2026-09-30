+++
title = "Commented-Out Code Should Still Have to Compile"
date = 2025-11-27

[taxonomies]
tags = ["programming", "opinion"]
+++

Every codebase of any age contains code in comments. A debugging print that someone wants to keep. An alternative implementation that lost a benchmark but might win the next one. A feature that was switched off for a release and will, everyone swears, be switched back on. The advice is always to delete it, because version control remembers, and the advice is always ignored, because nobody trusts themselves to find it again in version control.

I want to propose something different from deletion. **Code inside a comment should be parsed and checked by the language, exactly as if it were live, and it should fail the build when it stops making sense.**

## What I Mean

A special comment, marked somehow so the compiler knows to look inside it:

```c
/*@
    log_packet(pkt, sizeof(*pkt));
@*/
```

The code between the markers is not compiled into the program. It produces no object code, it runs nothing, it changes nothing about the binary. But the compiler parses it, resolves its names, and type-checks it against the surrounding scope, and if `log_packet` has been renamed, or `pkt` is no longer in scope here, or its type has changed so that the call no longer fits, the build fails with an error pointing at the comment.

That is the whole idea. Everything the language checks about live code, it checks about this code too. The only thing it does not do is emit it.

## Why

Commented-out code rots. This is not a matter of opinion; anyone who has uncommented a block that is two years old knows the experience. Half the identifiers no longer exist. A function it calls grew a parameter. A struct it walks has been reorganised. The block that was kept "in case we need it" is, when you need it, a puzzle that takes longer to solve than rewriting it would have.

And it rots invisibly. Live code that goes out of date breaks the build, so it gets fixed the same afternoon by the person who broke it, who knows exactly what they changed and why. Dead code in a comment breaks silently, and the breakage is discovered by someone else, years later, with no idea what changed in between.

**The cost of maintenance is not the problem. The timing of the cost is.** Keeping a block of commented code consistent with the code around it, one small fix at a time as the surroundings change, is cheap: a rename here, a parameter there, done by the person making the change while the change is in their head. Doing all of that maintenance at once, later, with no context, is expensive and often abandoned. Checked comments move the cost from the expensive moment to the cheap one.

## The Objection

The obvious reply is that this makes commented-out code a burden: now I cannot comment something out without keeping it correct forever.

Yes. That is the point. Either the code is worth keeping, in which case it is worth keeping correct, or it is not, in which case the right move was the one everyone recommends and nobody takes, which is to delete it. The checked comment forces the honest choice. The unchecked comment lets you avoid the choice, and the result of avoiding it is the graveyard every old project has.

There is a real cost to this in the case of a large block that is being kept for reference rather than for reuse, where correctness against the current code is not what you want. For that case, the ordinary comment still exists. Nobody is proposing to remove it. The checked comment is an additional tool for the specific case of code that is meant to come back.

## What It Would Take

Not much, in most languages. The parser already has to find the end of a comment; finding a marker inside it is a small extension. The checked block is then parsed as a statement list, or a declaration list, in the scope where the comment appears, with the same name resolution and type checking as live code, and then discarded before code generation. Languages with a preprocessor could do a crude version with `#if 0`, and some people do, but `#if 0` blocks are not parsed, which is exactly what is missing.

A few languages have wandered near this. Doc-comment examples that are compiled and run as tests are the same instinct applied to documentation: the example in the comment must keep working or the build fails. What I am describing is that instinct applied to the code you were going to leave dead.

## The General Principle

Anything you keep should be kept true, and the cheapest time to keep something true is continuously. Every mechanism that lets a thing drift silently out of correctness, whether it is a comment, a configuration file nobody validates, or a document nobody rebuilds, is a mechanism for turning a series of small, cheap fixes into one large, expensive one at the worst possible moment.

Compilers are very good at refusing to accept things that are wrong. We should let them refuse more.
