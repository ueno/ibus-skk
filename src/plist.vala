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

public errordomain PListParseError {
    FAILED
}

public class PList : Object {
    Map<string,string> map = new HashMap<string,string> ();

    public new string? @get (string key) {
        return map.get (key);
    }

    public PList (string str) throws PListParseError {
        StringBuilder builder = new StringBuilder ();
        string? key = null, value = null;
        int index;
        for (index = 0; index < str.length; index++) {
            switch (str[index]) {
            case '\\':
                index++;
                if (index == str.length) {
                    throw new PListParseError.FAILED ("");
                }
                builder.append_c (str[index]);
                break;
            case ',':
                if (key == null) {
                    throw new PListParseError.FAILED ("");
                }
                value = builder.str;
                builder.erase ();
                map.set (key, value);
                key = null;
                break;
            case '=':
                key = builder.str;
                builder.erase ();
                value = null;
                break;
            default:
                builder.append_c (str[index]);
                break;
            }
        }
        if (index == str.length) {
            if (key == null) {
                throw new PListParseError.FAILED ("");
            }
            value = builder.str;
            map.set (key, value);
        }
    }

    public static string escape (string str) {
        var builder = new StringBuilder ();
        int index = 0;
        unichar uc;
        while (str.get_next_char (ref index, out uc)) {
            if (uc == ',' || uc == '\\' || uc == '=') {
                builder.append ("\\");
            }
            builder.append_unichar (uc);
        }
        return builder.str;
    }

    public string to_string () {
        var props = new ArrayList<string?> ();
        var keys = new TreeSet<string> ();
        keys.add_all (map.keys);
        foreach (var key in keys) {
            var value = map.get (key);
            props.add ("%s=%s".printf (PList.escape (key),
                                       PList.escape (value)));
        }
        props.add (null);
        return string.joinv (",", props.to_array ());
    }
}
