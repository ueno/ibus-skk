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
import os

from gettext import dgettext
_  = lambda a : dgettext("ibus-skk", a)
N_ = lambda a : a


class EngineFactory(ibus.EngineFactoryBase):
    FACTORY_PATH = "/com/redhat/IBus/engines/SKK/Factory"
    ENGINE_PATH = "/com/redhat/IBus/engines/SKK/Engine"
    NAME = _("SKK")
    LANG = "ja"
    ICON = os.getenv("IBUS_SKK_PKGDATADIR") + "/icons/ibus-skk.png"
    AUTHORS = "Daiki Ueno <ueno@unixuser.org>"
    CREDITS = "GPLv2"

    def __init__(self, bus):
        self.__bus = bus
        # engine.Engine.CONFIG_RELOADED(bus)
        super(EngineFactory, self).__init__(bus)

        self.__id = 0
        self.__config = self.__bus.get_config()

        self.__config.connect("reloaded", self.__config_reloaded_cb)
        self.__config.connect("value-changed", self.__config_value_changed_cb)

    def create_engine(self, engine_name):
        if engine_name == "skk":
            self.__id += 1
            return engine.Engine(self.__bus, "%s/%d" % (self.ENGINE_PATH, self.__id))

        return super(EngineFactory, self).create_engine(engine_name)

    def __config_reloaded_cb(self, config):
        pass
    # engine.Engine.CONFIG_RELOADED(self.__bus)

    def __config_value_changed_cb(self, config, section, name, value):
        pass
    # engine.Engine.CONFIG_VALUE_CHANGED(self.__bus, section, name, value)

