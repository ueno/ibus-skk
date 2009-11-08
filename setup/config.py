import ibus
import os, os.path

class Config:
    __sysdict_paths = ('/usr/share/skk/SKK-JISYO',
                       '/usr/share/skk/SKK-JISYO.L',
                       '/usr/local/share/skk/SKK-JISYO',
                       '/usr/local/share/skk/SKK-JISYO.L')
    __usrdict_path = '~/.skk-ibus-jisyo'

    def __init__(self, bus=ibus.Bus()):
        self.__bus = bus
        self.__config = self.__bus.get_config()
        
    def __sysdict_path(self):
        for path in __sysdict_paths:
            if os.path.exists(path):
                return path
    sysdict_path = property(lambda self: self.get_value('sysdict') or \
                                self.__sysdict_path())

    def __usrdict_path(self):
        os.path.expanduser(__usrdict_path)
        open(usrdict_path, 'a+').close()
    usrdict_path = property(lambda self: self.get_value('usrdict') or \
                                self.__usrdict_path())

    def get_value(self, name, defval=None):
        value = self.__config.get_value('engine/SKK', name, None)
        if value is not None:
            return value
        self.__set_value(name, defval)
        return defval

    def set_value(self, name, val):
        self.__config.set_value('engine/SKK', name, val)
