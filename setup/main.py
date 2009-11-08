import gtk
import ibus
import locale
import os, os.path
import gettext

class PreferencesDialog:
    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        localedir = os.getenv('IBUS_LOCALEDIR')
        gettext.bindtextdomain('ibus-skk', localedir)
        gettext.bind_textdomain_codeset('ibus-skk', 'UTF-8')

        self.__bus = ibus.Bus()
        self.__config = self.__bus.get_config()
        self.__builder = gtk.Builder()
        self.__builder.set_translation_domain('ibus-skk')
        self.__builder.add_from_file('ibus-skk-preferences.ui')
        self.__dialog = self.__builder.get_object('dialog')

        self.__sysdict = self.__builder.get_object('sysdict')
        sysdict_paths = ('/usr/share/skk/SKK-JISYO',
                         '/usr/share/skk/SKK-JISYO.L',
                         '/usr/local/share/skk/SKK-JISYO',
                         '/usr/local/share/skk/SKK-JISYO.L')
        sysdict_path = None
        for path in sysdict_paths:
            if os.path.exists(path):
                sysdict_path = path
                break
        self.__sysdict.set_filename(self.__get_value('sysdict', sysdict_path))
        self.__sysdict.connect('file-set', self.__sysdict_file_set_cb)

        self.__usrdict = self.__builder.get_object('usrdict')
        usrdict_path = self.__get_value('usrdict',
                                        os.path.expanduser('~/.skk-ibus-jisyo'))
        open(usrdict_path, 'a+').close()
        self.__usrdict.set_filename(usrdict_path)
        self.__usrdict.connect('file-set', self.__usrdict_file_set_cb)

        self.__period_style = self.__builder.get_object('period_style')
        renderer = gtk.CellRendererText()
        self.__period_style.pack_start(renderer)
        self.__period_style.set_attributes(renderer, text=0)
        self.__period_style.set_active(self.__get_value('period_style', 0))
        self.__period_style.connect('changed', self.__period_style_changed_cb)

    def __sysdict_file_set_cb(self, widget):
        print widget.get_filename()
        self.__set_value('sysdict', widget.get_filename())

    def __usrdict_file_set_cb(self, widget):
        print widget.get_filename()
        self.__set_value('usrdict', widget.get_filename())
        
    def __period_style_changed_cb(self, widget):
        print widget.get_active()
        self.__set_value('period_style', widget.get_active())

    def __get_value(self, name, defval):
        value = self.__config.get_value('engine/SKK', name, None)
        if value is not None:
            return value
        self.__set_value(name, defval)
        return defval

    def __set_value(self, name, val):
        self.__config.set_value('engine/SKK', name, val)

    def run(self):
        return self.__dialog.run()

def main():
    PreferencesDialog().run()

if __name__ == "__main__":
    main()
