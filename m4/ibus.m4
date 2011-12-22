# IBUS_WITH_HOTKEYS([DEFAULT])
AC_DEFUN([IBUS_WITH_HOTKEYS], [
  IBUS_HOTKEYS_DEFAULT=m4_default([$1], [Control+space,Zenkaku_Hankaku])
  AC_ARG_WITH(hotkeys,
    [AC_HELP_STRING([--with-hotkeys=HOTKEYS],
    [Use hotkeys for ibus bridge mode. (available value: yes/no/keys)])],
    [with_hotkeys="$withval"],
    [with_hotkeys="no"])
  if test x$with_hotkeys = xno; then
    IBUS_HOTKEYS_XML="<!-- <hotkeys>${IBUS_HOTKEYS_DEFAULT}</hotkeys> -->"
  elif test x$with_hotkeys = xyes -o x$with_hotkeys = x; then
    IBUS_HOTKEYS="$IBUS_HOTKEYS_DEFAULT"
    IBUS_HOTKEYS_XML="<hotkeys>${IBUS_HOTKEYS}</hotkeys>"
  else
    IBUS_HOTKEYS="$with_hotkeys"
    IBUS_HOTKEYS_XML="<hotkeys>${IBUS_HOTKEYS}</hotkeys>"
  fi
  if test x$IBUS_HOTKEYS != x; then
    AC_DEFINE_UNQUOTED(IBUS_IBUS_HOTKEYS, ["$IBUS_HOTKEYS"],
      [IME specific hotkeys for IBus])
    AC_SUBST(IBUS_HOTKEYS)
  fi
  AC_SUBST(IBUS_HOTKEYS_XML)
])

# IBUS_SET_SYMBOL(SYMBOL)
AC_DEFUN([IBUS_SET_SYMBOL], [
  IBUS_SYMBOL="$1"
  embed_symbol=no
  AC_CHECK_FUNC(ibus_engine_desc_get_symbol, embed_symbol=yes)
  if test x$embed_symbol = xyes; then
    IBUS_SYMBOL_XML="<symbol>${IBUS_SYMBOL}</symbol>"
  else
    IBUS_SYMBOL_XML="<!-- <symbol>${IBUS_SYMBOL}</symbol> -->"
    IBUS_SYMBOL=
  fi
  if test x$IBUS_SYMBOL != x; then
    AC_DEFINE_UNQUOTED([IBUS_SYMBOL], ["$IBUS_SYMBOL"],
      [Icon symbol string for IBus])
    AC_SUBST(IBUS_SYMBOL)
  fi
  AC_SUBST(IBUS_SYMBOL_XML)
])
