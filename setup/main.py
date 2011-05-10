import gtk
import locale
import os, sys
import config
import gettext

from gettext import dgettext
_  = lambda a : dgettext("ibus-skk", a)
N_ = lambda a : a

def get_index_by_value (widget, value):
    model = widget.get_model()
    _iter = model.get_iter_root()
    index = 0
    _value = None
    while _iter:
        _value, = model.get(_iter, 1)
        if _value == value:
            return index
        index += 1
        _iter = model.iter_next(_iter)
    
class PreferencesDialog:
    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        localedir = os.getenv('IBUS_LOCALEDIR')
        # for non-standard localedir (Issue#27)
        locale.bindtextdomain('ibus-skk', localedir)
        gettext.bindtextdomain('ibus-skk', localedir)
        gettext.bind_textdomain_codeset('ibus-skk', 'UTF-8')

        self.__config = config.Config()
        self.__builder = gtk.Builder()
        self.__builder.set_translation_domain('ibus-skk')
        self.__builder.add_from_file('ibus-skk-preferences.ui')
        self.__dialog = self.__builder.get_object('dialog')

        self.__usrdict = self.__builder.get_object('usrdict')
        self.__use_skkserv = self.__builder.get_object('use_skkserv')
        self.__skkserv_host = self.__builder.get_object('skkserv_host')
        self.__skkserv_port = self.__builder.get_object('skkserv_port')
        self.__sysdict = self.__builder.get_object('sysdict')
        self.__sysdict_liststore = self.__builder.get_object('sysdict_liststore')
        self.__add_sysdict = self.__builder.get_object('add_sysdict')
        self.__remove_sysdict = self.__builder.get_object('remove_sysdict')
        self.__up_sysdict = self.__builder.get_object('up_sysdict')
        self.__down_sysdict = self.__builder.get_object('down_sysdict')
        self.__period_style = self.__builder.get_object('period_style')
        self.__page_size = self.__builder.get_object('page_size')
        self.__pagination_start = self.__builder.get_object('pagination_start')
        self.__show_annotation = self.__builder.get_object('show_annotation')
        self.__auto_start_henkan_keywords = \
            self.__builder.get_object('auto_start_henkan_keywords')
        self.__rom_kana_rule = self.__builder.get_object('rom_kana_rule')
        self.__initial_input_mode = \
            self.__builder.get_object('initial_input_mode')
        self.__egg_like_newline = self.__builder.get_object('egg_like_newline')
        self.__use_nicola = self.__builder.get_object('use_nicola')

        self.__usrdict.set_filename(self.__config.usrdict_path)
        sysdict_type = self.__config.get_value('sysdict_type')
        if sysdict_type == 'skkserv':
            self.__use_skkserv.set_active(True)
        self.__set_sysdict_widgets_sensitivity(sysdict_type)

        # sysdict treeview
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("path", renderer, text=0)
        self.__sysdict.append_column(column)
        for path in self.__config.sysdict_paths:
            self.__sysdict_liststore.append((path,))

        self.__skkserv_host.set_text(\
            self.__config.get_value('skkserv_host'))
        self.__skkserv_port.set_numeric(True)
        self.__skkserv_port.set_range(0.0, 65535.0)
        self.__skkserv_port.set_value(\
            int(self.__config.get_value('skkserv_port')))

        renderer = gtk.CellRendererText()
        self.__period_style.pack_start(renderer)
        self.__period_style.set_attributes(renderer, text=0)
        index = get_index_by_value(\
            self.__period_style,
            self.__config.get_value('period_style'))
        self.__period_style.set_active(index)

        self.__auto_start_henkan_keywords.set_text(\
            self.__config.get_value('auto_start_henkan_keywords'))

        self.__page_size.set_numeric(True)
        self.__page_size.set_range(7.0, 21.0)
        self.__page_size.set_value(\
            int(self.__config.get_value('page_size')))
        self.__pagination_start.set_numeric(True)
        self.__pagination_start.set_range(0.0, 7.0)
        self.__pagination_start.set_value(\
            int(self.__config.get_value('pagination_start')))
        self.__show_annotation.set_active(\
            self.__config.get_value('show_annotation'))

        renderer = gtk.CellRendererText()
        self.__rom_kana_rule.pack_start(renderer)
        self.__rom_kana_rule.set_attributes(renderer, text=0)
        index = get_index_by_value(\
            self.__rom_kana_rule,
            self.__config.get_value('rom_kana_rule'))
        self.__rom_kana_rule.set_active(index)

        renderer = gtk.CellRendererText()
        self.__initial_input_mode.pack_start(renderer)
        self.__initial_input_mode.set_attributes(renderer, text=0)
        index = get_index_by_value(\
            self.__initial_input_mode,
            self.__config.get_value('initial_input_mode'))
        self.__initial_input_mode.set_active(index)

        self.__egg_like_newline.set_active(\
            self.__config.get_value('egg_like_newline'))

        self.__use_nicola.set_active(\
            self.__config.get_value('use_nicola'))

        self.__usrdict.connect('file-set', self.__usrdict_file_set_cb)
        self.__use_skkserv.connect('toggled', self.__use_skkserv_toggle_cb)
        self.__skkserv_host.connect('changed', self.__skkserv_host_changed_cb)
        self.__skkserv_port.connect('changed', self.__skkserv_port_changed_cb)
        self.__sysdict.get_selection().connect_after('changed',
                                                     self.__sysdict_selection_changed_cb)
        self.__add_sysdict.connect('clicked', self.__add_sysdict_clicked_cb)
        self.__remove_sysdict.connect('clicked', self.__remove_sysdict_clicked_cb)
        self.__up_sysdict.connect('clicked', self.__up_sysdict_clicked_cb)
        self.__down_sysdict.connect('clicked', self.__down_sysdict_clicked_cb)
        self.__period_style.connect('changed', self.__period_style_changed_cb)
        self.__auto_start_henkan_keywords.connect(\
            'changed', self.__auto_start_henkan_keywords_changed_cb)
        self.__page_size.connect('changed', self.__page_size_changed_cb)
        self.__pagination_start.connect('changed', self.__pagination_start_changed_cb)
        self.__show_annotation.connect('toggled', self.__show_annotation_changed_cb)
        self.__rom_kana_rule.connect('changed', self.__rom_kana_rule_changed_cb)
        self.__initial_input_mode.connect('changed', self.__initial_input_mode_changed_cb)
        self.__egg_like_newline.connect('toggled', self.__egg_like_newline_changed_cb)
        self.__use_nicola.connect('toggled', self.__use_nicola_changed_cb)

    def __set_sysdict_widgets_sensitivity(self, sysdict_type):
        if sysdict_type == 'file':
            self.__sysdict.set_sensitive(True)
            self.__add_sysdict.set_sensitive(True)
            self.__skkserv_host.set_sensitive(False)
            self.__skkserv_port.set_sensitive(False)
            self.__sysdict_entry_buttons_set_sensitivity(\
                self.__sysdict.get_selection().get_selected()[1] is not None)
        else:
            self.__sysdict.set_sensitive(False)
            self.__add_sysdict.set_sensitive(False)
            self.__skkserv_host.set_sensitive(True)
            self.__skkserv_port.set_sensitive(True)
            self.__sysdict_entry_buttons_set_sensitivity(False)

    def __sysdict_entry_buttons_set_sensitivity(self, sensitive):
        self.__remove_sysdict.set_sensitive(sensitive)
        self.__up_sysdict.set_sensitive(sensitive)
        self.__down_sysdict.set_sensitive(sensitive)

    def __set_sysdict_from_model(self, model):
        paths = list()
        _iter = model.get_iter_root()
        while _iter:
            value, = model.get(_iter, 0)
            paths.append(value)
            _iter = model.iter_next(_iter)
        self.__config.set_value('sysdict_paths', paths)
        
    # Callbacks
    def __usrdict_file_set_cb(self, widget):
        self.__config.set_value('usrdict', widget.get_filename())
        
    def __use_skkserv_toggle_cb(self, widget):
        sysdict_type = 'skkserv' if self.__use_skkserv.get_active() else 'file'
        self.__config.set_value('sysdict_type', sysdict_type)
        self.__set_sysdict_widgets_sensitivity(sysdict_type)

    def __skkserv_host_changed_cb(self, widget):
        self.__config.set_value('skkserv_host', widget.get_text())

    def __skkserv_port_changed_cb(self, widget):
        self.__config.set_value('skkserv_port', widget.get_text())

    def __sysdict_selection_changed_cb(self, selection):
        self.__sysdict_entry_buttons_set_sensitivity(\
            selection.get_selected()[1] is not None)

    def __add_sysdict_clicked_cb(self, widget):
        chooser = gtk.FileChooserDialog(\
            title=_("Open Dictionary File"),
            parent=self.__dialog,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        if chooser.run() == gtk.RESPONSE_OK:
            model = self.__sysdict.get_model()
            path = chooser.get_filename()
            _iter = model.get_iter_root()
            while _iter:
                _value, = model.get(_iter, 0)
                if _value == path:
                    break
                _iter = model.iter_next(_iter)
            if not _iter:
                model.append((path,))
                self.__set_sysdict_from_model(model)
        chooser.hide()

    def __remove_sysdict_clicked_cb(self, widget):
        model, paths = self.__sysdict.get_selection().get_selected_rows()
        for path in paths:
            model.remove(model.get_iter(path))
        self.__set_sysdict_from_model(model)

    def __up_sysdict_clicked_cb(self, widget):
        model, _iter = self.__sysdict.get_selection().get_selected()
        if _iter:
            path = model.get_path(_iter)
            if path[0] > 0:
                model.move_before(_iter, model.get_iter((path[0] - 1,)))
                self.__set_sysdict_from_model(model)

    def __down_sysdict_clicked_cb(self, widget):
        model, _iter = self.__sysdict.get_selection().get_selected()
        if _iter:
            path = model.get_path(_iter)
            if path[0] < len(model) - 1:
                model.move_after(_iter, model.get_iter((path[0] + 1,)))
                self.__set_sysdict_from_model(model)

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

    def __rom_kana_rule_changed_cb(self, widget):
        self.__config.set_value('rom_kana_rule', widget.get_active())

    def __initial_input_mode_changed_cb(self, widget):
        _iter = widget.get_active_iter()
        if _iter:
            val, = widget.get_model().get(_iter, 1)
            self.__config.set_value('initial_input_mode', val)

    def __egg_like_newline_changed_cb(self, widget):
        self.__config.set_value('egg_like_newline', widget.get_active())

    def __use_nicola_changed_cb(self, widget):
        self.__config.set_value('use_nicola', widget.get_active())

    def run(self):
        if self.__dialog.run() == gtk.RESPONSE_OK:
            self.__config.commit_all()

def main():
    PreferencesDialog().run()

if __name__ == "__main__":
    main()
