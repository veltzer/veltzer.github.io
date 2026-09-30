+++
title = "A Fork Is a Mutiny, and Mutinies Happen Where Nobody Was Allowed to Talk"
date = 2011-05-22

[taxonomies]
tags = ["open-source", "culture"]
+++

Every open source project has, somewhere in its history, a fork. Somebody took the code, gave it a new name, and walked off with part of the community. We treat these events as the natural weather of the movement. I want to suggest that they are something more specific, and that the specificity is useful.

A fork is a mutiny. And mutinies have a well-understood anatomy.

## What a Mutiny at Sea Required

Ships of the age of sail were among the most hierarchical institutions human beings ever built, and they were also floating pressure cookers: a few hundred men, months at sea, no exit, and a captain with nearly absolute authority. Mutinies were rare given those conditions, and when they happened they needed three things.

**A grievance that could not be voiced.** Not merely a grievance. Sailors always had grievances. What set a mutiny off was a grievance with no channel: a captain who would not hear complaints, a chain of command that punished the messenger, a wardroom that met behind a closed door. Where a complaint could be made and answered, even badly, the pressure had somewhere to go.

**A leader.** Somebody with enough standing that others would follow him over the side. Usually not the lowest man aboard but a competent officer or senior hand who had concluded that the legitimate path was closed to him.

**Somewhere to go.** An island, a friendly port, a plausible story for the admiralty. A mutiny with nowhere to sail is a suicide, and men do not sign up for those.

Take away any one of the three and the ship stays whole. Take away the first and the other two never assemble.

## The Same Anatomy in a Project

Now look at a fork you know.

There was a grievance: a direction the maintainer would not consider, a patch series that sat unreviewed for a year, a licence decision made without consultation, a governance question answered with silence. There was a leader: a productive contributor with a reputation of their own, who had tried the legitimate path and found it closed. And there was somewhere to go: a hosting site, a name, a handful of users willing to follow, which is trivially available in a way an island never was.

**The third condition is now free, and the second is common, so the only variable that governs whether a fork happens is the first.** Whether the grievance had a channel.

That reframes the question. We tend to ask, after a fork, who was right about the technical dispute. That is the wrong question, and usually unanswerable. The right question is why the dispute had to be settled by secession instead of by argument, and the answer is almost always that argument was not available. The maintainer did not answer email. Decisions were made in a private channel. The roadmap lived in one person's head. Contributors learned what had been decided by reading the commit log.

## Why Projects Under-Communicate

None of this is malice. It is the default state of a small group of people who are good at code and were never selected for anything else.

Writing a decision down and defending it in public is expensive, and the person who could do it is the same person who could instead fix three bugs in the time. A maintainer does not experience silence as a governance failure; they experience it as getting work done. And the contributor who wanted an answer does not escalate, because there is nobody to escalate to; they either wait, leave quietly, or become the leader of the next mutiny.

The cost is invisible until the fork, at which point it is enormous: divided effort, duplicated bugs, a confused user base, and two projects each too small to do what one could have.

## What a Ship Learned to Do

The navies eventually understood this, and their remedy was not to be nicer. It was procedural. A written code that said what a captain could and could not do. A formal channel for complaints, with a defined path upward. Regular musters at which the state of the ship was stated aloud. The mutiny rate dropped, not because sailors became content, but because their discontent had somewhere to go that was not over the side.

The equivalents for a project are unglamorous and known. Decisions in public, on the list, with reasons. A stated process for how a disputed change is resolved, so that losing an argument feels like losing an argument rather than being ignored. Review latency treated as a metric, because an unanswered patch is a grievance accumulating interest. A roadmap that exists outside one skull. And a habit of saying no out loud, which is harder than saying nothing and far less expensive.

**Disagreement is not the problem. Disagreement with no channel is the problem**, and the fork is what disagreement becomes when the channel is missing. A project that wants to stay whole does not need agreement. It needs to talk more than its maintainers naturally would.

I have argued elsewhere that [corporations defect where individuals cooperate](@/blog/corporations_defect.en.md) because the structure removes the feedback that keeps behaviour honest. A silent project has removed the same feedback. The fork is the feedback arriving late, and all at once.
