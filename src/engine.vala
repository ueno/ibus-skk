/* 
 * Copyright (C) 2011-2012 Daiki Ueno <ueno@unixuser.org>
 * Copyright (C) 2011-2012 Red Hat, Inc.
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

class SkkEngine : IBus.Engine {
    // Preferences are shared among SkkEngine instances.
    static Preferences preferences;

    // Dictionaries are shared among SkkEngine instances and
    // maintained in the per-class signal handler in main().
    static ArrayList<Skk.Dict> dictionaries;

    Skk.Context context;
    IBus.LookupTable lookup_table;
    uint page_start;
    bool lookup_table_visible;

    bool show_annotation;

    IBus.Property input_mode_prop;
    IBus.PropList prop_list;
    bool properties_registered = false;

    Map<Skk.InputMode, IBus.Property> input_mode_props =
        new HashMap<Skk.InputMode, IBus.Property> ();
    Map<Skk.InputMode, string> input_mode_symbols =
        new HashMap<Skk.InputMode, string> ();
    Map<string, Skk.InputMode> name_input_modes =
        new HashMap<string, Skk.InputMode> ();

    construct {
        // Prepare lookup table
        lookup_table = new IBus.LookupTable (LOOKUP_TABLE_LABELS.length,
                                             0, true, false);
        for (var i = 0; i < LOOKUP_TABLE_LABELS.length; i++) {
            var text = new IBus.Text.from_string (LOOKUP_TABLE_LABELS[i]);
            lookup_table.set_label (i, text);
        }
        lookup_table.set_orientation (IBus.Orientation.HORIZONTAL);

        // Prepare the properties on the lang bar
        prop_list = new IBus.PropList ();
        var props = new IBus.PropList ();
        IBus.Property prop;

        prop = register_input_mode_property (Skk.InputMode.HIRAGANA,
                                             "InputMode.Hiragana",
                                             _("Hiragana"),
                                             "あ");
        props.append (prop);

        prop = register_input_mode_property (Skk.InputMode.KATAKANA,
                                             "InputMode.Katakana",
                                             _("Katakana"),
                                             "ア");
        props.append (prop);

        prop = register_input_mode_property (Skk.InputMode.HANKAKU_KATAKANA,
                                             "InputMode.HankakuKatakana",
                                             _("Halfwidth Katakana"),
                                             "_ｱ");
        props.append (prop);

        prop = register_input_mode_property (Skk.InputMode.LATIN,
                                             "InputMode.Latin",
                                             _("Latin"),
                                             "_A");
        props.append (prop);

        prop = register_input_mode_property (Skk.InputMode.WIDE_LATIN,
                                             "InputMode.WideLatin",
                                             _("Wide Latin"),
                                             "Ａ");
        props.append (prop);

        prop = new IBus.Property (
            "InputMode",
            IBus.PropType.MENU,
            new IBus.Text.from_string ("あ"),
            null,
            new IBus.Text.from_string (_("Switch input mode")),
            true,
            true,
            IBus.PropState.UNCHECKED,
            props);
        prop_list.append (prop);
        input_mode_prop = prop;

        prop = new IBus.Property (
            "setup",
            IBus.PropType.NORMAL,
            new IBus.Text.from_string (_("Setup")),
            "gtk-preferences",
            new IBus.Text.from_string (_("Configure SKK")),
            true,
            true,
            IBus.PropState.UNCHECKED,
            null);
        prop_list.append (prop);

        // Initialize libskk
        context = new Skk.Context (dictionaries.to_array ());

        apply_preferences ();
        preferences.value_changed.connect ((name, value) => {
                apply_preferences ();
                if (name == "dictionaries") {
                    // SkkEngine.dictionaries should be updated separately
                    context.dictionaries = SkkEngine.dictionaries.to_array ();
                }
            });

        context.notify["preedit"].connect (() => {
                update_preedit ();
            });
        context.notify["input-mode"].connect ((s, p) => {
                update_input_mode ();
            });
        context.candidates.populated.connect (() => {
                populate_lookup_table ();
            });
        context.candidates.notify["cursor-pos"].connect (() => {
                set_lookup_table_cursor_pos ();
            });
        context.candidates.selected.connect (() => {
                var output = context.poll_output ();
                if (output.length > 0) {
                    var text = new IBus.Text.from_string (output);
                    commit_text (text);
                }
                if (lookup_table_visible) {
                    hide_lookup_table ();
                    hide_auxiliary_text ();
                    lookup_table_visible = false;
                }
            });

        update_candidates ();
        update_input_mode ();
        context.retrieve_surrounding_text.connect (_retrieve_surrounding_text);
        context.delete_surrounding_text.connect (_delete_surrounding_text);
    }

    bool _retrieve_surrounding_text (out string text, out uint cursor_pos) {
        weak IBus.Text _text;
        uint _cursor_pos, anchor_pos;
        get_surrounding_text (out _text, out _cursor_pos, out anchor_pos);
        text = _text.text.dup ();
        cursor_pos = _cursor_pos;
        return true;
    }

    bool _delete_surrounding_text (int offset, uint nchars) {
        delete_surrounding_text (offset, nchars);
        return true;
    }

    void populate_lookup_table () {
        lookup_table.clear ();
        for (int i = (int) page_start;
             i < context.candidates.size;
             i++) {
            var text = new IBus.Text.from_string (
                context.candidates[i].output);
            lookup_table.append_candidate (text);
        }
    }

    void set_lookup_table_cursor_pos () {
        var empty_text = new IBus.Text.from_static_string ("");
        var cursor_pos = context.candidates.cursor_pos;
        if (context.candidates.page_visible) {
            lookup_table.set_cursor_pos (cursor_pos -
                                         context.candidates.page_start);
            update_lookup_table_fast (lookup_table, true);
            var candidate = context.candidates.get ();
            if (show_annotation && candidate.annotation != null) {
                var text = new IBus.Text.from_string (
                    candidate.annotation);
                update_auxiliary_text (text, true);
            } else {
                update_auxiliary_text (empty_text, false);
            }
            lookup_table_visible = true;
        } else if (lookup_table_visible) {
            hide_lookup_table ();
            hide_auxiliary_text ();
            lookup_table_visible = false;
        }
    }

    void update_preedit () {
        var text = new IBus.Text.from_string (context.preedit);
        uint underline_offset, underline_nchars;
        context.get_preedit_underline (out underline_offset,
                                       out underline_nchars);
        if (0 < underline_nchars) {
            text.append_attribute (IBus.AttrType.UNDERLINE,
                                   IBus.AttrUnderline.SINGLE,
                                   (int) underline_offset,
                                   (int) (underline_offset + underline_nchars));
        }
        update_preedit_text (text,
                             text.get_length (),
                             text.get_length () > 0);
    }

    void update_candidates () {
        context.candidates.page_start = page_start;
        context.candidates.page_size = lookup_table.get_page_size ();
        populate_lookup_table ();
        set_lookup_table_cursor_pos ();
    }

    void update_input_mode () {
        // Update the menu item
        var iter = input_mode_props.map_iterator ();
        if (iter.first ()) {
            do {
                var input_mode = iter.get_key ();
                var prop = iter.get_value ();
                if (input_mode == context.input_mode)
                    prop.set_state (IBus.PropState.CHECKED);
                else
                    prop.set_state (IBus.PropState.UNCHECKED);
                if (properties_registered)
                    update_property (prop);
            } while (iter.next ());
        }

        // Update the menu
        var symbol = new IBus.Text.from_string (
            input_mode_symbols.get (context.input_mode));
#if IBUS_1_5
        var label = new IBus.Text.from_string (
            _("Input Mode (%s)").printf (symbol.text));
        input_mode_prop.set_label (label);
        input_mode_prop.set_symbol (symbol);
#else
        input_mode_prop.set_label (symbol);
#endif
        if (properties_registered)
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
            if (mode == "readonly") {
                if (file.has_suffix (".cdb"))
                    return new Skk.CdbDict (file, encoding);
                else
                    return new Skk.FileDict (file, encoding);
            } else if (mode == "readwrite")
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
                warning ("can't parse plist \"%s\": %s",
                         str, e.message);
            } catch (GLib.Error e) {
                warning ("can't open dictionary \"%s\": %s",
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
        page_start = (uint) variant.get_int32 ();

        variant = preferences.get ("initial_input_mode");
        assert (variant != null);
        context.input_mode = (Skk.InputMode) variant.get_int32 ();

        variant = preferences.get ("show_annotation");
        assert (variant != null);
        show_annotation = variant.get_boolean ();
        
        variant = preferences.get ("egg_like_newline");
        assert (variant != null);
        context.egg_like_newline = variant.get_boolean ();

        variant = preferences.get ("typing_rule");
        assert (variant != null);
        try {
            context.typing_rule = new Skk.Rule (variant.get_string ());
        } catch (Skk.RuleParseError e) {
            warning ("can't load typing rule %s: %s",
                     variant.get_string (), e.message);
        }
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
                                    "q", "w", "e", "r", "u", "i", "o"};

    bool process_lookup_table_key_event (uint keyval,
                                         uint keycode,
                                         uint state)
    {
        var page_size = lookup_table.get_page_size ();
        if (state == 0 &&
            ((unichar) keyval).to_string () in LOOKUP_TABLE_LABELS) {
            string label = ((unichar) keyval).tolower ().to_string ();
            for (var index = 0;
                 index < int.min ((int)page_size, LOOKUP_TABLE_LABELS.length);
                 index++) {
                if (LOOKUP_TABLE_LABELS[index] == label) {
                    return context.candidates.select_at (index);
                }
            }
            return false;
        }

        if (state == 0) {
            bool retval = false;
            switch (keyval) {
            case IBus.Page_Up:
            case IBus.KP_Page_Up:
                retval = context.candidates.page_up ();
                break;
            case IBus.Page_Down:
            case IBus.KP_Page_Down:
                retval = context.candidates.page_down ();
                break;
            case IBus.Up:
            case IBus.Left:
                retval = context.candidates.cursor_up ();
                break;
            case IBus.Down:
            case IBus.Right:
                retval = context.candidates.cursor_down ();
                break;
            default:
                break;
            }

            if (retval) {
                set_lookup_table_cursor_pos ();
                update_preedit ();
                return true;
            }
        }

        return false;
    }

    public override bool process_key_event (uint keyval,
                                            uint keycode,
                                            uint state)
    {
        // Filter out unnecessary modifier bits
        // FIXME: should resolve virtual modifiers
        uint _state = state & (IBus.ModifierType.CONTROL_MASK |
                               IBus.ModifierType.MOD1_MASK |
                               IBus.ModifierType.MOD5_MASK |
                               IBus.ModifierType.RELEASE_MASK);
        if (context.candidates.page_visible &&
            process_lookup_table_key_event (keyval, keycode, _state)) {
            return true;
        }

        Skk.ModifierType modifiers = (Skk.ModifierType) _state;
        Skk.KeyEvent key;
        try {
            key = new Skk.KeyEvent.from_x_keysym (keyval, modifiers);
        } catch (Skk.KeyEventFormatError e) {
            return false;
        }

        var retval = context.process_key_event (key);
        var output = context.poll_output ();
        if (output.length > 0) {
            var text = new IBus.Text.from_string (output);
            commit_text (text);
        }
        return retval;
    }

    public override void enable () {
        context.reset ();

        // Request to use surrounding text feature
        get_surrounding_text (null, null, null);
        base.enable ();
    }

    public override void disable () {
        focus_out ();
        base.disable ();
    }

    public override void reset () {
        context.reset ();
        var empty_text = new IBus.Text.from_static_string ("");
        update_preedit_text (empty_text,
                             0,
                             false);
        base.reset ();
    }

    public override void focus_in () {
        update_input_mode ();
        register_properties (prop_list);
        properties_registered = true;
        base.focus_in ();
    }

    public override void focus_out () {
        context.reset ();
        hide_preedit_text ();
        hide_lookup_table ();
        properties_registered = false;
        base.focus_out ();
    }

    public override void property_activate (string prop_name,
                                            uint prop_state)
    {
        if (prop_name == "setup") {
            var filename = Path.build_filename (Config.LIBEXECDIR,
                                                "ibus-setup-skk");
            try {
                Process.spawn_command_line_async (filename);
            } catch (GLib.SpawnError e) {
                warning ("can't spawn %s: %s", filename, e.message);
            }
        }
        else if (prop_name.has_prefix ("InputMode.") &&
                 prop_state == IBus.PropState.CHECKED) {
            context.input_mode = name_input_modes.get (prop_name);
        }
    }

    public override void candidate_clicked (uint index, uint button, uint state) {
        context.candidates.select_at (index);
    }

    public override void cursor_up () {
        context.candidates.cursor_up ();
    }

    public override void cursor_down () {
        context.candidates.cursor_down ();
    }

    public override void page_up () {
        context.candidates.page_up ();
    }

    public override void page_down () {
        context.candidates.page_down ();
    }

    static bool ibus;

    const OptionEntry[] options = {
        {"ibus", 'i', 0, OptionArg.NONE, ref ibus,
         N_("Component is executed by IBus"), null },
        { null }
    };

    public static int main (string[] args) {
        IBus.init ();
        Skk.init ();

        Intl.setlocale (LocaleCategory.ALL, "");
        Intl.bindtextdomain (Config.GETTEXT_PACKAGE, Config.LOCALEDIR);
        Intl.bind_textdomain_codeset (Config.GETTEXT_PACKAGE, "UTF-8");

        var context = new OptionContext ("- ibus skk");
        context.add_main_entries (options, "ibus-skk");
        try {
            context.parse (ref args);
        } catch (OptionError e) {
            stderr.printf ("%s\n", e.message);
            return 1;
        }

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
