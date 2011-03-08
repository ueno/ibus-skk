# vim:set noet ts=4:
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

engine_skk_PYTHON = \
	engine.py \
	factory.py \
	main.py \
	skk.py \
	kzik.py \
	nicola.py \
	virtkbd.py \
	$(NULL)
engine_skkdir = $(pkgdatadir)/engine

libexec_SCRIPTS = ibus-engine-skk
engine_DATA = skk.xml
enginedir = $(datadir)/ibus/component

skk.xml: skk.xml.in
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

test:
	DBUS_DEBUG=true \
	IBUS_SKK_PKGDATADIR=$(abs_top_srcdir) \
	PYTHONPATH=$(builddir)/.libs:@pyexecdir@ \
	$(PYTHON) \
	$(srcdir)/main.py

EXTRA_DIST = \
	skk.xml.in.in \
	ibus-engine-skk.in \
	test.py \
	$(NULL)

CLEANFILES = \
	skk.xml \
	*.pyc \
	$(NULL)

DISTCLEANFILES = \
	$(NULL)
