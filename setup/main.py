import gtk
import locale
import os
import gettext
import config

class PreferencesDialog:
    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        localedir = os.getenv('IBUS_LOCALEDIR')
        gettext.bindtextdomain('ibus-skk', localedir)
        gettext.bind_textdomain_codeset('ibus-skk', 'UTF-8')

        self.__config = config.Config()
        self.__builder = gtk.Builder()
        self.__builder.set_translation_domain('ibus-skk')
        self.__builder.add_from_file('ibus-skk-preferences.ui')
        self.__dialog = self.__builder.get_object('dialog')

        self.__sysdict = self.__builder.get_object('sysdict')
        self.__sysdict.set_filename(self.__config.sysdict_path)
        self.__sysdict.connect('file-set', self.__sysdict_file_set_cb)

        self.__usrdict = self.__builder.get_object('usrdict')
        self.__usrdict.set_filename(self.__config.usrdict_path)
        self.__usrdict.connect('file-set', self.__usrdict_file_set_cb)

        self.__period_style = self.__builder.get_object('period_style')
        renderer = gtk.CellRendererText()
        self.__period_style.pack_start(renderer)
        self.__period_style.set_attributes(renderer, text=0)
        self.__period_style.set_active(\
            self.__config.get_value('period_style', 0))
        self.__period_style.connect('changed', self.__period_style_changed_cb)

    def __sysdict_file_set_cb(self, widget):
        self.__config.set_value('sysdict', widget.get_filename())

    def __usrdict_file_set_cb(self, widget):
        self.__config.set_value('usrdict', widget.get_filename())
        
    def __period_style_changed_cb(self, widget):
        self.__config.set_value('period_style', widget.get_active())

    def run(self):
        return self.__dialog.run()

def main():
    PreferencesDialog().run()

if __name__ == "__main__":
    main()
