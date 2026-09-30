+++
title = "The Two Traits That Make a Programmer Are Laziness and a Bad Memory"
date = 2013-04-21

[taxonomies]
tags = ["programming", "opinion"]
+++

Ask what makes a good programmer and you will hear about intelligence, curiosity, attention to detail, mathematical aptitude. All of these help. None of them is the thing. I have watched a lot of people learn to program, and the two traits that predicted who would become good at it were not on anyone's list of virtues. They were laziness and a poor memory.

I mean this literally, and I want to defend both.

## Laziness

The lazy programmer is the one who, faced with doing the same thing twice, refuses. Not out of principle. Out of a genuine, physical unwillingness to type the same thing again.

That unwillingness is the root of every good habit in the trade. **Automation is laziness with a compiler.** The person who writes a script to rename two hundred files is not more diligent than the person who renames them by hand; he is less diligent, and he has found a way to make the machine absorb the diligence he refuses to supply. Every function ever extracted, every loop ever written, every build system, every deployment pipeline, is a monument to somebody who could not be bothered.

The industrious programmer is a menace. He will happily copy a block of code into five places and edit each one slightly, because that is work, and work is what he is for. He will run the fourteen-step release procedure by hand every Friday for a year without once thinking that fourteen steps that never vary are a program waiting to be written. He does not experience the repetition as pain, and so he never fixes it. His diligence is exactly what makes his code unmaintainable: he can maintain it, at great effort, and he mistakes the effort for value.

The lazy programmer experiences repetition as pain and fixes it immediately, because fixing it is less work than the third repetition. That is the whole mechanism. It is not a metaphor.

There is a second effect. Laziness makes you read the documentation. The industrious programmer tries seventeen things. The lazy one thinks: someone has surely done this already, where is it? And he finds the library function, the existing tool, the standard idiom, because looking was less effort than building. Half of expertise is knowing what already exists, and laziness is what sends you looking.

## A Bad Memory

This one sounds like a defect and is the more important of the two.

A programmer with an excellent memory can hold a large, messy system in his head. He knows that the flag on line 340 interacts with the global on line 1200, that you have to call `init` before `configure` but only on the second run, that the variable called `count` actually holds a size in bytes. He knows all of it, and because he knows it, he never fixes it. The mess costs him nothing. He is its index.

Then he leaves, or forgets, or gets a second project, and the system is unmaintainable, because it was only ever maintainable by his memory.

The programmer with a bad memory cannot do this. He cannot remember that `count` is bytes, so he renames it `size_bytes`. He cannot remember the calling order, so he makes `configure` call `init` itself, or makes it fail loudly if it was skipped. He cannot remember what a function does, so he gives it a name that says, and if it does three things he splits it into three, because three short names are easier to forget and recover than one long behaviour. **He writes code that does not need to be remembered, because he cannot remember it.**

This is what clarity is. Every principle of good code, meaningful names, small functions, no hidden state, no action at a distance, is a technique for making a system legible to someone who has forgotten it. The programmer with a bad memory is that someone every morning, and he writes for himself. The result is code that everyone else can read too.

The excellent memory has one more cost. It makes you tolerant of complexity, and complexity is the enemy. If you can hold twelve interacting conditions in mind, you will write code with twelve interacting conditions, and it will be correct, and nobody else will ever be able to touch it. The person who can hold four will find a design that needs four. The constraint produces the simplicity.

## The Two Together

Notice that the traits reinforce each other. Laziness makes you refuse to repeat yourself, so you abstract. A bad memory makes you unable to keep track of the abstraction unless it is clear, so you name it well and keep it small. Laziness then makes you refuse to look up how the thing works every time, so you make it work the obvious way. Round and round, and out comes something maintainable.

The conventional virtues do not have this property. Intelligence lets you get away with mess. Diligence lets you sustain mess. A good memory lets you navigate mess. All three make the mess survivable, and a mess that is survivable is a mess that survives.

## What Follows

I am not saying you should try to be lazy or forgetful; I am not sure that can be done on purpose. I am saying that if you are, you have the raw material, and that when you interview programmers, the one who says he cannot stand doing anything twice and cannot remember what he wrote last month is telling you something good about himself.

And I am saying that if you have a brilliant memory and boundless energy, be careful. Write as though you had neither. The person maintaining your code next year has neither, and there is a reasonable chance that person is you.
