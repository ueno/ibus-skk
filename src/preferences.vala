/* 
 * Copyright (C) 2011 Daiki Ueno <ueno@unixuser.org>
 * Copyright (C) 2011 Red Hat, Inc.
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
 * 02110-1301 USA
 */
using Gee;

public class Preferences : Object {
    IBus.Config config;

    Map<string,Variant> _default = new HashMap<string,Variant> ();
    Map<string,Variant> current = new HashMap<string,Variant> ();

    public void load () {
        Variant? values = config.get_values ("engine/skk");
        if (values != null) {
            var iter = values.iterator ();
            Variant? entry = null;
            while ((entry = iter.next_value ()) != null) {
                string name;
                Variant value;
                entry.get ("{sv}", out name, out value);
                current.set (name, value);
            }
        }
    }

    public void save () {
        var iter = current.map_iterator ();
        if (iter.first ()) {
            do {
                config.set_value ("engine/skk",
                                  iter.get_key (),
                                  iter.get_value ());
            } while (iter.next ());
        }
    }

    public new Variant? @get (string name) {
        Variant? value = current.get (name);
        if (value != null) {
            return value;
        }
        return _default.get (name);
    }

    public new void @set (string name, Variant value) {
        current.set (name, value);
    }

    static const string[] AUTO_START_HENKAN_KEYWORDS = {
        "を", "、", "。", "．", "，", "？", "」",
        "！", "；", "：", ")", ";", ":", "）",
        "”", "】", "』", "》", "〉", "｝", "］",
        "〕", "}", "]", "?", ".", ",", "!"
    };

    public Preferences (IBus.Config config) {
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
        _default.set ("auto_start_henkan_keywords",
                      new Variant.strv (AUTO_START_HENKAN_KEYWORDS));
        _default.set ("period_style",
                      new Variant.int32 ((int32) Skk.PeriodStyle.JA_JA));
        _default.set ("page_size",
                      new Variant.int32 (7));
        _default.set ("pagination_start",
                      new Variant.int32 (4));
        _default.set ("show_annotation",
                      new Variant.boolean (true));
        _default.set ("initial_input_mode",
                      new Variant.int32 (Skk.InputMode.HIRAGANA));
        _default.set ("egg_like_newline",
                      new Variant.boolean (false));
        _default.set ("typing_rule",
                      new Variant.string ("default"));

        this.config = config;
        load ();
        config.value_changed.connect (value_changed_cb);
    }

    public signal void value_changed (string name, Variant value);

    void value_changed_cb (IBus.Config config,
                           string section,
                           string name,
                           Variant value)
    {
        if (section == "engine/skk") {
            current.set (name, value);
            value_changed (name, value);
        }
    }
}
