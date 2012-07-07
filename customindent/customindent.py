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
    import cPickle as pickle
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
    _lm = GtkSource.LanguageManager()

    @staticmethod
    def load():
        """Loads language settings."""
        settings_path = Settings.get_path()
        if not os.path.exists(settings_path):
            lang_ids = Settings._lm.get_language_ids()
            for lang_id in lang_ids:
                Settings._settings[lang_id] = (Settings.DEFAULT_TAB_WIDTH, 
                        Settings.DEFAULT_USE_SPACES)
        else:
            try:
                f = open(settings_path, "rb")
            except IOError:
                print "Failed to load settings."
                sys.exit(1)
            Settings._settings = pickle.load(f)
            f.close()

    @staticmethod
    def save():
        """Saves language settings."""
        settings_path = Settings.get_path()
        try:
            f = open(settings_path, "wb")
        except IOError:
            print "Failed to save settings."
            sys.exit(1)
        pickle.dump(Settings._settings, f)
        f.close()

    @staticmethod
    def get_path():
        """Returns the settings file path."""
        path = os.path.expanduser("~/.local/share/gedit/plugins/customindent/")
        return path + Settings.SETTINGS_FILENAME

    @staticmethod
    def get_lang_settings():
        """Returns language settings."""
        return Settings._settings


class ConfigWidget(object):
    """Builds configuration UI objects. It does not represent the whole dialog,
    but a child element that will be managed by gedit and plugged into a dialog.
    """

    def __init__(self):
        """Constructs the configuration widget."""
        self._root = None
        self._combo = None
        self._spin = None
        self._check = None
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
        for lang_id in sorted(Settings.get_lang_settings().keys()):
            store.append([lang_id])
        self._combo = Gtk.ComboBoxText()
        self._combo.set_model(store)
        self._combo.set_active(0)
        # Create tab width spinner.
        self._spin = Gtk.SpinButton()
        self._spin.set_adjustment(Gtk.Adjustment(4, 1, 16, 1))
        # Create spaces check box.
        self._check = Gtk.CheckButton()
        # Set event handlers.
        self._combo.connect("changed", self._on_combo_changed)
        self._spin.connect("value-changed", self._on_spin_changed)
        self._check.connect("toggled", self._on_check_changed)
        # Pack.
        self._root = Gtk.Table(3, 2)
        self._root.attach(Gtk.Label("Language"), 0, 1, 0, 1, xpadding = 12)
        self._root.attach(self._combo, 1, 2, 0, 1, ypadding = 6)
        self._root.attach(Gtk.Label("Tab width"), 0, 1, 1, 2, xpadding = 12)
        self._root.attach(self._spin, 1, 2, 1, 2, ypadding = 6)
        self._root.attach(Gtk.Label("Use spaces"), 0, 1, 2, 3, xpadding = 12)
        self._root.attach(self._check, 1, 2, 2, 3, ypadding = 6)
        self._load(self._combo.get_active_text())

    def _on_combo_changed(self, combo):
        """Called when language combobox changes it's value. Loads selected
        language configuration.
        """
        lang_id = combo.get_active_text()
        self._load(lang_id)
 
    def _on_spin_changed(self, spin):
        """Called when the tabs width is changed. Saves language settings."""
        self._save()        

    def _on_check_changed(self, check):
        """Called when the tabs or spaces checkbox is changed. 
        Saves language settings.
        """
        self._save()

    def _save(self):
        """Save language settings from the configuration dialog."""
        lang_id = self._combo.get_active_text()
        tab_width = self._spin.get_value_as_int()
        use_spaces = self._check.get_active()
        Settings.get_lang_settings()[lang_id] = (tab_width, use_spaces)
        Context.apply_settings([lang_id])

    def _load(self, lang_id):
        """Load language settings to configuration dialog."""
        lang_settings = Settings.get_lang_settings()[lang_id]
        self._spin.get_adjustment().set_value(lang_settings[0])
        self._check.set_active(lang_settings[1])


class Context(object):
    """Stores global objects."""

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
    def apply_settings(lang_ids = []):
        """Applies current language settings from a specified language list to
        opened documents."""
        for doc in Context.get_window().get_documents():
            lang = doc.get_language()
            if lang == None or (not lang.get_id() in lang_ids):
                continue
            view = Gedit.Tab.get_from_document(doc).get_view()
            settings = Settings.get_lang_settings()[lang.get_id()]
            view.set_tab_width(settings[0])
            view.set_insert_spaces_instead_of_tabs(settings[1])


class CustomIndent(GObject.Object, Gedit.WindowActivatable, 
        PeasGtk.Configurable):
    """Plugin class instantiated by gedit plugin manager.
    
    This class is also instantiated when the user tries to open the
    configuration dialog. This caused some problems which implied the
    implementation of Settings and Context classes with static methods. Other
    classes might need to access the gedit window, and the easiest way to do it
    is to expose it globally when the plugin is initialized.
    """

    __gtype_name__ = "CustomIndent"
    window = GObject.property(type = Gedit.Window)

    def __init__(self):
        """Initialize plugin and language settings."""
        GObject.Object.__init__(self)

    def do_activate(self):
        """Load settings."""
        Settings.load()
        Context.init(self.window)
        Context.apply_settings()
        self.window.connect("tab-added", self._on_tab_added)

    def do_deactivate(self):
        """Save settings."""
        Settings.save()

    def do_update_state(self):
        """Do nothing."""
        pass

    def do_create_configure_widget(self):
        """Create configuration widget."""
        return ConfigWidget().get_root()

    def _on_tab_added(self, window, tab):
        """Add event handlers to the new document."""
        tab.get_document().connect("loaded", self._on_document_loaded)

    def _on_document_loaded(self, document, error):
        """Apply language settings to document."""
        if document.get_language() != None:
            Context.apply_settings([document.get_language().get_id()])
