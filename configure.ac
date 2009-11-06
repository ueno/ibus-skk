# vim:set et ts=4:
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
# Copyright (C) 2009 Daiki Ueno <ueno@unixuser.org>
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

# if not 1, append datestamp to the version number.
m4_define([ibus_released], [0])
m4_define([ibus_major_version], [1])
m4_define([ibus_minor_version], [2])
m4_define([ibus_micro_version], [0])
m4_define(ibus_maybe_datestamp,
    m4_esyscmd([if test x]ibus_released[ != x1; then date +.%Y%m%d | tr -d '\n\r'; fi]))

m4_define([ibus_version],
    ibus_major_version.ibus_minor_version.ibus_micro_version[]ibus_maybe_datestamp)

AC_INIT([ibus-skk], [ibus_version])
AM_INIT_AUTOMAKE([1.10])
AC_GNU_SOURCE

AC_CONFIG_HEADERS([config.h])
AC_CONFIG_MACRO_DIR([m4])

# define PACKAGE_VERSION_* variables
AM_SANITY_CHECK
AM_MAINTAINER_MODE
AM_DISABLE_STATIC
AC_PROG_CC
AM_PROG_CC_C_O
AC_PROG_CXX
AC_ISC_POSIX
AC_HEADER_STDC
AM_PROG_LIBTOOL

# For dislpay Date
m4_define(ibus_maybe_datedisplay,
    m4_esyscmd([if test x]ibus_released[ != x1; then date '+%a %b %d %Y' | tr -d '\n\r'; fi]))
m4_define([ibus_datedisplay], ibus_maybe_datedisplay)
DATE_DISPLAY="ibus_datedisplay"
AC_SUBST(DATE_DISPLAY)

# check env
AC_PATH_PROG(ENV, env)
AC_SUBST(ENV)

# check python
AM_PATH_PYTHON([2.5])

AC_PATH_PROG(PYTHON_CONFIG, python$PYTHON_VERSION-config)
if test x"$PYTHON_CONFIG" == x""; then
    AC_PATH_PROG(PYTHON_CONFIG, python-config)
fi
if test x"$PYTHON_CONFIG" != x""; then
    PYTHON_CFLAGS=`$PYTHON_CONFIG --includes`
    PYTHON_LIBS=`$PYTHON_CONFIG --libs`
else
    PYTHON_CFLAGS=`$PYTHON $srcdir/python-config.py --includes`
    PYTHON_LIBS=`$PYTHON $srcdir/python-config.py --libs`
fi
AC_SUBST(PYTHON_CFLAGS)
AC_SUBST(PYTHON_LIBS)

# OUTPUT files
AC_CONFIG_FILES([
Makefile
engine/Makefile
engine/ibus-engine-skk
engine/skk.xml.in
icons/Makefile
m4/Makefile
])

AC_OUTPUT
