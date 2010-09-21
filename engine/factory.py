# vim:set et sts=4 sw=4:
# -*- coding: utf-8 -*-
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
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

import ibus
import engine
import sys, os, os.path
import skk

from gettext import dgettext
_  = lambda a : dgettext("ibus-skk", a)
N_ = lambda a : a

sys.path.insert(0, os.path.join(os.getenv('IBUS_SKK_PKGDATADIR'), 'setup'))
import config

class EngineFactory(ibus.EngineFactoryBase):
    FACTORY_PATH = "/com/redhat/IBus/engines/SKK/Factory"
    ENGINE_PATH = "/com/redhat/IBus/engines/SKK/Engine"
    NAME = _("SKK")
    LANG = "ja"
    ICON = os.getenv("IBUS_SKK_PKGDATADIR") + "/icons/ibus-skk.svg"
    AUTHORS = "Daiki Ueno <ueno@unixuser.org>"
    CREDITS = "GPLv2"

    def __init__(self, bus):
        self.__bus = bus
        super(EngineFactory, self).__init__(bus)

        self.__id = 0
        bus_config = self.__bus.get_config()
        bus_config.connect("reloaded", self.__config_reloaded_cb)
        bus_config.connect("value-changed", self.__config_value_changed_cb)
        self.__config_reloaded_cb(bus_config)

    def create_engine(self, engine_name):
        if engine_name == "skk":
            self.__id += 1
            return engine.Engine(self.__bus, "%s/%d" % (self.ENGINE_PATH, self.__id))

        return super(EngineFactory, self).create_engine(engine_name)

    def __load_sysdict(self, _config):
        sysdict_type = _config.get_value('sysdict_type', 'file')
        try:
            if sysdict_type == 'file':
                use_mmap = _config.get_value('use_mmap', True)
                instances = list()
                for path in _config.sysdict_paths():
                    instances.append(skk.SysDict(path, use_mmap=use_mmap))
                return skk.MultiSysDict(instances)
            else:
                host = _config.get_value('skkserv_host', 'localhost')
                port = int(_config.get_value('skkserv_port', '1178'))
                args = [host, port]
                encoding = _config.get_value('skkserv_encoding')
                if encoding:
                    args.append(encoding)
                return skk.SkkServ(*args)
        except:
            return skk.EmptyDict()

    def __config_reloaded_cb(self, bus_config):
        engine.Engine.config = config.Config(self.__bus)
        engine.Engine.sysdict = self.__load_sysdict(engine.Engine.config)

    def __config_value_changed_cb(self, bus_config, section, name, value):
        if section == 'engine/SKK':
            engine.Engine.config.set_value(name, value)
            if name in ('sysdict_type', 'sysdict_paths', 'use_mmap',
                        'skkserv_host', 'skkserv_port',
                        'skkserv_encoding'):
                engine.Engine.sysdict = self.__load_sysdict(engine.Engine.config)
