# vim:set et sts=4 sw=4:
# -*- coding: utf-8 -*-
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
# Copyright (C) 2009-2010 Daiki Ueno <ueno@unixuser.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import gobject
import ibus
from ibus import keysyms
from ibus import modifier
import sys, os, os.path
import skk

from gettext import dgettext
_  = lambda a : dgettext("ibus-skk", a)
N_ = lambda a : a

# Work-around for older IBus releases.
if not hasattr(ibus, 'ORIENTATION_HORIZONTAL'):
    ibus.ORIENTATION_HORIZONTAL = 0

class CandidateSelector(skk.CandidateSelector):
    def __init__(self, lookup_table, keys, page_size, pagination_start):
        self.__lookup_table = lookup_table
        self.__keys = keys
        super(CandidateSelector, self).__init__(page_size, pagination_start)

    def set_candidates(self, candidates):
        super(CandidateSelector, self).set_candidates(candidates)
        if len(candidates) > self.pagination_start:
            self.__lookup_table.clean()
            for candidate, annotation in candidates[self.pagination_start:]:
                self.__lookup_table.append_candidate(ibus.Text(candidate))

    def lookup_table_visible(self):
        if self.index() >= self.pagination_start:
            return True
        return False
        
    def next_candidate(self, move_over_pages=True):
        super(CandidateSelector, self).next_candidate(move_over_pages)
        if self.lookup_table_visible():
            if self.index() == self.pagination_start:
                self.__lookup_table.set_cursor_pos(0)
            elif not move_over_pages:
                self.__lookup_table.set_cursor_pos(self.index() -
                                                   self.pagination_start)
            else:
                self.__lookup_table.page_down()
                self.__lookup_table.set_cursor_pos_in_current_page(0)
        return self.candidate()

    def previous_candidate(self, move_over_pages=True):
        super(CandidateSelector, self).previous_candidate(move_over_pages)
        if self.lookup_table_visible():
            if self.index() == self.pagination_start:
                self.__lookup_table.set_cursor_pos(0)
            elif not move_over_pages:
                self.__lookup_table.set_cursor_pos(self.index() -
                                                   self.pagination_start)
            else:
                self.__lookup_table.page_up()
                self.__lookup_table.set_cursor_pos_in_current_page(0)
        return self.candidate()

    __emacsclient_paths = ('/usr/bin/emacsclient',
                           '/usr/local/bin/emacsclient')
                     
    def candidate(self):
        candidate = super(CandidateSelector, self).candidate()
        if candidate is None:
            return None
        output, annotation, save = candidate
        if output.startswith(u'(') and output.endswith(u')'):
            for path in self.__emacsclient_paths:
                if os.system('%s --eval \'(ignore)\'' % path) == 0:
                    pw, pr = os.popen2('%s --eval \'\
(read (encode-coding-string (prin1-to-string %s) (quote utf-8)))\'' %
                                       (path, output))
                    output = pr.read().decode('UTF-8').strip()
                    if output.startswith('"') and output.endswith('"'):
                        output = output[1:-1]
                    return (output, annotation, False)
        return candidate

    def set_index(self, index):
        super(CandidateSelector, self).set_index(index)
        if self.index() >= self.pagination_start:
            self.__lookup_table.set_cursor_pos(self.index() -
                                               self.pagination_start)

    def key_to_index(self, key):
        if key not in self.__keys:
            raise IndexError('%s is not a valid key' % key)
        pos = self.__keys.index(key)
        if self.__lookup_table.set_cursor_pos_in_current_page(pos):
            index = self.__lookup_table.get_cursor_pos()
            return self.__pagination_start + index
        else:
            raise IndexError('invalid key position %d' % pos)

class Engine(ibus.EngineBase):
    config = None
    sysdict = None
    __setup_pid = 0

    __select_keys = [u'a', u's', u'd', u'f', u'j', u'k', u'l',
                     u'q', u'w', u'e', u'r', u'u', u'i', u'o',
                     u'z', u'x', u'c', u'v', u'm', u',', u'.']
     
    __input_mode_prop_names = {
        skk.INPUT_MODE_HIRAGANA : u"InputMode.Hiragana",
        skk.INPUT_MODE_KATAKANA : u"InputMode.Katakana",
        skk.INPUT_MODE_LATIN : u"InputMode.Latin",
        skk.INPUT_MODE_WIDE_LATIN : u"InputMode.WideLatin",
        skk.INPUT_MODE_HANKAKU_KATAKANA : u"InputMode.HankakuKatakana"
        }

    __prop_name_input_modes = dict()
    for key, val in __input_mode_prop_names.items():
        __prop_name_input_modes[val] = key

    __input_mode_labels = {
        skk.INPUT_MODE_HIRAGANA : u"あ",
        skk.INPUT_MODE_KATAKANA : u"ア",
        skk.INPUT_MODE_LATIN : u"_A",
        skk.INPUT_MODE_WIDE_LATIN : u"Ａ",
        skk.INPUT_MODE_HANKAKU_KATAKANA : u"_ｱ"
        }

    def __init__(self, bus, object_path):
        super(Engine, self).__init__(bus, object_path)
        self.__is_invalidate = False
        labels = [ibus.Text(c.upper() + u':') for c in self.__select_keys]
        page_size = self.config.get_value('page_size',
                                          skk.CandidateSelector.PAGE_SIZE)
        pagination_start = \
            self.config.get_value('pagination_start',
                                  skk.CandidateSelector.PAGINATION_START)
        self.__lookup_table = ibus.LookupTable(page_size=page_size,
                                               round=False,
                                               labels=labels)
        if hasattr(self.__lookup_table, 'set_orientation'):
            self.__lookup_table.set_orientation(ibus.ORIENTATION_HORIZONTAL)

        self.__candidate_selector = CandidateSelector(self.__lookup_table,
                                                      self.__select_keys,
                                                      page_size,
                                                      pagination_start)
        usrdict = skk.UsrDict(self.config.usrdict_path)
        self.__skk = skk.Context(usrdict, self.sysdict,
                                 self.__candidate_selector)
        self.__skk.kutouten_type = self.config.get_value('period_style',
                                                         skk.KUTOUTEN_JP)
        auto_start_henkan_keywords = \
            self.config.get_value('auto_start_henkan_keywords',
                                  ''.join(skk.AUTO_START_HENKAN_KEYWORDS))
        self.__skk.auto_start_henkan_keywords = \
            list(iter(auto_start_henkan_keywords))
        self.__skk.rom_kana_rule = self.config.get_value('rom_kana_rule',
                                                         skk.ROM_KANA_NORMAL)
        self.__skk.translated_strings['dict-edit-prompt'] =\
            _(u'DictEdit').decode('UTF-8')
        self.__skk.translated_strings['kuten-prompt'] =\
            _(u'Kuten([MM]KKTT) ').decode('UTF-8')
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__prop_dict = dict()
        self.__prop_list = self.__init_props()
        self.__input_mode = self.__skk.input_mode
        self.__update_input_mode()
        self.__suspended_mode = None

    def __init_props(self):
        skk_props = ibus.PropList()

        input_mode_prop = ibus.Property(key=u"InputMode",
                                        type=ibus.PROP_TYPE_MENU,
                                        label=u"あ",
                                        tooltip=_(u"Switch input mode"))
        self.__prop_dict[u"InputMode"] = input_mode_prop

        props = ibus.PropList()
        props.append(ibus.Property(key=u"InputMode.Hiragana",
                                   type=ibus.PROP_TYPE_RADIO,
                                   label=_(u"Hiragana")))
        props.append(ibus.Property(key=u"InputMode.Katakana",
                                   type=ibus.PROP_TYPE_RADIO,
                                   label=_(u"Katakana")))
        props.append(ibus.Property(key=u"InputMode.Latin",
                                   type=ibus.PROP_TYPE_RADIO,
                                   label=_(u"Latin")))
        props.append(ibus.Property(key=u"InputMode.WideLatin",
                                   type=ibus.PROP_TYPE_RADIO,
                                   label=_(u"Wide Latin")))
        props.append(ibus.Property(key=u"InputMode.HankakuKatakana",
                                   type=ibus.PROP_TYPE_RADIO,
                                   label=_(u"HankakuKatakana")))

        props[self.__skk.input_mode].set_state(ibus.PROP_STATE_CHECKED)

        for prop in props:
            self.__prop_dict[prop.key] = prop

        input_mode_prop.set_sub_props(props)
        skk_props.append(input_mode_prop)

        skk_props.append(ibus.Property(key=u"setup",
                                         icon=u"ibus-setup",
                                         tooltip=_(u"Configure SKK")))

        return skk_props

    def __update_input_mode(self):
        if self.__input_mode == self.__skk.input_mode:
            return False
        self.__input_mode = self.__skk.input_mode
        prop_name = self.__input_mode_prop_names[self.__input_mode]
        self.__prop_dict[prop_name].set_state(ibus.PROP_STATE_CHECKED)
        self.update_property(self.__prop_dict[prop_name])
        prop = self.__prop_dict[u"InputMode"]
        prop.label = self.__input_mode_labels[self.__input_mode]
        self.update_property(prop)
        self.__invalidate()

    def process_key_event(self, keyval, keycode, state):
        # ignore key release events
        if state & modifier.RELEASE_MASK:
            return False
        # ignore alt+key events
        if state & modifier.MOD1_MASK:
            return False

        if self.__skk.conv_state == skk.CONV_STATE_SELECT:
            if keyval == keysyms.Page_Up or keyval == keysyms.KP_Page_Up:
                self.page_up()
                return True
            elif keyval == keysyms.Page_Down or keyval == keysyms.KP_Page_Down:
                self.page_down()
                return True
            elif keyval == keysyms.Up or keyval == keysyms.Left:
                self.__skk.previous_candidate(False)
                self.__update()
                return True
            elif keyval == keysyms.Down or keyval == keysyms.Right:
                self.__skk.next_candidate(False)
                self.__update()
                return True
            elif self.__candidate_selector.lookup_table_visible():
                try:
                    index = self.__candidate_selector.\
                        key_to_index(unichr(keyval).lower())
                    handled, output = self.__skk.select_candidate(index)
                    if handled:
                        if output:
                            self.commit_text(ibus.Text(output))
                        gobject.idle_add(self.__skk.usrdict.save,
                                         priority = gobject.PRIORITY_LOW)
                        self.__lookup_table.clean()
                        self.__update()
                        return True
                except IndexError:
                    pass

        if keyval == keysyms.Tab:
            keychr = u'\t'
        elif keyval == keysyms.Return:
            keychr = u'return'
        elif keyval == keysyms.Escape:
            keychr = u'escape'
        elif keyval == keysyms.BackSpace:
            keychr = u'backspace'
        else:
            keychr = unichr(keyval)
            if 0x20 > ord(keychr) or ord(keychr) > 0x7E:
                return False
        if keychr.isalpha():
            keychr = keychr.lower()
        if state & modifier.SHIFT_MASK:
            keychr = u'shift+' + keychr
        if state & modifier.CONTROL_MASK:
            keychr = u'ctrl+' + keychr
        handled, output = self.__skk.press_key(keychr)
        if handled:
            if output:
                self.commit_text(ibus.Text(output))
            gobject.idle_add(self.__skk.usrdict.save,
                             priority = gobject.PRIORITY_LOW)
            self.__update()
            return True
        return False

    def __invalidate(self):
        if self.__is_invalidate:
            return
        self.__is_invalidate = True
        gobject.idle_add(self.__update, priority = gobject.PRIORITY_LOW)

    def page_up(self):
        if self.__lookup_table.page_up():
            self.page_up_lookup_table()
            return True
        return False

    def page_down(self):
        if self.__lookup_table.page_down():
            self.page_down_lookup_table()
            return True
        return False

    def cursor_up(self):
        if self.__lookup_table.cursor_up():
            self.cursor_up_lookup_table()
            return True
        return False

    def cursor_down(self):
        if self.__lookup_table.cursor_down():
            self.cursor_down_lookup_table()
            return True
        return False

    def __possibly_update_config(self):
        if self.__skk.usrdict.path != self.config.usrdict_path:
            self.__skk.usrdict = skk.UsrDict(self.config.usrdict_path)
        self.__skk.kutouten_type = self.config.get_value('period_style',
                                                         skk.KUTOUTEN_JP)
        self.__skk.rom_kana_rule = self.config.get_value('rom_kana_rule',
                                                         skk.ROM_KANA_NORMAL)
        self.__skk.auto_start_henkan_keywords = \
            list(iter(self.config.get_value('auto_start_henkan_keywords',
                                            ''.join(skk.AUTO_START_HENKAN_KEYWORDS))))

    # ABBREV_CURSOR_COLOR = (65, 105, 225)
    # INPUT_MODE_CURSOR_COLORS = {
    #     skk.INPUT_MODE_HIRAGANA: (139, 62, 47),
    #     skk.INPUT_MODE_KATAKANA: (34, 139, 34),
    #     skk.INPUT_MODE_LATIN: (139, 139, 131),
    #     skk.INPUT_MODE_WIDE_LATIN: (255, 215, 0),
    #     skk.INPUT_MODE_HANKAKU_KATAKANA: (138, 43, 226)
    #     }

    def __update(self):
        prompt, prefix, word, suffix = self.__skk.preedit_components()
        prefix_start = len(prompt)
        word_start = prefix_start + len(prefix)
        suffix_start = word_start + len(word)
        suffix_end = suffix_start + len(suffix)
        attrs = ibus.AttrList()
        # Display "[DictEdit]" way different from other components
        # (black/lightsalmon).
        attrs.append(ibus.AttributeForeground(ibus.RGB(0, 0, 0),
                                              0, prefix_start))
        attrs.append(ibus.AttributeBackground(ibus.RGB(255, 160, 122),
                                              0, prefix_start))
        if self.__skk.conv_state == skk.CONV_STATE_SELECT:
            # Use colors from skk-henkan-face-default (black/darkseagreen2).
            attrs.append(ibus.AttributeForeground(ibus.RGB(0, 0, 0),
                                                  word_start, suffix_start))
            attrs.append(ibus.AttributeBackground(ibus.RGB(180, 238, 180),
                                                  word_start, suffix_start))
            attrs.append(ibus.AttributeUnderline(ibus.ATTR_UNDERLINE_SINGLE,
                                                 suffix_start, suffix_end))
        else:
            attrs.append(ibus.AttributeUnderline(ibus.ATTR_UNDERLINE_SINGLE,
                                                 word_start, suffix_end))
        # Color cursor, currently disabled.
        #
        # if self.__skk.abbrev:
        #     cursor_color = self.ABBREV_CURSOR_COLOR
        # else:
        #     cursor_color = self.INPUT_MODE_CURSOR_COLORS.get(\
        #         self.__skk.input_mode)
        # attrs.append(ibus.AttributeBackground(ibus.RGB(*cursor_color),
        #                                       suffix_end, suffix_end + 1))
        # preedit = ''.join((prompt, prefix, word, suffix, u' '))
        #
        preedit = ''.join((prompt, prefix, word, suffix))
        self.update_preedit_text(ibus.Text(preedit, attrs),
                                 len(preedit), len(preedit) > 0)
        visible = self.__candidate_selector.lookup_table_visible()
        if self.config.get_value('show_annotation', True):
            candidate = self.__candidate_selector.candidate()
            annotation = candidate[1] if candidate else None
            self.update_auxiliary_text(ibus.Text(annotation or u''), visible)
        self.update_lookup_table(self.__lookup_table, visible)
        self.__update_input_mode()

        if self.__skk.conv_state is not skk.CONV_STATE_SELECT:
            gobject.idle_add(self.__possibly_update_config,
                             priority = gobject.PRIORITY_LOW)

        self.__is_invalidate = False

    def fill_lookup_table(self, candidates):
        self.__lookup_table.clean()
        for candidate in candidates:
            self.__lookup_table.append_candidate(ibus.Text(candidate))
        self.__lookup_table_hidden = False

    def lookup_table_visible(self):
        return not self.__lookup_table_hidden and \
            self.__lookup_table.get_number_of_candidates() > 1

    def show_lookup_table(self):
        self.__lookup_table_hidden = False
        super(Engine, self).show_lookup_table()

    def hide_lookup_table(self):
        self.__lookup_table_hidden = True
        super(Engine, self).hide_lookup_table()

    def __start_setup(self):
        if Engine.__setup_pid != 0:
            pid, state = os.waitpid(Engine.__setup_pid, os.P_NOWAIT)
            if pid != Engine.__setup_pid:
                return
            Engine.__setup_pid = 0
        setup_cmd = os.path.join(os.getenv('LIBEXECDIR'), 'ibus-setup-skk')
        Engine.__setup_pid = os.spawnl(os.P_NOWAIT, setup_cmd, 'ibus-setup-skk')

    def focus_in(self):
        self.register_properties(self.__prop_list)
        # skipped at first focus_in after ibus startup
        if self.__suspended_mode is not None:
            self.__skk.activate_input_mode(self.__suspended_mode)
            self.__suspended_mode = None
        self.__update_input_mode()

    def focus_out(self):
        self.__suspended_mode = self.__skk.input_mode
        # self.__skk.kakutei()
        # self.commit_text(ibus.Text(u''))
        self.__lookup_table.clean()
        self.__update()
        self.reset()

    def reset(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)

    def property_activate(self, prop_name, state):
        # print "PropertyActivate(%s, %d)" % (prop_name, state)
        if state == ibus.PROP_STATE_CHECKED:
            input_mode = self.__prop_name_input_modes[prop_name]
            self.__skk.activate_input_mode(input_mode)
            self.__update_input_mode()
        else:
            if prop_name == 'setup':
                self.__start_setup()
