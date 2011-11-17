# vim:set noet ts=4:
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
# Copyright (C) 2009-2010 Daiki Ueno <ueno@unixuser.org>
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

SUBDIRS = \
	src \
	icons \
	m4 \
	po \
	scripts \
	$(NULL)

ACLOCAL_AMFLAGS = -I m4

component_DATA = skk.xml
componentdir = $(datadir)/ibus/component

skk.xml: skk.xml.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

EXTRA_DIST = \
	autogen.sh \
	skk.xml.in.in \
	ibus-skk.spec.in \
	$(NULL)

CLEANFILES = \
	skk.xml \
	$(NULL)

DISTCLEANFILES = \
	skk.xml.in \
	po/stamp-it \
	$(NULL)

dist-hook:
	if test -d .git ; then \
		git log --name-status --date=iso > $(distdir)/ChangeLog ; \
	fi
