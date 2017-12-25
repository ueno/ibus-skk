ibus-skk -- a Japanese SKK input engine for IBus
======

What's this?
------

ibus-skk is an implementation of the SKK (Simple Kana-Kanji) input
method on the IBus input method framework.  Note that SKK works quite
differently from other Japanese input methods.  To learn about SKK,
see:

* [SKK](https://ja.wikipedia.org/wiki/SKK)

How to install
------
If you build from the source, you will need to separately install
[libskk](http://github.com/ueno/libskk/downloads/).

After installing it, do:
```
$ ./configure
$ make
$ sudo make install
```

How to report bugs
------

Use [issue tracker at GitHub](http://github.com/ueno/ibus-skk/issues).

License
------
```
GPLv2+

Copyright (C) 2011-2017 Daiki Ueno <ueno@gnu.org>
Copyright (C) 2011-2017 Red Hat, Inc.

This file is free software; as a special exception the author gives
unlimited permission to copy and/or distribute it, with or without
modifications, as long as this notice is preserved.

This file is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY, to the extent permitted by law; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```
