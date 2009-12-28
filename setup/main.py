import gtk
import locale
import os, sys
import gettext
import config

sys.path.insert(0, os.path.join(os.getenv('IBUS_SKK_PKGDATADIR'), 'engine'))
import skk

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
        self.__page_size = self.__builder.get_object('page_size')
        self.__pagination_start = self.__builder.get_object('pagination_start')
        self.__show_annotation = self.__builder.get_object('show_annotation')
        self.__auto_start_henkan_keywords = \
            self.__builder.get_object('auto_start_henkan_keywords')

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
            self.__config.get_value('skkserv_host', skk.SkkServ.HOST))
        self.__skkserv_port.set_numeric(True)
        self.__skkserv_port.set_range(0.0, 65535.0)
        self.__skkserv_port.set_value(\
            int(self.__config.get_value('skkserv_port', skk.SkkServ.PORT)))

        renderer = gtk.CellRendererText()
        self.__period_style.pack_start(renderer)
        self.__period_style.set_attributes(renderer, text=0)
        self.__period_style.set_active(\
            self.__config.get_value('period_style', skk.KUTOUTEN_JP))

        self.__auto_start_henkan_keywords.set_text(\
            self.__config.get_value('auto_start_henkan_keywords',
                                    ''.join(skk.AUTO_START_HENKAN_KEYWORDS)))

        self.__page_size.set_numeric(True)
        self.__page_size.set_range(7.0, 21.0)
        self.__page_size.set_value(\
            int(self.__config.get_value('page_size',
                                        skk.CandidateSelector.PAGE_SIZE)))
        self.__pagination_start.set_numeric(True)
        self.__pagination_start.set_range(0.0, 7.0)
        self.__pagination_start.set_value(\
            int(self.__config.get_value('pagination_start',
                                        skk.CandidateSelector.PAGINATION_START)))
        self.__show_annotation.set_active(\
            self.__config.get_value('show_annotation', False))

        self.__usrdict.connect('file-set', self.__usrdict_file_set_cb)
        self.__sysdict_file.connect('toggled', self.__sysdict_toggle_cb)
        self.__sysdict_skkserv.connect('toggled', self.__sysdict_toggle_cb)
        self.__sysdict.connect('file-set', self.__sysdict_file_set_cb)
        self.__skkserv_host.connect('changed', self.__skkserv_host_changed_cb)
        self.__skkserv_port.connect('changed', self.__skkserv_port_changed_cb)
        self.__period_style.connect('changed', self.__period_style_changed_cb)
        self.__auto_start_henkan_keywords.connect(\
            'changed', self.__auto_start_henkan_keywords_changed_cb)
        self.__page_size.connect('changed', self.__page_size_changed_cb)
        self.__pagination_start.connect('changed', self.__pagination_start_changed_cb)
        self.__show_annotation.connect('toggled', self.__show_annotation_changed_cb)

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
        
    def __skkserv_host_changed_cb(self, widget):
        self.__config.set_value('skkserv_host', widget.get_text())

    def __skkserv_port_changed_cb(self, widget):
        self.__config.set_value('skkserv_port', widget.get_text())

    def __period_style_changed_cb(self, widget):
        self.__config.set_value('period_style', widget.get_active())

    def __auto_start_henkan_keywords_changed_cb(self, widget):
        self.__config.set_value('auto_start_henkan_keywords',
                                widget.get_text())

    def __page_size_changed_cb(self, widget):
        self.__config.set_value('page_size', widget.get_value_as_int())

    def __pagination_start_changed_cb(self, widget):
        self.__config.set_value('pagination_start', widget.get_value_as_int())

    def __show_annotation_changed_cb(self, widget):
        self.__config.set_value('show_annotation', widget.get_active())

    def run(self):
        return self.__dialog.run()

def main():
    PreferencesDialog().run()

if __name__ == "__main__":
    main()
