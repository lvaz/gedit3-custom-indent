# -*- coding: utf-8 -*-
#
#    Gedit Custom Indentation
#    Copyright (C) 2012  Leandro Vaz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
try:
    import pickle as pickle
except:
    import pickle
import sys

from gi.repository import Gedit, GObject, Gtk, GtkSource, PeasGtk


class Settings(object):
    """Manages language settings."""

    SETTINGS_FILENAME = "settings.pkl"
    DEFAULT_TAB_WIDTH = 4
    DEFAULT_USE_SPACES = True

    _settings = {}
    _lang_map = {}

    @staticmethod
    def load():
        """Loads language settings."""
        settings_path = Settings.get_path()
        lm = GtkSource.LanguageManager()
        if not os.path.exists(settings_path):
            lang_ids = lm.get_language_ids()
            for lang_id in lang_ids:
                Settings._settings[lang_id] = (Settings.DEFAULT_TAB_WIDTH, 
                        Settings.DEFAULT_USE_SPACES)
        else:
            try:
                f = open(settings_path, "rb")
            except IOError:
                print("Failed to load settings.")
                sys.exit(1)
            Settings._settings = pickle.load(f)
            f.close()
        # Associate language names to language ids.
        for lang_id in lm.get_language_ids():
            lang = lm.get_language(lang_id)
            Settings._lang_map[lang.get_name()] = lang_id

    @staticmethod
    def save():
        """Saves language settings."""
        settings_path = Settings.get_path()
        try:
            f = open(settings_path, "wb")
        except IOError:
            print("Failed to open the settings file.")
            sys.exit(1)
        pickle.dump(Settings._settings, f)
        f.close()

    @staticmethod
    def get_path():
        """Returns the settings file path."""
        path = os.path.expanduser("~/.local/share/gedit/plugins/customindent/")
        return path + Settings.SETTINGS_FILENAME

    @staticmethod
    def get_lang_names():
        """Returns a list of language names."""
        return list(Settings._lang_map.keys())

    @staticmethod
    def get_lang_id_from_name(lang_name):
        """Returns a language id from it's name."""
        if lang_name in Settings._lang_map:
            return Settings._lang_map[lang_name]
        return None

    @staticmethod
    def get_lang_settings(lang_id):
        """Returns language settings for the specified language."""
        return Settings._settings[lang_id]

    @staticmethod
    def set_lang_settings(lang_id, tab_width, use_spaces):
        """Sets language settings for the specified language."""
        Settings._settings[lang_id] = (tab_width, use_spaces)

    @staticmethod
    def get_lang_settings_from_name(lang_name):
        """Returns language settings for the specified language."""
        lang_id = Settings._lang_map[lang_name]
        return Settings._settings[lang_id]

    @staticmethod
    def set_lang_settings_from_name(lang_name, tab_width, use_spaces):
        """Sets language settings for the specified language."""
        lang_id = Settings._lang_map[lang_name]
        Settings.set_lang_settings(lang_id, tab_width, use_spaces)


class ConfigWidget(object):
    """Builds configuration UI objects. It does not represent the whole dialog
    but a GTK UI element that will be plugged into a dialog created by gedit.
    """

    def __init__(self):
        """Constructs the configuration widget."""
        self._root = None
        self._combobox = None
        self._spinbtn = None
        self._checkbtn = None
        self._build()

    def get_root(self):
        """Returns the root element of the widget."""
        return self._root

    def _build(self):
        """Configures child widget for plugin configuration.

        On previous version of gedit it was required to build the full dialog,
        but now we just need to create a child widget, gedit will handle the
        creation of the dialog.
        """
        # Create languages combo box.
        store = Gtk.ListStore(GObject.TYPE_STRING)
        for lang_name in sorted(Settings.get_lang_names()):
            store.append([lang_name])
        self._combobox = Gtk.ComboBoxText()
        self._combobox.set_model(store)
        self._combobox.set_active(0)
        # Create tab width spinner.
        self._spinbtn = Gtk.SpinButton()
        self._spinbtn.set_adjustment(Gtk.Adjustment(4, 1, 16, 1))
        # Create spaces check box.
        self._checkbtn = Gtk.CheckButton()
        # Set event handlers.
        self._combobox.connect("changed", self._on_combobox_changed)
        self._spinbtn.connect("value-changed", self._on_spinbtn_value_changed)
        self._checkbtn.connect("toggled", self._on_checkbtn_toggled)
        # Pack.
        self._root = Gtk.Table(3, 2)
        self._root.attach(Gtk.Label("Language"), 0, 1, 0, 1, xpadding = 12)
        self._root.attach(self._combobox, 1, 2, 0, 1, ypadding = 6)
        self._root.attach(Gtk.Label("Tab width"), 0, 1, 1, 2, xpadding = 12)
        self._root.attach(self._spinbtn, 1, 2, 1, 2, ypadding = 6)
        self._root.attach(Gtk.Label("Use spaces"), 0, 1, 2, 3, xpadding = 12)
        self._root.attach(self._checkbtn, 1, 2, 2, 3, ypadding = 6)
        self._load(self._combobox.get_active_text())

    def _on_combobox_changed(self, combobox):
        """Called when language combo changes it's value. Loads the selected 
        language configuration.
        """
        lang_id = combobox.get_active_text()
        self._load(lang_id)
 
    def _on_spinbtn_value_changed(self, spinbtn):
        """Called when the tabs width is changed. Saves language settings."""
        self._save()

    def _on_checkbtn_toggled(self, checkbtn):
        """Called when the tabs or spaces checkbox is changed. Saves language 
        settings.
        """
        self._save()

    def _save(self):
        """Save language settings from the configuration dialog."""
        lang_name = self._combobox.get_active_text()
        tab_width = self._spinbtn.get_value_as_int()
        use_spaces = self._checkbtn.get_active()
        Settings.set_lang_settings_from_name(lang_name, tab_width, use_spaces)
        lang_id = Settings.get_lang_id_from_name(lang_name)
        Context.apply_settings([lang_id])

    def _load(self, lang_name):
        """Load language settings to configuration dialog."""
        tab_width, use_spaces = Settings.get_lang_settings_from_name(lang_name)
        self._spinbtn.get_adjustment().set_value(tab_width)
        self._checkbtn.set_active(use_spaces)


class Context(object):
    """Global context."""

    _window = None

    @staticmethod
    def init(window):
        """Constructs the global context."""
        Context._window = window

    @staticmethod
    def get_window():
        """Returns the gedit window instance."""
        return Context._window

    @staticmethod
    def get_statusbar():
        """Returns the window status bar."""
        return Context.get_window().get_children()[0].get_children()[3]

    @staticmethod
    def get_statusbar_language_combobox():
        """Returns the status bar combobox that changes the document
        language.
        """
        return Context.get_statusbar().get_children()[3]

    @staticmethod
    def get_statusbar_tabwidth_combobox():
        """Returns the status bar combobox that changes the document tab 
        width.
        """
        return Context.get_statusbar().get_children()[4]

    @staticmethod
    def apply_settings(lang_ids = []):
        """Applies current language settings from a specified language list to
        documents."""
        for doc in Context.get_window().get_documents():
            lang = doc.get_language()
            if lang != None and (lang.get_id() in lang_ids):
                view = Gedit.Tab.get_from_document(doc).get_view()
                lang_id = lang.get_id()
                tab_width, use_spaces = Settings.get_lang_settings(lang_id)
                view.set_tab_width(tab_width)
                view.set_insert_spaces_instead_of_tabs(use_spaces)


class CustomIndent(GObject.Object, Gedit.WindowActivatable, 
        PeasGtk.Configurable):
    """Plugin class instantiated by gedit plugin manager.
    
    This class is also instantiated everytime the user opens the configuration 
    dialog, but the global the state is retained from the first instantiation.
    The do_activate() method is called when the plugin loads for the first 
    time and loads all definitions needed.
    """

    __gtype_name__ = "CustomIndent"
    window = GObject.property(type = Gedit.Window)

    def __init__(self):
        """Initialize plugin."""
        GObject.Object.__init__(self)
        # Flag needed to control if the status bar tab width combo box events
        # are called when a new document is loaded or when the user really
        # tries to change the language settings.
        self._tab_added = False

    def do_activate(self):
        """Load settings."""
        Settings.load()
        Context.init(self.window)
        Context.apply_settings()
        Context.get_window().connect("tab-added", self._on_tab_added)
        Context.get_statusbar_language_combobox().connect("changed", 
            self._on_statusbar_language_combobox_changed)
        Context.get_statusbar_tabwidth_combobox().connect("changed",
            self._on_statusbar_tabwidth_combobox_changed)

    def do_deactivate(self):
        """Save settings."""
        Settings.save()

    def do_update_state(self):
        pass

    def do_create_configure_widget(self):
        """Create and display configuration widget."""
        return ConfigWidget().get_root()

    def _on_tab_added(self, window, tab):
        """Connect event handlers to the new document."""
        self._tab_added = True
        tab.get_document().connect("loaded", self._on_document_loaded)

    def _on_document_loaded(self, document, error):
        """Applies selected language settings to documents."""
        if document.get_language() != None:
            lang_id = document.get_language().get_id()
            Context.apply_settings([lang_id])

    def _on_statusbar_language_combobox_changed(self, combobox, item):
        """Applies selected language settings to documents."""
        lang_name = item.get_label()
        lang_id = Settings.get_lang_id_from_name(lang_name)
        if lang_id != None:
            Context.apply_settings([lang_id])

    def _on_statusbar_tabwidth_combobox_changed(self, combobox, item):
        """Applies selected language settings to documents."""
        doc = Context.get_window().get_active_document()
        lang = doc.get_language()
        if lang == None: return
        lang_id = doc.get_language().get_id()
        if type(item) == Gtk.CheckMenuItem:
            tab_width, use_spaces = Settings.get_lang_settings(lang_id)
            use_spaces = item.get_active()
            Settings.set_lang_settings(lang_id, tab_width, use_spaces)
            Context.apply_settings([lang_id])
        else:
            if self._tab_added:
                self._tab_added = False
                return
            tab_width, use_spaces = Settings.get_lang_settings(lang_id)
            tab_width = int(item.get_label())
            Settings.set_lang_settings(lang_id, tab_width, use_spaces)
            Context.apply_settings([lang_id])
