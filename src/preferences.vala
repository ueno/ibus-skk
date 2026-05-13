/* 
 * Copyright (C) 2011-2018 Daiki Ueno <ueno@gnu.org>
 * Copyright (C) 2011-2018 Red Hat, Inc.
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
 * 02110-1301, USA.
 */
using Gee;

public class Preferences : Object {
    Settings settings;

    Map<string,Variant> _default = new HashMap<string,Variant> ();
    Map<string,Variant> current = new HashMap<string,Variant> ();

    public void load (bool is_default) {
        SettingsSchemaSource schema_source = SettingsSchemaSource.get_default ();
        string schema_id = settings.schema_id;
        SettingsSchema schema = schema_source.lookup (schema_id, false);
        foreach (unowned string key in schema.list_keys()) {
            if (is_default) {
                _default.set (key, settings.get_default_value (key));
            } else {
                Variant? value = settings.get_user_value (key);
                if (value != null)
                    current.set (key, value);
            }
        }
    }

    public void save () {
        var iter = current.map_iterator ();
        while (iter.next ()) {
            settings.set_value (iter.get_key (),
                                iter.get_value ());
        }
        Settings.sync ();
    }

    public new Variant? @get (string name) {
        Variant? value = current.get (name);
        if (value != null) {
            return value;
        }
        return _default.get (name);
    }

    public new void @set (string name, Variant value) {
        Variant? _value = current.get (name);
        if (_value == null || !_value.equal (value))
            current.set (name, value);
    }

    public Preferences () {
        settings = new Settings ("org.freedesktop.ibus.engine.skk");
        load (true);

        ArrayList<string> dictionaries = new ArrayList<string> ();
        dictionaries.add (
            "type=file,file=%s/ibus-skk/user.dict,mode=readwrite".printf (
                Environment.get_user_config_dir ()));
        dictionaries.add (
            "type=file,file=/usr/share/skk/SKK-JISYO.L,mode=readonly");
        dictionaries.add (
            "type=server,host=localhost,port=1178");
        _default.set ("dictionaries",
                      new Variant.strv (dictionaries.to_array ()));

        load (false);
        settings.changed.connect (value_changed_cb);
    }

    public signal void value_changed (string name, Variant value);

    void value_changed_cb (Settings settings,
                           string name)
    {
        Variant? value = settings.get_user_value (name);
        if (value == null) {
            current.unset (name);
            value = _default.get (name);
        } else {
            // save() will call this callback and should not change the current.
            Variant? _value = current.get (name);
            if (_value == null || !_value.equal (value))
                current.set (name, value);
        }
        value_changed (name, value);
    }
}
