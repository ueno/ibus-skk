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

class SkkEngine : IBus.Engine {
    // preferences are shared among SkkEngine instances.
    static Preferences preferences;

    // dictionaries are shared among SkkEngine instances and
    // maintained in the per-class signal handler in main().
    static ArrayList<Skk.Dict> dictionaries;

    Skk.Context context;
    IBus.LookupTable lookup_table;
    int pagination_start;

    bool show_annotation;

    IBus.Property input_mode_prop;
    IBus.PropList prop_list;

    Map<Skk.InputMode, IBus.Property> input_mode_props =
        new HashMap<Skk.InputMode, IBus.Property> ();
    Map<Skk.InputMode, string> input_mode_symbols =
        new HashMap<Skk.InputMode, string> ();
    Map<string, Skk.InputMode> name_input_modes =
        new HashMap<string, Skk.InputMode> ();

    construct {
        // prepare lookup table
        lookup_table = new IBus.LookupTable (LOOKUP_TABLE_LABELS.length,
                                             0, true, false);
        for (var i = 0; i < LOOKUP_TABLE_LABELS.length; i++) {
            var text = new IBus.Text.from_string (LOOKUP_TABLE_LABELS[i]);
            lookup_table.set_label (i, text);
        }

        // prepare the properties on the lang bar
        prop_list = new IBus.PropList ();
        var props = new IBus.PropList ();
        IBus.Property prop;

        prop = register_input_mode_property (Skk.InputMode.HIRAGANA,
                                         "InputMode.Hiragana",
                                         "Hiragana",
                                         "あ");
        props.append (prop);

        prop = register_input_mode_property (Skk.InputMode.KATAKANA,
                                         "InputMode.Katakana",
                                         "Katakana",
                                         "ア");
        props.append (prop);

        prop = register_input_mode_property (Skk.InputMode.HANKAKU_KATAKANA,
                                         "InputMode.HankakuKatakana",
                                         "HankakuKatakana",
                                         "ｱ");
        props.append (prop);

        prop = register_input_mode_property (Skk.InputMode.LATIN,
                                         "InputMode.Latin",
                                         "Latin",
                                         "A");
        props.append (prop);

        prop = register_input_mode_property (Skk.InputMode.WIDE_LATIN,
                                         "InputMode.WideLatin",
                                         "WideLatin",
                                         "Ａ");
        props.append (prop);

        prop = new IBus.Property (
            "InputMode",
            IBus.PropType.MENU,
            new IBus.Text.from_string ("あ"),
            null,
            new IBus.Text.from_string ("Switch input mode"),
            true,
            true,
            IBus.PropState.UNCHECKED,
            props);
        prop_list.append (prop);
        input_mode_prop = prop;

        prop = new IBus.Property (
            "setup",
            IBus.PropType.NORMAL,
            new IBus.Text.from_string ("Setup"),
            "gtk-preferences",
            new IBus.Text.from_string ("Configure SKK"),
            true,
            true,
            IBus.PropState.UNCHECKED,
            null);
        prop_list.append (prop);

        // initialize libskk
        context = new Skk.Context (dictionaries.to_array ());

        apply_preferences ();
        preferences.value_changed.connect ((name, value) => {
                apply_preferences ();
                if (name == "dictionaries") {
                    // SkkEngine.dictionaries should be updated separately
                    context.dictionaries = SkkEngine.dictionaries.to_array ();
                }
            });

        var empty_text = new IBus.Text.from_static_string ("");
        context.notify["preedit"].connect (() => {
                var text = new IBus.Text.from_string (context.preedit);
                update_preedit_text (text,
                                     text.get_length (),
                                     text.get_length () > 0);
            });
        context.candidates.notify["cursor-pos"].connect (() => {
                if (context.candidates.cursor_pos >= pagination_start) {
                    lookup_table.set_cursor_pos (
                        context.candidates.cursor_pos - pagination_start);
                    update_lookup_table (lookup_table, true);
                    var candidate = context.candidates.get ();
                    if (show_annotation && candidate.annotation != null) {
                        var text = new IBus.Text.from_string (
                            candidate.annotation);
                        update_auxiliary_text (text, true);
                    } else {
                        update_auxiliary_text (empty_text, false);
                    }
                } else {
                    update_lookup_table (lookup_table, false);
                    update_auxiliary_text (empty_text, false);
                }
            });
        context.candidates.populated.connect (() => {
                lookup_table.clear ();
                for (var i = pagination_start;
                     i < context.candidates.size;
                     i++) {
                    var text = new IBus.Text.from_string (
                        context.candidates[i].output);
                    lookup_table.append_candidate (text);
                }
            });
        context.notify["input-mode"].connect ((s, p) => {
                update_input_mode ();
            });
        update_input_mode ();
    }

    void update_input_mode () {
        // update the state of menu item
        var _prop = input_mode_props.get (context.input_mode);
        _prop.set_state (IBus.PropState.CHECKED);
        update_property (_prop);
        
        // update the label of the menu
        var symbol = new IBus.Text.from_string (
            input_mode_symbols.get (context.input_mode));
        input_mode_prop.set_label (symbol);
        update_property (input_mode_prop);
    }

    static Skk.Dict? parse_dict_from_plist (PList plist) throws GLib.Error {
        var encoding = plist.get ("encoding") ?? "EUC-JP";
        var type = plist.get ("type");
        if (type == "file") {
            string? file = plist.get ("file");
            if (file == null) {
                return null;
            }
            string mode = plist.get ("mode") ?? "readonly";
            if (mode == "readonly")
                return new Skk.FileDict (file, encoding);
            else if (mode == "readwrite")
                return new Skk.UserDict (file, encoding);
        } else if (type == "server") {
            var host = plist.get ("host") ?? "localhost";
            var port = plist.get ("port") ?? "1178";
            return new Skk.SkkServ (host, (uint16) int.parse (port), encoding);
        }
        return null;
    }

    static void reload_dictionaries () {
        SkkEngine.dictionaries.clear ();
        Variant? variant = preferences.get ("dictionaries");
        assert (variant != null);
        string[] strv = variant.dup_strv ();
        foreach (var str in strv) {
            try {
                var plist = new PList (str);
                Skk.Dict? dict = parse_dict_from_plist (plist);
                if (dict != null)
                    dictionaries.add (dict);
            } catch (PListParseError e) {
                stderr.printf ("can't parse plist \"%s\": %s\n",
                               str, e.message);
            } catch (GLib.Error e) {
                stderr.printf ("can't open dictionary \"%s\": %s\n",
                               str, e.message);
            }
        }
    }

    void apply_preferences () {
        Variant? variant;

        variant = preferences.get ("auto_start_henkan_keywords");
        assert (variant != null);
        context.auto_start_henkan_keywords = variant.get_strv ();

        variant = preferences.get ("period_style");
        assert (variant != null);
        context.period_style = (Skk.PeriodStyle) variant.get_int32 ();

        variant = preferences.get ("page_size");
        assert (variant != null);
        lookup_table.set_page_size (variant.get_int32 ());

        variant = preferences.get ("pagination_start");
        assert (variant != null);
        pagination_start = variant.get_int32 ();

        variant = preferences.get ("initial_input_mode");
        assert (variant != null);
        context.input_mode = (Skk.InputMode) variant.get_int32 ();

        variant = preferences.get ("show_annotation");
        assert (variant != null);
        show_annotation = variant.get_boolean ();
        
        variant = preferences.get ("egg_like_newline");
        assert (variant != null);
        context.egg_like_newline = variant.get_boolean ();
    }

    IBus.Property register_input_mode_property (Skk.InputMode mode,
                                                string name,
                                                string label,
                                                string symbol)
    {
        var prop = new IBus.Property (name,
                                      IBus.PropType.RADIO,
                                      new IBus.Text.from_string (label),
                                      null,
                                      null,
                                      true,
                                      true,
                                      IBus.PropState.UNCHECKED,
                                      null);
        input_mode_props.set (mode, prop);
        input_mode_symbols.set (mode, symbol);
        name_input_modes.set (name, mode);
        return prop;
    }

    string[] LOOKUP_TABLE_LABELS = {"a", "s", "d", "f", "j", "k", "l",
                                    "q", "w", "e", "r", "u", "i", "o",
                                    "z", "x"};

    uint get_page_start_cursor_pos () {
        var page_size = lookup_table.get_page_size ();
        return (lookup_table.get_cursor_pos () / page_size) * page_size;
    }

    bool process_lookup_table_key_event (uint keyval,
                                         uint keycode,
                                         uint state)
    {
        if (state == 0 && (keyval == IBus.Page_Up ||
                           keyval == IBus.KP_Page_Up)) {
            var cursor_pos = get_page_start_cursor_pos () - lookup_table.get_page_size ();
            if (lookup_table.page_up ()) {
                context.candidates.cursor_pos = (int) cursor_pos + pagination_start;
                update_lookup_table (lookup_table, true);
            }
            return true;
        }
        else if (state == 0 && (keyval == IBus.Page_Down ||
                                keyval == IBus.KP_Page_Down)) {
            var cursor_pos = get_page_start_cursor_pos () + lookup_table.get_page_size ();
            if (lookup_table.page_down ()) {
                context.candidates.cursor_pos = (int) cursor_pos + pagination_start;
                update_lookup_table (lookup_table, true);
            }
            return true;
        }
        else if (state == 0 && (keyval == IBus.Up ||
                                keyval == IBus.Left)) {
            if (lookup_table.cursor_up ()) {
                update_lookup_table (lookup_table, true);
                if (context.candidates.cursor_pos > 0)
                    context.candidates.cursor_pos--;
            }
            return true;
        }
        else if (state == 0 && (keyval == IBus.Down ||
                                keyval == IBus.Right)) {
            if (lookup_table.cursor_down ()) {
                update_lookup_table (lookup_table, true);
                if (context.candidates.cursor_pos < context.candidates.size - 1)
                    context.candidates.cursor_pos++;
            }
            return true;
        }
        else if (state == 0) {
            var page_size = lookup_table.get_page_size ();
            string label = ((unichar)keyval).tolower ().to_string ();
            for (var index = 0;
                 index < int.min ((int)page_size, LOOKUP_TABLE_LABELS.length);
                 index++) {
                if (LOOKUP_TABLE_LABELS[index] == label) {
                    var cursor_pos = get_page_start_cursor_pos () + index;
                    lookup_table.set_cursor_pos (cursor_pos);
                    update_lookup_table (lookup_table, true);
                    context.candidates.cursor_pos = (int) cursor_pos + pagination_start;
                    context.candidates.select ();
                    var output = context.get_output ();
                    if (output.length > 0) {
                        var text = new IBus.Text.from_string (output);
                        commit_text (text);
                    }
                    return true;
                }
            }
        }
        return false;
    }

    public override bool process_key_event (uint keyval, uint keycode, uint state) {
        // ignore release event
        if ((IBus.ModifierType.RELEASE_MASK & state) != 0)
            return false;

        if (context.candidates.cursor_pos >= pagination_start &&
            process_lookup_table_key_event (keyval, keycode, state)) {
            return true;
        }

        var builder = new StringBuilder ();
        if ((IBus.ModifierType.CONTROL_MASK & state) != 0)
            builder.append ("C-");
        if ((IBus.ModifierType.MOD1_MASK & state) != 0)
            builder.append ("A-");
        if ((IBus.ModifierType.META_MASK & state) != 0)
            builder.append ("M-");
        if ((IBus.ModifierType.MOD5_MASK & state) != 0)
            builder.append ("G-");

        unichar keychr = (unichar) keyval;
        if (keyval == IBus.Tab) {
            keychr = '\t';
        }
        else if (keyval == IBus.Return) {
            keychr = '\n';
        }
        else if (keyval == IBus.BackSpace) {
            keychr = '\x7F';
        }

        if (0 <= keychr && keychr <= 0x7F) {
            builder.append_unichar (keychr);
            bool retval = context.process_key_event (builder.str);
            var output = context.get_output ();
            if (output.length > 0) {
                var text = new IBus.Text.from_string (output);
                commit_text (text);
            }
            return retval;
        }
        return false;
    }

    public override void enable () {
        context.reset ();
    }

    public override void disable () {
    }

    public override void reset () {
        context.reset ();
    }

    public override void focus_in () {
        register_properties (prop_list);
        context.reset ();
    }

    public override void focus_out () {
    }

    public override void property_activate (string prop_name,
                                            uint prop_state)
    {
        if (prop_name == "setup") {
            try {
                Process.spawn_command_line_async (
                    Path.build_filename (Config.LIBEXECDIR,
                                         "ibus-setup-skk"));
            } catch (GLib.SpawnError e) {
                stderr.printf ("can't spawn ibus-setup-skk: %s\n", e.message);
            }
        }
        else if (prop_name.has_prefix ("InputMode.") &&
                 prop_state == IBus.PropState.CHECKED) {
            context.input_mode = name_input_modes.get (prop_name);
        }
    }

    static bool ibus;

    const OptionEntry[] options = {
        {"ibus", 'i', 0, OptionArg.NONE, ref ibus,
         N_("Component is executed by IBus"), null },
        { null }
    };

    public static int main (string[] args) {
        Intl.bindtextdomain (Config.GETTEXT_PACKAGE, "");
        Intl.bind_textdomain_codeset (Config.GETTEXT_PACKAGE, "UTF-8");
        Intl.textdomain (Config.GETTEXT_PACKAGE);

        var context = new OptionContext ("- ibus skk");
        context.add_main_entries (options, "ibus-skk");
        try {
            context.parse (ref args);
        } catch (OptionError e) {
            stderr.printf ("%s\n", e.message);
            return 1;
        }

        IBus.init ();
        var bus = new IBus.Bus ();

        if (!bus.is_connected ()) {
            stderr.printf ("Can not connect to ibus-daemon!\n");
            return 1;
        }

        bus.disconnected.connect (() => { IBus.quit (); });

        var config = bus.get_config ();
        SkkEngine.preferences = new Preferences (config);
        SkkEngine.dictionaries = new ArrayList<Skk.Dict> ();
        SkkEngine.reload_dictionaries ();
        SkkEngine.preferences.value_changed.connect ((name, value) => {
                if (name == "dictionaries") {
                    SkkEngine.reload_dictionaries ();
                }
            });

        var factory = new IBus.Factory (bus.get_connection());
        factory.add_engine ("skk", typeof(SkkEngine));
        if (ibus) {
            bus.request_name ("org.freedesktop.IBus.SKK", 0);
        } else {
            var component = new IBus.Component (
                "org.freedesktop.IBus.SKK",
                N_("SKK"), Config.PACKAGE_VERSION, "GPL",
                "Daiki Ueno <ueno@unixuser.org>",
                "http://code.google.com/p/ibus/",
                "",
                "ibus-skk");
            var engine = new IBus.EngineDesc (
                "skk",
                "SKK",
                "SKK Input Method",
                "ja",
                "GPL",
                "Daiki Ueno <ueno@unixuser.org>",
                "%s/icons/ibus-skk.svg".printf (Config.PACKAGE_DATADIR),
                "us");
            component.add_engine (engine);
            bus.register_component (component);
        }
        IBus.main ();
        return 0;
    }
}