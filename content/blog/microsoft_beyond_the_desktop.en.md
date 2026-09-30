+++
title = "Microsoft's Damage Was Never Mainly About the Desktop"
date = 2026-04-25

[taxonomies]
tags = ["windows", "history", "opinion"]
+++

I have [written before](@/blog/windows_damage_to_tech.en.md) about what it cost the industry to train a generation of developers on an operating system that nothing in production ran on. That post was about the developer's desk. This one is about everything else, because the desk was the smallest of the problems, and because I argued about the rest of them at the time and would like to record how the argument came out.

## An Operating System Interface Is Infrastructure

Start with what an operating system's programming interface actually is. Every application on a platform is written against it. Every driver, every library, every tool. It is the road network of computing: not a product you choose but the surface everything else has to run on.

We understand this about roads, water, and the electrical grid, and we regulate them accordingly. Nobody thinks it acceptable for a private firm to own the only road into a city and to price and shape it for its own advantage.

**For twenty years the dominant operating system interface of the world was owned by one company that did exactly that**, and we treated it as an ordinary commercial arrangement. The interface was documented selectively. It changed when change disadvantaged a competitor. The company's own applications knew things about it that everyone else's did not. Both the United States and the European Union eventually found that this was how the platform had been used, and the remedies were mild and late.

The point is not that a monopoly existed. Monopolies come and go. The point is that the thing monopolised was infrastructure, and we let infrastructure be run as a product.

## The Chip Industry Held in Place

The second cost is harder to see because it is a cost of things that did not happen.

For most of the personal computing era there was one processor architecture that mattered, because there was one operating system that mattered and it ran on that architecture. The two companies had a shared interest in keeping it so. A competing processor design had to clear a bar no technical merit could clear: it had to run the software, and the software ran on the incumbent.

So for two decades the hardware side of the industry improved along one axis, clock speed and then core count, inside one instruction set, because that was the only direction in which improvement could be sold. Everything else, and there was a great deal else being designed in laboratories, could not get past the platform.

When the lock finally broke, it broke from outside. It took a whole new class of device, the phone, running a different operating system, to make a different architecture commercially viable. That is what it costs to displace an infrastructure monopoly: you cannot do it on the merits, you have to wait for the terrain to change.

## Pricing and Conduct

Two smaller items, quickly.

An operating system licence was priced as though it were a scarce good. It was not; the marginal copy cost nothing. The price was what the lock permitted, and it was paid on every machine sold whether or not the buyer wanted the software, because manufacturers were contractually discouraged from shipping anything else. Economists call this a tax and they are right.

And the conduct toward anything that threatened the arrangement was aggressive in a way the record documents thoroughly. Internal correspondence produced in the antitrust cases describes competitors as things to be cut off from air. Standards were embraced in order to be extended into incompatibility. Partners who strayed were punished. None of this is controversial now; it is in the court findings.

## The SCO Episode

Then, in 2003, a company called SCO announced that Linux infringed its rights to Unix and began suing users and vendors. The claims were weak and were eventually thrown out. What made the episode instructive was the money.

A firm called BayStar Capital invested fifty million dollars in SCO to fund the litigation. It later emerged, and BayStar said so publicly, that Microsoft had referred them to the deal. Microsoft also bought Unix licences from SCO at the same time, for reasons nobody outside the company found convincing.

Whatever the intent, the effect was that a lawsuit whose main function was to frighten businesses away from Linux was financed, indirectly, by the company that Linux threatened. The fear worked for a few years. Then it stopped working, because the lawsuit failed and the fear had nothing to stand on.

## What I Argued Then

I wrote, at the time, an open argument to the business community, and I want to state it because it turned out to be right in a way I did not fully expect.

The argument was not that monopolies are bad. It was a forecast. If you accept that free operating systems are not going away, then the tech sector has to adapt to them eventually, and **every year the adaptation is delayed makes it more expensive.** Slowing Linux does not prevent the transition. It stacks the cost of the transition higher, to be paid all at once later. Training on Windows, tooling for Windows, products built on Windows, all of it becomes stranded investment on the day the platform stops being the platform.

Here is how it played out. The transition did happen, though not on the desktop where everyone was looking. It happened in the server room, in the phone, in the cloud, in embedded devices, in the supercomputer. Linux became the operating system of essentially everything except the desk, and the desk stopped being where computing happened.

And the cost was paid exactly as predicted. Decades of Windows-specific skill had to be relearned. Whole categories of tooling existed only to bridge a gap that need not have existed. The companies that had bet entirely on the incumbent platform either rebuilt themselves or disappeared. Microsoft itself eventually shipped Linux inside Windows, which is as close to a formal concession as a company can make.

## The Lesson That Was Not Learned

The lesson is not about one company, which has since become a reasonable citizen of the open-source world and is now a distant second in the platform wars it once won.

The lesson is about infrastructure. **When a layer that everything runs on is owned by one party, the cost is not the price. The cost is every direction the industry could not go.** We saw that cost paid once, over about twenty-five years, and we are letting it be paid again in the platforms that replaced the operating system as the surface everything runs on. The names have changed. The structure has not.
