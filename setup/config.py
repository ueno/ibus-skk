import ibus
import os, os.path

class Config:
    __sysdict_paths = ('/usr/share/skk/SKK-JISYO',
                       '/usr/share/skk/SKK-JISYO.L',
                       '/usr/local/share/skk/SKK-JISYO',
                       '/usr/local/share/skk/SKK-JISYO.L')
    __usrdict_path_unexpanded = '~/.skk-ibus-jisyo'

    def __init__(self, bus=ibus.Bus()):
        self.__bus = bus
        self.__config = self.__bus.get_config()
        
    def __sysdict_path(self):
        for path in self.__sysdict_paths:
            if os.path.exists(path):
                return path
    sysdict_path = property(lambda self: self.get_value(\
            'sysdict', self.__sysdict_path()))

    def sysdict_paths(self):
        return self.get_value('sysdict_paths',
                              [self.sysdict_path] if self.sysdict_path else list())

    def __usrdict_path(self):
        usrdict_path = os.path.expanduser(self.__usrdict_path_unexpanded)
        open(usrdict_path, 'a+').close()
        return usrdict_path
    usrdict_path = property(lambda self: self.get_value(\
            'usrdict', self.__usrdict_path()))

    def get_value(self, name, defval=None):
        value = self.__config.get_value('engine/SKK', name, None)
        if value is not None:
            return value
        self.set_value(name, defval)
        return defval

    def set_value(self, name, value):
        if value is not None:
            self.__config.set_value('engine/SKK', name, value)
