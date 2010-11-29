from __future__ import with_statement
import ibus
import os, os.path, sys
import dbus
import json

sys.path.insert(0, os.path.join(os.getenv('IBUS_SKK_PKGDATADIR'), 'engine'))
import skk

class Config:
    __sysdict_path_candidates = ('/usr/share/skk/SKK-JISYO',
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
        'use_nicola': False,
        }

    # Options which can only be specified in ~/.config/ibus-skk.json.
    # This is a workaround for that currently IBus does not allows
    # several complex types (e.g. dictionary) to be stored in its
    # config mechanism.
    __file_defaults = {
        'custom_rom_kana_rule': dict()
        }

    __modified = dict()

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
        self.fetch_all()

    def fetch_all(self):
        for name in self.__defaults.keys():
            print 'get_value engine/SKK/%s' % name
            value = self.__config.get_value('engine/SKK', name, None)
            if value is not None:
                self.__modified[name] = value

    def commit_all(self):
        for name in self.__defaults.keys():
            value = self.__modified[name]
            if value is not None:
                print 'set_value engine/SKK/%s' % name
                self.__config.set_value('engine/SKK', name, value)
        
    def __sysdict_path(self):
        path = self.get_value('sysdict')
        if path is not None:
            return path
        for path in self.__sysdict_path_candidates:
            if os.path.exists(path):
                return path
        return None

    def __sysdict_paths(self):
        paths = self.get_value('sysdict_paths')
        if paths is not None:
            return paths
        path = self.__sysdict_path()
        if path:
            return [path]
        else:
            return dbus.Array(signature='s')
    sysdict_paths = property(lambda self: self.__sysdict_paths())

    def __usrdict_path(self):
        path = self.get_value('usrdict')
        if path is not None:
            return path
        return os.path.expanduser(self.__usrdict_path_unexpanded)
    usrdict_path = property(lambda self: self.__usrdict_path())

    def get_value(self, name):
        value = self.__modified.get(name)
        if value is not None:
            return value
        value = self.__defaults.get(name)
        if value is not None:
            return value
        value = self.__config_from_file.get(name)
        if value is not None:
            return value
        value = self.__file_defaults.get(name)
        if value is not None:
            return value
        return None

    def set_value(self, name, value):
        if value is not None:
            self.__modified[name] = value
        else:
            del self.__modified[name]
