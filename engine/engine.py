# vim:set et sts=4 sw=4:
# -*- coding: utf-8 -*-
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
# Copyright (C) 2009 Daiki Ueno <ueno@unixuser.org>
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
import pango
import ibus
from ibus import keysyms
from ibus import modifier
import sys, os, os.path
import skk

from gettext import dgettext
_  = lambda a : dgettext("ibus-skk", a)
N_ = lambda a : a

class CandidateSelector(skk.CandidateSelectorBase):
    def __init__(self, engine):
        self.__engine = engine
        super(CandidateSelector, self).__init__()

    def set_candidates(self, candidates):
        self.__engine.fill_lookup_table(map(lambda (candidate, annotation):
                                                candidate,
                                            candidates))
        self.__candidate = None
        super(CandidateSelector, self).set_candidates(candidates)

    def next_candidate(self):
        if self.__candidate:
            self.__engine.cursor_down()
        self.__candidate = \
            super(CandidateSelector, self).next_candidate()
        return self.__candidate

    def previous_candidate(self):
        if self.__candidate:
            self.__engine.cursor_up()
        self.__candidate = \
            super(CandidateSelector, self).previous_candidate()
        return self.__candidate

    def current_candidate(self):
        return self.__candidate

class Engine(ibus.EngineBase):
    config = None
    sysdict = None
    __setup_pid = 0

    __labels = [u'a', u's', u'd', u'f', u'j', u'k', u'l']
     
    def __init__(self, bus, object_path):
        super(Engine, self).__init__(bus, object_path)
        self.__is_invalidate = False
        labels = [ibus.Text(label) for label in self.__labels]
        page_size = self.config.get_value('page_size', 7)
        self.__lookup_table = ibus.LookupTable(page_size=page_size,
                                               labels=labels,
                                               round=False)
        
        usrdict = skk.UsrDict(self.config.usrdict_path)
        self.__skk = skk.Context(usrdict, self.sysdict)
        self.__skk.kutouten_type = self.config.get_value('period_style',
                                                         skk.KUTOUTEN_JP)
        self.__skk.auto_start_henkan_keywords = \
            list(iter(self.config.get_value('auto_start_henkan_keywords',
                                            ''.join(skk.AUTO_START_HENKAN_KEYWORDS))))
        self.__candidate_selector = CandidateSelector(self)
        self.__skk.set_candidate_selector(self.__candidate_selector)
        self.__prop_dict = dict()
        self.__prop_list = self.__init_props()
        self.__input_modes = {
            skk.INPUT_MODE_HIRAGANA : u"InputMode.Hiragana",
            skk.INPUT_MODE_KATAKANA : u"InputMode.Katakana",
            skk.INPUT_MODE_LATIN : u"InputMode.Latin",
            skk.INPUT_MODE_WIDE_LATIN : u"InputMode.WideLatin"
            }
        self.__input_mode = self.__skk.input_mode
        self.__input_mode_activate(self.__input_modes[self.__skk.input_mode],
                                   ibus.PROP_STATE_CHECKED)

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

        props[self.__skk.input_mode].set_state(ibus.PROP_STATE_CHECKED)

        for prop in props:
            self.__prop_dict[prop.key] = prop

        input_mode_prop.set_sub_props(props)
        skk_props.append(input_mode_prop)

        skk_props.append(ibus.Property(key=u"setup",
                                         icon=u"ibus-setup",
                                         tooltip=_(u"Configure SKK")))

        return skk_props

    def __input_mode_activate(self, prop_name, state):
        if not prop_name.startswith(u"InputMode."):
            return False

        input_modes = {
            u"InputMode.Hiragana" : (skk.INPUT_MODE_HIRAGANA, u"あ"),
            u"InputMode.Katakana" : (skk.INPUT_MODE_KATAKANA, u"ア"),
            u"InputMode.Latin" : (skk.INPUT_MODE_LATIN, u"_A"),
            u"InputMode.WideLatin" : (skk.INPUT_MODE_WIDE_LATIN, u"Ａ"),
        }

        if prop_name not in input_modes:
            print >> sys.stderr, "Unknow prop_name = %s" % prop_name
            return True
        self.__prop_dict[prop_name].set_state(state)
        self.update_property(self.__prop_dict[prop_name])

        mode, label = input_modes[prop_name]
        if self.__input_mode == mode:
            return True

        self.__input_mode = mode
        prop = self.__prop_dict[u"InputMode"]
        prop.label = label
        self.update_property(prop)
        self.__invalidate()

    def process_key_event(self, keyval, keycode, state):
        # ignore key release events
        if state & modifier.RELEASE_MASK:
            return False
        # ignore alt+key events
        if state & modifier.MOD1_MASK:
            return False

        if self.__skk.conv_state in (skk.CONV_STATE_START,
                                     skk.CONV_STATE_SELECT):
            if keyval == keysyms.Return or \
                    (keyval in (keysyms.j, keysyms.J) and \
                         state & modifier.CONTROL_MASK != 0):
                self.commit_text(ibus.Text(self.__skk.kakutei()))
                gobject.idle_add(self.__skk.usrdict.save,
                                 priority = gobject.PRIORITY_LOW)
                self.__lookup_table.clean()
                self.__update()
                return True
            elif keyval == keysyms.Escape:
                self.__skk.kakutei()
                self.__lookup_table.clean()
                self.__update()
                return True

        if keyval == keysyms.BackSpace:
            handled, output = self.__skk.delete_char()
            if handled:
                if output:
                    self.commit_text(ibus.Text(output))
                self.__update()
                return True
            return False
                
        if self.__skk.conv_state == skk.CONV_STATE_SELECT:
            if keyval == keysyms.Page_Up or keyval == keysyms.KP_Page_Up:
                self.page_up()
                return True
            elif keyval == keysyms.Page_Down or keyval == keysyms.KP_Page_Down:
                self.page_down()
                return True
            elif keyval == keysyms.Up:
                keyval = keysyms.x
            elif keyval == keysyms.Down:
                keyval = keysyms.space
            elif unichr(keyval) in self.__labels:
                pos = self.__labels.index(unichr(keyval))
                if self.__lookup_table.set_cursor_pos_in_current_page(pos):
                    candidate = self.__lookup_table.get_current_candidate().text
                    self.__skk.kakutei()
                    self.__lookup_table.clean()
                    self.commit_text(ibus.Text(candidate))
                    self.__update()
                    return True

        keychr = unichr(keyval)
        if keyval == keysyms.Tab:
            keychr = u'\t'
        elif 0x20 > ord(keychr) or ord(keychr) > 0x7E:
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
        self.__skk.kutouten_type = self.config.get_value('period_style', 0)
        self.__skk.auto_start_henkan_keywords = \
            list(iter(self.config.get_value('auto_start_henkan_keywords',
                                            ''.join(skk.AUTO_START_HENKAN_KEYWORDS))))

    def __update(self):
        prefix, midasi, suffix = self.__skk.split_preedit()
        midasi_start = len(prefix)
        suffix_start = midasi_start + len(midasi)
        suffix_end = suffix_start + len(suffix)
        attrs = ibus.AttrList()
        if self.__skk.conv_state == skk.CONV_STATE_SELECT:
            # Use colors from skk-henkan-face-default (black/darkseagreen2).
            attrs.append(ibus.AttributeForeground(ibus.RGB(0, 0, 0),
                                                  midasi_start, suffix_start))
            attrs.append(ibus.AttributeBackground(ibus.RGB(180, 238, 180),
                                                  midasi_start, suffix_start))
            attrs.append(ibus.AttributeUnderline(pango.UNDERLINE_SINGLE,
                                                 suffix_start, suffix_end))
        else:
            attrs.append(ibus.AttributeUnderline(pango.UNDERLINE_SINGLE,
                                                 midasi_start, suffix_end))
        preedit = ''.join((prefix, midasi, suffix))
        self.update_preedit_text(ibus.Text(preedit, attrs),
                                 len(preedit), len(preedit) > 0)
        visible = self.__lookup_table.get_number_of_candidates() > 1
        current_candidate = self.__candidate_selector.current_candidate()
        annotation = current_candidate[1] if current_candidate else None
        self.update_auxiliary_text(ibus.Text(annotation or u''), visible)
        self.update_lookup_table(self.__lookup_table, visible)
        self.__input_mode_activate(self.__input_modes[self.__skk.input_mode],
                                   ibus.PROP_STATE_CHECKED)

        if self.__skk.conv_state is not skk.CONV_STATE_SELECT:
            gobject.idle_add(self.__possibly_update_config,
                             priority = gobject.PRIORITY_LOW)

        self.__is_invalidate = False

    def fill_lookup_table(self, candidates):
        self.__lookup_table.clean()
        for candidate in candidates:
            self.__lookup_table.append_candidate(ibus.Text(candidate))

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

    def focus_out(self):
        self.reset()

    def reset(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)

    def property_activate(self, prop_name, state):
        # print "PropertyActivate(%s, %d)" % (prop_name, state)
        if state == ibus.PROP_STATE_CHECKED:
            self.__input_mode_activate(prop_name, state)
        else:
            if prop_name == 'setup':
                self.__start_setup()
