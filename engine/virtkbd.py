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

try:
    import eekboard, virtkey
    factory_class_name = 'VirtualKeyboardEekboard'
except ImportError:
    factory_class_name = 'VirtualKeyboard'

KEYBOARD_TYPE_US, KEYBOARD_TYPE_JP = range(2)

INPUT_MODE_HIRAGANA, \
INPUT_MODE_KATAKANA, \
INPUT_MODE_HALF_WIDTH_KATAKANA, \
INPUT_MODE_LATIN, \
INPUT_MODE_WIDE_LATIN = range(5)

class VirtualKeyboard(object):
    keyboard_type = property(lambda self: KEYBOARD_TYPE_US)

    def __init__(self, engine):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def set_input_mode(self, input_mode):
        pass

    def set_keyboard_type(self, keyboard_type):
        pass

    def toggle_keyboard_type(self):
        pass

    def toggle_visible(self):
        pass

class VirtualKeyboardEekboard(VirtualKeyboard):
    def __init__(self, engine):
        self.__engine = engine
        self.__input_mode = None

        self.__client = eekboard.Client()
        self.__context = self.__client.create_context("ibus-skk")

        self.__keyboards = {
            KEYBOARD_TYPE_US: self.__context.add_keyboard("us"),
            KEYBOARD_TYPE_JP: self.__context.add_keyboard("jp-kana")
            }
        self.set_keyboard_type(KEYBOARD_TYPE_US)
        self.__context.connect('key-pressed', self.__key_pressed_cb)
        self.__virtkey = virtkey.virtkey()

    keyboard_type = property(lambda self: self.__keyboard_type)

    def enable(self):
        self.__client.push_context(self.__context)

    def disable(self):
        self.__client.pop_context()

    def __set_group(self):
        if self.__keyboard_type == KEYBOARD_TYPE_US:
            self.__context.set_group(0)
        else:
            if self.__input_mode == INPUT_MODE_HIRAGANA:
                self.__context.set_group(0)
            elif self.__input_mode == INPUT_MODE_KATAKANA:
                self.__context.set_group(1)

    def set_input_mode(self, input_mode):
        self.__input_mode = input_mode
        self.__set_group()

    def set_keyboard_type(self, keyboard_type):
        self.__keyboard_type = keyboard_type
        self.__context.set_keyboard(self.__keyboards[keyboard_type])
        self.__set_group()

    def toggle_keyboard_type(self):
        if self.__keyboard_type == KEYBOARD_TYPE_US:
            self.set_keyboard_type(KEYBOARD_TYPE_JP)
        else:
            self.set_keyboard_type(KEYBOARD_TYPE_US)

    def toggle_visible(self):
        if self.__context.props.visible:
            self.__context.hide_keyboard()
        else:
            self.__context.show_keyboard()

    def __process_key_event(self, symbol, modifiers):
        if type(symbol) == eekboard.Symbol:
            if symbol.name == 'cycle-keyboard' and \
                    (modifiers & modifier.RELEASE_MASK) == 0:
                self.toggle_keyboard_type()
            return True

        if isinstance(symbol, eekboard.Keysym):
            if self.__engine.process_key_event(symbol.xkeysym, 0, modifiers):
                return True

            # if the event is not handled, pass it back with virtkey
            if modifiers & modifier.RELEASE_MASK:
                self.__virtkey.release_keysym(symbol.xkeysym)
            else:
                self.__virtkey.press_keysym(symbol.xkeysym)
            return True
        return False

    def __key_pressed_cb(self, context, keyname, symbol, modifiers):
        if symbol.modifier_mask != 0:
            return
        self.__process_key_event(symbol, modifiers)
        self.__process_key_event(symbol, modifiers | modifier.RELEASE_MASK)

def create_virtual_keyboard(engine):
    factory_class = globals().get(factory_class_name, VirtualKeyboard)
    return factory_class(engine)

