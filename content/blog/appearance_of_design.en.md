+++
title = "There Is No Such Thing as the \"Appearance of Design\""
date = 2026-09-24

[taxonomies]
tags = ["philosophy", "science", "atheism", "programming", "linux"]
+++

Richard Dawkins opens *The Blind Watchmaker* with a definition of his entire field: "Biology is the study of complicated things that give the appearance of having been designed for a purpose." A few pages later he says that the products of natural selection "overwhelmingly impress us with the illusion of design and planning." In *Climbing Mount Improbable* he went further and coined a word for it. Living things are not designed, he says, they are *designoid*: objects that look designed but are not, as opposed to Mount Rushmore, which is. And in *The God Delusion* natural selection "shatters the illusion of design within the domain of biology." Francis Crick put the same idea even more bluntly in *What Mad Pursuit*: "Biologists must constantly keep in mind that what they see was not designed, but rather evolved."

I want to object to the phrase. Let me be blunt about where I am coming from, since this is a topic where sentences get lifted out of context: this is an argument *against* a designer, not for one. Natural selection is exactly what Dawkins says it is, blind, unplanned, and without foresight. But the words "appearance of design" concede something to the creationist that never needed conceding, and they leave Dawkins holding a distinction he cannot draw. Organisms do not have the appearance of design. They have a design. It was produced by a real designer, natural selection, working under unusually severe constraints. And once you see that, the argument from design does not need to be refuted. It simply has nothing left to point at.

## Apparent Design Versus Real Design

Dawkins's vocabulary commits him to two categories: things that are really designed, like Mount Rushmore, and things that are merely designoid, like a face in a hillside or a bird's wing. The trouble is that he owes us a way of telling them apart, and he has none that survives inspection.

It cannot be the artifact. A wing is fitted to flight more tightly than any aircraft; an eye is fitted to seeing better than any camera. If you judged by the object alone, the organism would win the design contest against the artifact every time. Dawkins knows this, which is why he needs the word "appearance" in the first place: the object is indistinguishable from a designed one, so the difference must lie elsewhere.

It cannot be the process either, as I will argue below, because the process by which minds design things turns out to be the same process that selection runs.

That leaves only one candidate: a mind was present. "Real design" means "a mind did it," and "apparent design" means "it looks the same but no mind did it." But that is not a discovery about biology. It is a stipulation about a word, and a strange one for a materialist to make. It puts the whole weight of the word "design" on a fact about the history of the object that leaves no trace in the object and no trace in the process. Dawkins would never accept that a computer merely has the appearance of arithmetic because nobody is inside it doing sums. Yet that is exactly the move he makes here.

Under the framework I am proposing there is no such problem, because there is no such distinction. Design is what a certain kind of process produces: generate variants, test them against a criterion, keep what passes, iterate, and never let the system stop working along the way. Anything that has been through that process has a design. Human engineers run it with one set of constraints, natural selection runs it with another, and they are both real design, in exactly the same sense, differing in their constraints and not in their kind.

## The Objection: Design Needs a Designer

The obvious reply is that design does involve intent, by definition, and evolution has none. A designer wants something; selection wants nothing. That is a real difference and I do not want to hide it. But it is a difference in the *motive* of the process, not in the process or its result, and we can check that claim in the one field where we get to watch design happen from the inside: software.

## Agile Development Is Evolution With a Coding Standard

Ask a working software engineer how large systems actually get built, and you will not hear about a blueprint. You will hear about agile development, which is a set of constraints adopted on purpose by an entire industry. The central constraint is this: **never make a large change.** Work in small increments. Every increment must leave the system working and shippable. There is no "under construction" state. Do not write the grand design up front; let the design emerge from the accumulation of increments, each one tested against a customer who does not know what they want until they see it.

Now list the properties of natural selection. Never make a large change, because a large mutation is almost always lethal. Every intermediate organism must survive and reproduce; there is no "under construction" state. There is no blueprint; the form emerges from the accumulation of small changes, each one tested against an environment that states no requirements and simply accepts or rejects what is delivered.

These are not analogous processes. They are the same process, described twice. Agile even reproduces evolution's most famous flaw. Because you may never stop and redesign, you accumulate what programmers call technical debt: the ugly workaround that was locally the smallest change and can never be removed because everything now depends on it.

Biology is full of technical debt. The recurrent laryngeal nerve loops from the brain down around the aorta and back up to the larynx, several meters of detour in a giraffe, because in a fish it ran straight and no intermediate could be allowed to break. The vertebrate retina is wired backwards. The human spine is a horizontal design pressed into vertical service. Any engineer who has maintained a ten-year-old codebase recognizes all of it at once. François Jacob said in 1977 that evolution works like a tinkerer rather than an engineer. He was right about the tinkering and wrong about the contrast: the tinkerer is what an engineer looks like under the constraint that nothing may ever be broken.

Would anyone say that a team practicing agile development does not *design* its software? That the finished product merely has the "appearance of design," because no one drew it in advance? Of course not. We would say it was designed incrementally, under a constraint, by a process of variation and selection. And that is exactly what we should say about the eye.

## Linus Torvalds Already Said This

The largest piece of software on earth, which runs most of the internet, every Android phone, and nearly every supercomputer, was built this way, and the man who built it has been unusually honest about it. In November 2001, on the Linux kernel mailing list, in a thread that started as an argument about coding style, Linus Torvalds wrote:

> Let's just be honest, and admit that it wasn't designed.
>
> Software evolves. It isn't designed. The only question is how strictly you control the evolution.
>
> It grew. It grew with a lot of mutations - and because the mutations were less than random, they were faster.
>
> Don't EVER make the mistake that you can design something better than what you get from ruthless massively parallel trial-and-error with a feedback cycle.

And two years later, on a Usenet group: "You're giving the human mind too much credit, and giving too little credit to the selection process."

Read those again. Torvalds has minds available. He has thousands of intelligent contributors, each one choosing their changes deliberately. He concedes that this makes the mutations "less than random," which speeds the process up. And he still says the result was not designed in the sense Dawkins means, that it *evolved*, and that the design came from the feedback cycle and not from anyone's intelligence. Torvalds and Dawkins agree completely on the facts. They just draw the line in opposite places. Dawkins says: not made by a mind, therefore not design, merely designoid. Torvalds says: this is how design is actually done, and the mind is the least important part.

Torvalds is right, and he is right for a reason Dawkins should appreciate. If you reserve the word "design" for what minds do, you have to say what the minds are doing that selection is not. And when you look, you find that the minds are running selection. An engineer generates candidates, tests them against a criterion, keeps the survivors, and iterates. Nobody derives a bridge from first principles; they copy last year's bridge and modify it. Human design is descent with modification plus a selection filter called testing.

## What Intent Actually Buys

I said I would not hide the difference, so here it is. A mind can run the selection loop over models instead of over organisms. An engineer discards a bad bridge on paper; evolution discards it as a corpse. Karl Popper's phrase for this was that we let our hypotheses die in our stead. That is a genuine advantage, and it is why an engineer takes a decade to do what selection takes a hundred million years to do. The mind supplies a better mutation operator: variants are proposed with some foresight, and many are killed before they are ever built.

But notice what this concession is. It is a statement about the *constraints* the process runs under, not about whether it is design. Human design is selection with cheap tests and foresighted proposals. Natural selection is design with expensive tests and blind proposals. A team doing agile with a good test suite is somewhere in between. These are different points on one scale, and every point on it is real design. There is no place on the scale where design turns into the appearance of design, because nothing about the process changes except its budget.

## Why the Distinction Matters

The argument from design has one premise that does all the work: design implies a designer. Dawkins accepts the premise and denies that there is any design, which forces him into "apparent," "illusion," and "designoid," and then into a distinction between apparent and real that he cannot cash out. That is a weak position, and the creationist can feel it. If organisms really are indistinguishable from designed things, in artifact and in process, then calling them designoid sounds like exactly what it is: a refusal to use the obvious word.

The stronger position denies the premise instead. Design does not imply a designer. Design implies a design process, and a design process needs a source of variation, a selection criterion, and time. Minds are one such process. Natural selection is another. Both are real, both produce real designs, and the second one is the one that produced us. Once that is said, there is no gap for a God to fill. The creationist's strongest observation, that living things are exquisitely designed, is granted in full, and it leads nowhere, because the designer it points at is a blind process that we can watch at work in any software company.

Crick's sentence should therefore be reversed. Biologists must constantly keep in mind that what they see was not planned, but rather designed, by the same method Linus used, with a worse mutation operator and a much larger budget.

## Conclusion

Dawkins needs two kinds of design, real and apparent, and cannot say what separates them, because nothing does. I need one kind, with different constraints, and the organisms come out designed and the God comes out unemployed. There is nothing designoid about an eye. It has a design, produced by a designer that is real, blind, and slow, and that anyone who has ever shipped software in small working increments already knows from the inside. Selection is not something that imitates design. Selection is how design gets done.
