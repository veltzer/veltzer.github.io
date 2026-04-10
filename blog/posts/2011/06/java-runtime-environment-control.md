---
tags:
  - java
  - programming
  - linux
date: 2011-06-09
---

# Java runtime environment control

There are four ways to control Java environment for runtime:

	- _JAVA_OPTIONS environment variable.
	- Command line when running the java virtual machine.
	- Java source code. In this case you must make sure to set the option before it is picked up by whatever subsystem it is intended for.
- In Java web start you can also use the JNLP file to control the environment passed over to the executing JVM.

Examples of them can be:

- `export _JAVA_OPTIONS='-Dawt.useSystemAAFontSettings=lcd'`
- `java -Dawt.useSystemAAFontSettings=lcd [arguments...]`
- `System.setProperty("awt.useSystemAAFontSettings","lcd");`
- `property name="awt.useSystemAAFontSettings" value="lcd"` (under the `resources` element)

Each of these methods naturally has it's own advantages and disadvantages. In Java web start you have a hard time controlling the environment variables or the command line but two options (the JNLP file and the source code itself) are still open to you. 

Some properties, like the anti-aliasing option, is notoriously bad by default and setting it (as shown above) will give you much better look and feel.

The values of the `awt.useSystemAAFontSettings` key are as follows:

- 
`false` corresponds to disabling font smoothing on the desktop.

- 
`on` corresponds to Gnome Best shapes/Best contrast (no equivalent Windows setting).

- 
`gasp` corresponds to Windows `Standard` font smoothing (no equivalent Gnome desktop setting).

- 
`lcd` corresponds to Gnome's `subpixel smoothing` and Windows `ClearType`.

What is the best option to choose? Well - I really don't know. On my laptop `lcd` looks best. Let me know about your own experience...
