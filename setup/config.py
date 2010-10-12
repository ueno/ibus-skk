from __future__ import with_statement
import ibus
import os, os.path, sys
import dbus
import json

sys.path.insert(0, os.path.join(os.getenv('IBUS_SKK_PKGDATADIR'), 'engine'))
import skk

class Config:
    __sysdict_paths = ('/usr/share/skk/SKK-JISYO',
                       '/usr/share/skk/SKK-JISYO.L',
                       '/usr/local/share/skk/SKK-JISYO',
                       '/usr/local/share/skk/SKK-JISYO.L')
    __usrdict_path_unexpanded = '~/.skk-ibus-jisyo'
    __config_path_unexpanded = '~/.config/ibus-skk.json'
    __defaults = {
        'sysdict_type': 'file',
        'use_mmap': True,
        'skkserv_host': skk.SkkServ.HOST,
        'skkserv_port': skk.SkkServ.PORT,
        'period_style': skk.KUTOUTEN_JP,
        'auto_start_henkan_keywords': ''.join(skk.AUTO_START_HENKAN_KEYWORDS),
        'page_size': skk.CandidateSelector.PAGE_SIZE,
        'pagination_start': skk.CandidateSelector.PAGINATION_START,
        'show_annotation': True,
        'rom_kana_rule': skk.ROM_KANA_NORMAL,
        'initial_input_mode': skk.INPUT_MODE_HIRAGANA,
        'egg_like_newline': True,
        'custom_rom_kana_rule': dbus.Dictionary(signature='sv'),
        }

    def __init__(self, bus=ibus.Bus()):
        self.__bus = bus
        self.__config = self.__bus.get_config()
        config_path = os.path.expanduser(self.__config_path_unexpanded)
        try:
            with open(config_path, 'r') as f:
                self.__config_from_file = json.load(f)
        except:
            # print "Can't read config file: %s" % self.__config_path_unexpanded
            self.__config_from_file = dict()
        
    def __sysdict_path(self):
        for path in self.__sysdict_paths:
            if os.path.exists(path):
                return path
    sysdict_path = property(lambda self: self.__get_value(\
            'sysdict', self.__sysdict_path()))

    def sysdict_paths(self):
        return self.__get_value('sysdict_paths',
                                [self.sysdict_path] if self.sysdict_path else dbus.Array(signature='s'))

    def __usrdict_path(self):
        usrdict_path = os.path.expanduser(self.__usrdict_path_unexpanded)
        open(usrdict_path, 'a+').close()
        return usrdict_path
    usrdict_path = property(lambda self: self.__get_value('usrdict', self.__usrdict_path()))

    def get_value(self, name):
        return self.__get_value(name, self.__defaults.get(name))

    def __get_value(self, name, defval=None):
        value = self.__config_from_file.get(name)
        if value is not None:
            return value
        value = self.__config.get_value('engine/SKK', name, None)
        if value is not None:
            return value
        self.set_value(name, defval)
        return defval

    def set_value(self, name, value):
        if value is not None:
            self.__config.set_value('engine/SKK', name, value)
