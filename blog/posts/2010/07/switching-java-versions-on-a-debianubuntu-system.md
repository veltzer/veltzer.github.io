---
tags:
  - java
  - debian
  - linux
date: 2010-07-26
---

# Switching Java versions on a Debian/Ubuntu system

I recently found some issues with the openjdk Ubuntu/Debian default Java implementation. Specifically I had issues with their web start support (javaws). I found that the Sun implementation of Java did not have such a deficiency and the Sun implementation is available through the regular Ubuntu/Debian package sources. I installed the Sun implementation and wanted to switch the default Java to that version.

So what have I found out ?

When you want to switch to the Sun implementation:
`sudo update-java-alternatives --set java-6-sun`

When you want to go back to the openjdk implementation:
`sudo update-java-alternatives --set java-6-openjdk`

Notice that once you do any of the above you leave "auto" mode which means that new installation of Java implementation will **not** switch your default one. If that is what you want then ok. If not you can return to "auto" mode with:
`sudo update-java-alternatives --auto`
