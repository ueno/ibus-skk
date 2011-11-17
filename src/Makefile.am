libexec_PROGRAMS = ibus-engine-skk ibus-setup-skk
noinst_LTLIBRARIES = libibusskk.la

libibusskk_la_VALAFLAGS =					\
	-H libibusskk.h --vapi ibus-skk.vapi			\
	--vapidir=.						\
	--pkg config --pkg gee-1.0 --pkg skk-1.0 --pkg ibus-1.0	\
	--library ibus-skk					\
	$(VALAFLAGS)
libibusskk_la_SOURCES =				\
	preferences.vala			\
	plist.vala
libibusskk_la_CFLAGS =				\
	$(IBUS_SKK_CFLAGS)

# force include config.h before gi18n.h.
AM_CPPFLAGS = -include $(CONFIG_HEADER)

ibus_engine_skk_VALAFLAGS =			\
	--vapidir=.				\
	--pkg config --pkg ibus-skk		\
	$(VALAFLAGS)

ibus_engine_skk_CFLAGS =			\
	$(IBUS_SKK_CFLAGS)			\
	-DPACKAGE_DATADIR=\"$(pkgdatadir)\"	\
	-DLOCALEDIR=\"$(datadir)/locale\"	\
	-DLIBEXECDIR=\"$(libexecdir)\"

ibus_engine_skk_LDADD =				\
	$(IBUS_SKK_LIBS)			\
	libibusskk.la

ibus_engine_skk_SOURCES =			\
	engine.vala

ibus_setup_skk_VALAFLAGS =				\
	--vapidir=.					\
	--pkg config --pkg ibus-skk --pkg gtk+-3.0	\
	$(VALAFLAGS)

ibus_setup_skk_CFLAGS =				\
	$(IBUS_SKK_CFLAGS) $(GTK_CFLAGS)	\
	-DPACKAGE_DATADIR=\"$(pkgdatadir)\"	\
	-DLOCALEDIR=\"$(datadir)/locale\"	\
	-DSETUPDIR=\"$(setupdir)\"		\
	-DDATADIR=\"$(datadir)\"

ibus_setup_skk_LDADD =				\
	$(IBUS_SKK_LIBS)			\
	$(GTK_LIBS)				\
	libibusskk.la

ibus_setup_skk_SOURCES =			\
	setup.vala

setupdir = $(pkgdatadir)/setup
setup_DATA = ibus-skk-preferences.ui

CLEANFILES =					\
	*.[ch]					\
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
