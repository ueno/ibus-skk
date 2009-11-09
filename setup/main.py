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

        self.__usrdict = self.__builder.get_object('usrdict')
        self.__sysdict_file = self.__builder.get_object('sysdict_file')
        self.__sysdict = self.__builder.get_object('sysdict')
        self.__sysdict_skkserv = self.__builder.get_object('sysdict_skkserv')
        self.__skkserv_host = self.__builder.get_object('skkserv_host')
        self.__skkserv_port = self.__builder.get_object('skkserv_port')
        self.__period_style = self.__builder.get_object('period_style')

        self.__usrdict.set_filename(self.__config.usrdict_path)

        sysdict_type = self.__config.get_value('sysdict_type', 'file')
        if sysdict_type == 'file':
            self.__sysdict_file.set_active(True)
            self.__sysdict_skkserv.set_active(False)
        else:
            self.__sysdict_file.set_active(False)
            self.__sysdict_skkserv.set_active(True)
        self.__set_sysdict_widgets_sensitivity(sysdict_type)
        self.__sysdict.set_filename(self.__config.sysdict_path)
        self.__skkserv_host.set_text(\
            self.__config.get_value('skkserv_host', 'localhost'))
        self.__skkserv_port.set_text(\
            self.__config.get_value('skkserv_port', '1178'))

        renderer = gtk.CellRendererText()
        self.__period_style.pack_start(renderer)
        self.__period_style.set_attributes(renderer, text=0)
        self.__period_style.set_active(\
            self.__config.get_value('period_style', 0))

        self.__usrdict.connect('file-set', self.__usrdict_file_set_cb)
        self.__sysdict_file.connect('toggled', self.__sysdict_toggle_cb)
        self.__sysdict_skkserv.connect('toggled', self.__sysdict_toggle_cb)
        self.__sysdict.connect('file-set', self.__sysdict_file_set_cb)
        self.__period_style.connect('changed', self.__period_style_changed_cb)

    def __sysdict_toggle_cb(self, widget):
        sysdict_type = 'file' if self.__sysdict_file.get_active() else 'skkserv'
        self.__config.set_value('sysdict_type', sysdict_type)
        self.__set_sysdict_widgets_sensitivity(sysdict_type)

    def __set_sysdict_widgets_sensitivity(self, sysdict_type):
        if sysdict_type == 'file':
            self.__sysdict.set_sensitive(True)
            self.__skkserv_host.set_sensitive(False)
            self.__skkserv_port.set_sensitive(False)
        else:
            self.__sysdict.set_sensitive(False)
            self.__skkserv_host.set_sensitive(True)
            self.__skkserv_port.set_sensitive(True)

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
