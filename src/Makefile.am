libexec_PROGRAMS = ibus-engine-skk ibus-setup-skk
noinst_LTLIBRARIES = libutil.la

libutil_la_VALAFLAGS =				\
	-H libutil.h --vapi ibus-skk.vapi	\
	--vapidir=.				\
	--pkg config				\
	--pkg gee-1.0				\
	--pkg skk-1.0				\
	--pkg ibus-1.0				\
	--library ibus-skk			\
	$(VALAFLAGS)
libutil_la_SOURCES =				\
	preferences.vala			\
	plist.vala
libutil_la_CFLAGS =				\
	$(COMMON_CFLAGS)

# force include config.h before gi18n.h.
AM_CPPFLAGS = -include $(CONFIG_HEADER)

COMMON_CFLAGS =					\
	$(IBUS_CFLAGS)				\
	$(LIBSKK_CFLAGS)			\
	-DPACKAGE_DATADIR=\"$(pkgdatadir)\"	\
	-DLOCALEDIR=\"$(datadir)/locale\"	\
	-DSETUPDIR=\"$(setupdir)\"		\
	-DLIBEXECDIR=\"$(libexecdir)\"		\
	-DDATADIR=\"$(datadir)\"

COMMON_LIBS =					\
	$(IBUS_LIBS)				\
	$(LIBSKK_LIBS)

ibus_engine_skk_VALAFLAGS =			\
	--vapidir=.				\
	--pkg config --pkg ibus-skk		\
	$(VALAFLAGS)

ibus_engine_skk_CFLAGS =			\
	$(COMMON_CFLAGS)

ibus_engine_skk_LDADD =				\
	$(COMMON_LIBS)				\
	libutil.la

ibus_engine_skk_SOURCES =			\
	engine.vala

ibus_setup_skk_VALAFLAGS =			\
	--vapidir=.				\
	--pkg config				\
	--pkg ibus-skk				\
	--pkg gtk+-3.0				\
	$(VALAFLAGS)

ibus_setup_skk_CFLAGS =				\
	$(COMMON_CFLAGS)			\
	$(GTK_CFLAGS)

ibus_setup_skk_LDADD =				\
	$(COMMON_LIBS)				\
	$(GTK_LIBS)				\
	libutil.la

ibus_setup_skk_SOURCES =			\
	setup.vala

setupdir = $(pkgdatadir)/setup
setup_DATA = ibus-skk-preferences.ui

CLEANFILES =					\
	ibus-skk.vapi				\
	$(NULL)

EXTRA_DIST =					\
	config.vapi				\
	ibus-skk.deps				\
	ibus-1.0.vapi				\
	ibus-1.0.deps				\
	ibus-skk-preferences.ui.in		\
	$(NULL)

DISTCLEANFILES =				\
	ibus-skk-preferences.ui			\
	$(NULL)
