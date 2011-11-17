libexec_PROGRAMS = ibus-engine-skk ibus-setup-skk

# force include config.h before gi18n.h.
AM_CPPFLAGS = -include $(CONFIG_HEADER)

ibus_engine_skk_VALAFLAGS = \
	--vapidir=. \
	--pkg config --pkg gee-1.0 --pkg skk-1.0 --pkg ibus-1.0 \
	$(VALAFLAGS)

ibus_engine_skk_CFLAGS = \
	$(IBUS_SKK_CFLAGS) \
	-DPACKAGE_DATADIR=\"$(pkgdatadir)\"	\
	-DLOCALEDIR=\"$(datadir)/locale\"	\
	-DLIBEXECDIR=\"$(libexecdir)\"

ibus_engine_skk_LDADD = \
	$(IBUS_SKK_LIBS)

ibus_engine_skk_SOURCES = \
	preferences.vala \
	plist.vala \
	engine.vala

ibus_setup_skk_VALAFLAGS = \
	--vapidir=. \
	--pkg config --pkg gee-1.0 --pkg skk-1.0 --pkg ibus-1.0 --pkg gtk+-3.0 \
	$(VALAFLAGS)

ibus_setup_skk_CFLAGS = \
	$(IBUS_SKK_CFLAGS) $(GTK_CFLAGS) \
	-DPACKAGE_DATADIR=\"$(pkgdatadir)\" \
	-DLOCALEDIR=\"$(datadir)/locale\" \
	-DSETUPDIR=\"$(setupdir)\" \
	-DDATADIR=\"$(datadir)\"

ibus_setup_skk_LDADD = \
	$(IBUS_SKK_LIBS) $(GTK_LIBS)

ibus_setup_skk_SOURCES = \
	preferences.vala \
	plist.vala \
	setup.vala

setupdir = $(pkgdatadir)/setup
setup_DATA = ibus-skk-preferences.ui

CLEANFILES = *.[ch]
EXTRA_DIST = config.vapi ibus-1.0.vapi ibus-1.0.deps ibus-skk-preferences.ui.in
DISTCLEANFILES = ibus-skk-preferences.ui
