ibus-skk -- a Japanese SKK input engine for IBus
======

*I'm no longer actively maintain this project.  If you use it and want to take over the maintenance, let [me](mailto:ueno@gnu.org) know.*

What's this?
------

ibus-skk is an implementation of the SKK (Simple Kana-Kanji) input
method on the IBus input method framework.  To learn about SKK, see:

* [SKK Openlab](http://openlab.jp/skk/)
* [SKK](https://secure.wikimedia.org/wikipedia/ja/wiki/SKK)

How to install
------
```
$ sudo yum install ibus-skk # on Fedora
$ sudo apt-get install ibus-skk # on Debian or Ubuntu
```

If you build from the source, you will need to separately install
[libskk](http://github.com/ueno/libskk/downloads/).

How to report bugs
------

Use [issue tracker at GitHub](http://github.com/ueno/ibus-skk/issues) for upstream issues, [Red Hat Bugzilla](https://bugzilla.redhat.com/buglist.cgi?component=ibus-skk&product=Fedora) for Fedora specific issues, or [Debian BTS](http://bugs.debian.org/cgi-bin/pkgreport.cgi?pkg=ibus-skk;dist=unstable) for Debian specific issues.

License
------
```
GPLv2+

Copyright (C) 2011-2014 Daiki Ueno <ueno@gnu.org>
Copyright (C) 2011-2012 Red Hat, Inc.

This file is free software; as a special exception the author gives
unlimited permission to copy and/or distribute it, with or without
modifications, as long as this notice is preserved.

This file is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY, to the extent permitted by law; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```
