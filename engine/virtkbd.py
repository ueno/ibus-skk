# vim:set et sts=4 sw=4:
# -*- coding: utf-8 -*-
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (C) 2011 Daiki Ueno <ueno@unixuser.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from ibus import keysyms
from ibus import modifier

KEYBOARD_TYPE_US, KEYBOARD_TYPE_JP = range(2)

INPUT_MODE_HIRAGANA, \
INPUT_MODE_KATAKANA, \
INPUT_MODE_HALF_WIDTH_KATAKANA, \
INPUT_MODE_LATIN, \
INPUT_MODE_WIDE_LATIN = range(5)

TYPING_MODE_ROMAJI, \
TYPING_MODE_KANA, \
TYPING_MODE_THUMB_SHIFT = range(3)

class VirtualKeyboardFallback(object):
    keyboard_type = property(lambda self: KEYBOARD_TYPE_US)

    def __init__(self, engine):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def set_mode(self, input_mode=None, typing_mode=None):
        pass

    def toggle_keyboard_type(self):
        pass

    def toggle_visible(self):
        pass

class VirtualKeyboardEekboard(object):
    def __init__(self, engine):
        import eekboard, virtkey

        self.__engine = engine
        self.__input_mode = None
        self.__typing_mode = None

        self.__client = eekboard.Client()
        self.__context = self.__client.create_context("ibus-skk")

        self.__keyboard_type_to_id = {
            KEYBOARD_TYPE_US: self.__context.add_keyboard("us"),
            KEYBOARD_TYPE_JP: self.__context.add_keyboard("jp-kana")
            }
        self.__keyboard_id_to_type = dict()
        for k, v in self.__keyboard_type_to_id.iteritems():
            self.__keyboard_id_to_type[v] = k

        self.__keyboard_type = None
        self.__group = 0
        self.__set_keyboard_type(KEYBOARD_TYPE_US)
        self.__set_group(0)
        self.__context.connect('key-pressed', self.__key_pressed_cb)
        self.__context.connect('notify::keyboard', self.__notify_keyboard_cb)
        self.__context.connect('notify::group', self.__notify_group_cb)
        self.__virtkey = virtkey.virtkey()

    keyboard_type = property(lambda self: self.__keyboard_type)

    def enable(self):
        self.__client.push_context(self.__context)

    def disable(self):
        self.__client.pop_context()

    def __set_keyboard_type(self, keyboard_type):
        if self.__keyboard_type != keyboard_type:
            keyboard_id = self.__keyboard_type_to_id[keyboard_type]
            self.__context.set_keyboard(keyboard_id)
            self.__keyboard_type = keyboard_type

    def __set_group(self, group):
        self.__context.set_group(group)

    def __get_keyboard_type_and_group(self, input_mode, typing_mode):
        if typing_mode == TYPING_MODE_KANA:
            if input_mode == INPUT_MODE_HIRAGANA:
                keyboard_type = KEYBOARD_TYPE_JP
                group = 0
            elif input_mode in (INPUT_MODE_KATAKANA,
                                INPUT_MODE_HALF_WIDTH_KATAKANA):
                keyboard_type = KEYBOARD_TYPE_JP
                group = 1
            else:
                keyboard_type = KEYBOARD_TYPE_US
                group = 0
        else:
            keyboard_type = KEYBOARD_TYPE_US
            group = 0
        return (keyboard_type, group)

    def set_mode(self, input_mode=None, typing_mode=None):
        if input_mode == None:
            input_mode = self.__input_mode
        if typing_mode == None:
            typing_mode = self.__typing_mode
        keyboard_type, group = \
            self.__get_keyboard_type_and_group(input_mode, typing_mode)
        self.__set_keyboard_type(keyboard_type)
        self.__set_group(group)
        self.__input_mode = input_mode
        self.__typing_mode = typing_mode

    def toggle_keyboard_type(self):
        if self.__keyboard_type == KEYBOARD_TYPE_US:
            self.__set_keyboard_type(KEYBOARD_TYPE_JP)
            self.__typing_mode = TYPING_MODE_KANA
        else:
            self.__set_keyboard_type(KEYBOARD_TYPE_US)
            self.__typing_mode = TYPING_MODE_ROMAJI
        keyboard_type, group = \
            self.__get_keyboard_type_and_group(self.__input_mode,
                                               self.__typing_mode)
        self.__set_group(group)

    def toggle_visible(self):
        if self.__context.props.visible:
            self.__context.hide_keyboard()
        else:
            self.__context.show_keyboard()

    def __process_key_event(self, symbol, modifiers):
        if hasattr(symbol, 'xkeysym'):
            if self.__engine.process_key_event(symbol.xkeysym, 0, modifiers):
                return True

            # if the event is not handled, pass it back with virtkey
            if modifiers & modifier.RELEASE_MASK:
                self.__virtkey.release_keysym(symbol.xkeysym)
            else:
                self.__virtkey.press_keysym(symbol.xkeysym)
            return True
        else:
            if symbol.name == 'cycle-keyboard' and \
                    (modifiers & modifier.RELEASE_MASK) == 0:
                self.toggle_keyboard_type()
            return True
        return False

    def __key_pressed_cb(self, context, keyname, symbol, modifiers):
        if symbol.modifier_mask != 0:
            return
        self.__process_key_event(symbol, modifiers)
        self.__process_key_event(symbol, modifiers | modifier.RELEASE_MASK)

    def __notify_keyboard_cb(self, context, pspec):
        self.__keyboard_type = self.__keyboard_id_to_type(context.props.keyboard)

    def __notify_group_cb(self, context, pspec):
        self.__group = context.props.group
