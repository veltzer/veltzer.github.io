+++
title = "Open Source Is Tit for Tat, and Lock-In Is Always Defect"
date = 2011-01-16

[taxonomies]
tags = ["open-source", "game-theory", "programming"]
+++

Robert Axelrod's *The Evolution of Cooperation* is about a tournament. Strategies for the iterated prisoner's dilemma were submitted as programs and played against each other many times over. The winner, famously, was the simplest entry: tit for tat. Cooperate first, then do whatever the other side did last time. It beat every clever scheme submitted against it, including the strategy that always defects.

I have found this the most useful single frame for understanding what has been happening in the software industry for the last twenty years, and I want to lay the correspondence out.

## The Game

Two parties who exchange software repeatedly face the prisoner's dilemma every time. Each can cooperate, meaning use open formats, document interfaces, share improvements, or defect, meaning lock the other in, hide the interfaces, keep the improvements. In any single exchange defection pays: you gain the lock and the other side bears the cost.

But software exchanges are not single. The same vendors, users and developers meet again every release, every integration, every hiring cycle. That makes the game iterated, and in an iterated game the calculation changes completely, which is Axelrod's whole result.

## Always Defect

Proprietary lock-in is the strategy Axelrod's tournament called ALL-D: defect on every move regardless of what the other side does. Closed formats so that files cannot leave. Undocumented protocols so that competitors cannot connect. Licence terms that punish the customer for looking elsewhere.

ALL-D does well early, against players who have not yet learned what they are dealing with. It extracts a great deal from each exchange. And then it runs out of partners, because everyone who has played against it once switches to defecting back, and a defector surrounded by defectors earns the worst outcome the game offers.

This is not a metaphor. Every organisation that has been burned by a vendor lock-in behaves differently at the next procurement. The industry's collective memory is the tournament's later rounds.

## Tit for Tat

Open source is tit for tat, almost by definition. It cooperates first: the code is published before anyone has done anything to deserve it. It reciprocates: contribute and your contribution is merged, benefit everyone including you. And it retaliates against defection in the one way that matters. The GPL says that if you take and do not give back, you lose the right to take. Even the permissive licences retaliate socially; a company that strip-mines a project and returns nothing finds that the project's developers will not work with it.

**Tit for tat wins in Axelrod's tournament for four reasons, and open source has every one of them.** It is nice, meaning it never defects first. It is retaliatory, so it cannot be exploited for long. It is forgiving, returning to cooperation as soon as the other side does. And it is clear, so that anyone playing against it quickly understands that cooperation is the only way to gain.

## Why Cooperation Wins Where the Game Repeats

Axelrod's condition for cooperation to be stable is that the shadow of the future must be long enough. Players must expect to meet again, and value the future exchanges enough that defecting now is not worth losing them.

Software has an extremely long shadow of the future. Code lives for decades. Formats outlive the products that created them. Developers move between companies carrying their habits and their grudges. A vendor that defects today will be dealing with the same customers, competitors and engineers in ten years, and they will remember.

That is why the open strategy has been gaining ground steadily rather than winning at a stroke. It does not beat lock-in in any single deal. It beats it over the sequence, as more players learn the game and switch to reciprocating. Every server that runs Linux, every language whose reference implementation is free, every standard that was written down before it was implemented is a round of the tournament in which tit for tat scored and ALL-D did not.

## The Uncomfortable Half

The frame also says something open-source advocates do not like to hear. Tit for tat is not altruism. It cooperates because cooperation pays over the long game, and it retaliates because retaliation is what makes cooperation pay. A project that never retaliates, that lets itself be used indefinitely by parties who give nothing back, is not playing tit for tat. It is playing always cooperate, and always cooperate loses to everything.

So the moral of Axelrod for the industry is not that sharing is good. It is that **reciprocity is the strategy that wins a repeated game, and sharing is what reciprocity looks like when the game is software.** The vendors who are losing have not understood that the game repeats. The projects that are winning have not understood it either, in many cases, but their licences understood it for them.
