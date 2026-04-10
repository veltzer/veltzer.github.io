---
tags:
  - embedded
  - real-time
  - programming
date: 2010-09-04
---

# Real time programming tips: running critical tests at application startup

There is much accumulated wisdom in the embedded systems programming field as to how to correctly write a real time application. Examples of this wisdom could be found in the methodology of breaking up the application to a startup phase and a run phase, avoiding exiting the application, avoiding dynamic memory allocation and deallocation at runtime and more. There is also much accumulated wisdom in the programming field in general where a very important principle is ones control of ones software, as opposed to the other way around, and the notion of finding bugs and problems early whether that be in code writing, QA, deployment or beginning of execution.

The combination of the two aforementioned elements forms the principle of critical condition testing at application startup. According to this principle you should put all environmental concerns as tests to be executed at the startup phase of your embedded application. Environmental conditions to be checked may include, among others, the following:

- 
Operating system or C library versions as the software may be adjusted for specific versions of these.

- 
Real time patch availability and version as the software may require real time capabilities.

- 
System real time clock accuracy as the software may require the availability of an accurate system clock.

- 
User under which the software is running as the software may require special permission or user at some point in it's execution.

- 
Free disk space availability as the software may require some disk space.

- 
Free memory availability as the software may accidentally be run on a system with less than the required amount.

- 
A previously running instance of the same or other software that may hinder the softwares operation.

- 
The availability of certain APIs of the kernel or certain kernel modules which are required.

- 
The availability of certain devices (/dev files) with permission to access these.

All of these checks should be run in the first second or so of the software's execution and, contrary to normal wisdom, should cause the software to halt and not proceed with normal execution. The reasons for this scary tactic is that:

- 
You may miss error printouts from your application and so run around trying to find errors in all the wrong places.

- 
You want the errors to show up early and anything that can be made to show up early should be made so.

- 
I have seen programmers confidence in their hardware/OS/environment break too many times and lead to endless hours of wasted effort which could have been prevented by using this strategy.

Some requirements are of the *make or break* type and you really should not go on running without them.

- 
Some of the requirements of real time and embedded systems are so subtle that you would not even notice these break as error in runtime but rather get weird behavior from your system. These are very hard to pin point and should be avoided.

These checks should also be written in a way which enables them to be easily removed when the system has stabilized, when it's environment has stabilized (like when the system moves to production) or in order to reduce boot time.

This principle is especially important to real time and embedded systems programmers because of a few factors:

- 
real time and embedded systems are harder to debug and monitor.

- 
real time and embedded systems have less tools on them that enable one to find bugs.

- 
real time and embedded applications are much more sensitive than other types of applications to various changes in the environment.

- 
embedded systems programs usually interact with other systems which are in the debug phase as well and so may throw the developers on endless bug hunts which waste valuable time and cause the developers to mistrust their entire design or the system and tools that they are using.

- 
embedded software systems usually run 24/7 and have only an end user interface. if at all. Due to this many embedded applications only output a long log and as such either encourage the user to disregard the log completely or make the task of discerning which log lines pertain to critical errors a daunting task.
