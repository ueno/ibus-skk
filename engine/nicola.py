# vim:set et sts=4 sw=4:
# -*- coding: utf-8 -*-
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (C) 2010 Daiki Ueno <ueno@unixuser.org>
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

NICOLA_RULE = {
    'q': [u'。', u'',   u'ぁ'],
    'w': [u'か', u'が', u'え'],
    'e': [u'た', u'だ', u'り'],
    'r': [u'こ', u'ご', u'ゃ'],
    't': [u'さ', u'ざ', u'れ'],

    'y': [u'ら', u'よ', u'ぱ'],
    'u': [u'ち', u'に', u'ぢ'],
    'i': [u'く', u'る', u'ぐ'],
    'o': [u'つ', u'ま', u'づ'],
    'p': [u'，',  u'ぇ', u'ぴ'],
    '@': [u'、', u'',   u''],
    '[': [u'゛', u'゜', u''],

    'a': [u'う', u'',   u'を'],
    's': [u'し', u'じ', u'あ'],
    'd': [u'て', u'で', u'な'],
    'f': [u'け', u'げ', u'ゅ'],
    'g': [u'せ', u'ぜ', u'も'],

    'h': [u'は', u'み', u'ば'],
    'j': [u'と', u'お', u'ど'],
    'k': [u'き', u'の', u'ぎ'],
    'l': [u'い', u'ょ', u'ぽ'],
    ';': [u'ん', u'っ', u''],

    'z': [u'．',  u'',   u'ぅ'],
    'x': [u'ひ', u'び', u'ー'],
    'c': [u'す', u'ず', u'ろ'],
    'v': [u'ふ', u'ぶ', u'や'],
    'b': [u'へ', u'べ', u'ぃ'],

    'n': [u'め', u'ぬ', u'ぷ'],
    'm': [u'そ', u'ゆ', u'ぞ'],
    ',': [u'ね', u'む', u'ぺ'],
    '.': [u'ほ', u'わ', u'ぼ'],
    '/': [u'・', u'ぉ', u''],

    '1': [u'1',  u'',   u'？'],
    '2': [u'2',  u'',   u'／'],
    '4': [u'4',  u'',   u'「'],
    '5': [u'5',  u'',   u'」'],

    '6': [u'6',  u'［',  u''],
    '7': [u'7',  u'］',  u''],
    '8': [u'8',  u'（',  u''],
    '9': [u'9',  u'）',  u''],
    '\\': [u'￥', u'',  u''],
}

class Event(object):
    def __init__(self, key, time):
        self.__key = key
        self.__time = time

    key = property(lambda self: self.__key)
    time = property(lambda self: self.__time)

class Result(object):
    def __init__(self, output, wait):
        self.__output = output
        self.__wait = wait
        
    output = property(lambda self: self.__output)
    wait = property(lambda self: self.__wait)

LSHIFT, RSHIFT = range(2)
    
def is_shift(event):
    return event.key in ('lshift', 'rshift')

def get_shift(event):
    return ('lshift', 'rshift').index(event.key)

def format_double(a, b):
    if is_shift(a) and is_shift(b):
        return u'[LR]'
    elif is_shift(a):
        return a.key + u'+' + b.key
    elif is_shift(b):
        return b.key + u'+' + a.key
    keys = u''.join(sorted((a.key, b.key)))
    return u'[' + keys + u']'

def decompose_double(double):
    if not double.startswith(u'[') or not double.endswith(u']'):
        return list(double)
    return [c for c in double[1:-1] if c.islower()]

class Nicola(object):
    def __init__(self, time_func, timeout=0.1, overlap=0.05, maxwait=10,
                 special_doubles=(u'[fj]', u'[gh]', u'[dk]', u'[LR]')):
        self.__time_func = time_func
        assert timeout > overlap
        self.__timeout = timeout
        self.__overlap = overlap
        self.__maxwait = maxwait
        self.__special_doubles = special_doubles
        self.__pending = list()
        self.__rsingle = None

    def __make_result(self, output):
        time = self.__time_func()
        self.__pending = [event for event in self.__pending
                          if time - event.time <= self.__timeout]
        if len(self.__pending) > 0:
            wait = self.__timeout - (time - self.__pending[-1].time)
        else:
            wait = self.__maxwait
        return Result(output, wait)

    def peek(self):
        return self.__rsingle or len(self.__pending) > 0

    def queue(self, key):
        time = self.__time_func()
        # press/release a same key
        if key.startswith(u'release+'):
            letter = key[len(u'release+'):]
            if len(self.__pending) > 0 and self.__pending[0].key == letter:
                self.__rsingle = self.__make_result((letter,))
                del self.__pending[0:]
        # ignore key repeat
        elif len(self.__pending) > 0 and self.__pending[0].key == key:
            self.__pending[0] = Event(key, time)
            self.__rsingle = self.__make_result((key,))
        else:
            self.__pending.insert(0, Event(key, time))

    def __dispatch_single(self):
        time = self.__time_func()
        a = self.__pending[0]
        if time - a.time > self.__timeout:
            del self.__pending[0:]
            return self.__make_result((a.key,))
        return self.__make_result(tuple())

    def dispatch(self):
        if self.__rsingle:
            result = self.__rsingle
            self.__rsingle = None
            return result

        # assert len(self.__pending) <= 3
        # abandon events older than the first 3 events
        del self.__pending[3:]
        if len(self.__pending) == 0:
            return self.__make_result(tuple())

        time = self.__time_func()
        # triple key combination
        # http://nicola.sunicom.co.jp/spec/kikaku.htm#04070402
        if len(self.__pending) == 3:
            b, s, a = self.__pending
            t1 = s.time - a.time
            t2 = b.time - s.time
            if t1 <= t2:
                del self.__pending[1:]
                # b may be expired
                r = self.__dispatch_single()
                return self.__make_result((format_double(s, a),) + r.output)
            else:
                del self.__pending[0:]
                return self.__make_result((a.key, format_double(s, b)))
        # double key combination
        elif len(self.__pending) == 2:
            b, a = self.__pending
            if b.time - a.time > self.__overlap:
                del self.__pending[1:]
                # b may be expired
                r = self.__dispatch_single()
                return self.__make_result((a.key,) + r.output)
            # skk-nicola uses some combinations of 2 normal keys
            # ([fj], [gh], etc.)
            if (not is_shift(b) and not is_shift(a)) or \
                    (is_shift(b) and is_shift(a)):
                double = format_double(b, a)
                if double in self.__special_doubles:
                    del self.__pending[0:]
                    return self.__make_result((double,))
                del self.__pending[1:]
                # b may be expired
                r = self.__dispatch_single()
                return self.__make_result((a.key,) + r.output)
            if time - a.time > self.__timeout:
                del self.__pending[0:]
                if is_shift(b):
                    return self.__make_result((format_double(b, a),))
                else:
                    return self.__make_result((format_double(a, b),),)
            return self.__make_result(tuple())
        elif len(self.__pending) == 1:
            return self.__dispatch_single()
        return self.__make_result(tuple())
