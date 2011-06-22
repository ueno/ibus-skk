# IBUS_WITH_HOTKEYS
AC_DEFUN([IBUS_WITH_HOTKEYS], [
  AC_ARG_WITH(hotkeys,
    [AC_HELP_STRING([--with-hotkeys=HOTKEYS],
    [Use hotkeys for ibus bridge mode. (available value: yes/no/keys)])],
    [HOTKEYS="$withval"],
    [HOTKEYS="no"])
  if test x$HOTKEYS = xno; then
    HOTKEYS="<!-- <hotkeys>Control+space,Zenkaku_Hankaku</hotkeys> -->"
  elif test x$HOTKEYS = xyes; then
    HOTKEYS="<hotkeys>Control+space,Zenkaku_Hankaku</hotkeys>"
  elif test x$HOTKEYS = x; then
    HOTKEYS="<hotkeys>Control+space,Zenkaku_Hankaku</hotkeys>"
  else
    HOTKEYS="<hotkeys>${HOTKEYS}</hotkeys>"
  fi
  AC_SUBST(HOTKEYS)
])

# IBUS_ICON_SYMBOL(SYMBOL)
AC_DEFUN([IBUS_ICON_SYMBOL], [
  if test x$PYTHON = x; then
    AM_PATH_PYTHON([2.5])
  fi
  AC_MSG_CHECKING([if ibus supports icon symbol])
  $PYTHON <<_ICON_SYMBOL_TEST
import ibus
engine = ibus.EngineDesc('test')
exit(hasattr(engine, 'icon_symbol'))
_ICON_SYMBOL_TEST
  if test $? -ne 0; then
    ICON_SYMBOL="<icon_symbol>$1</icon_symbol>"
    AC_MSG_RESULT([yes])
  else
    ICON_SYMBOL="<!-- <icon_symbol>$1</icon_symbol> -->"
    AC_MSG_RESULT([no])
  fi
  AC_SUBST(ICON_SYMBOL)
])
