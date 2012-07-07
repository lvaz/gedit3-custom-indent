Gedit Custom Indent
-------------------

A plugin for gedit3 that allows to customize indentation settings for each 
language

* Authors:
  * Leandro Vaz
* Version: 0.0.1


Installation
------------

1. Download Custom Indent
2. Check if ~/.local/share/gedit/plugins/ directory exists. If not, create the
   missing directories.
3. Copy the folder named customindent to ~/.local/share/gedit/plugins/
4. Restart gedit if opened
5. Activate the plugin under 'Edit -> Preferences -> Plugins'


Usage
-----

The plugin manages indentation settings for your gedit. If you want to use
this plugin, then you should not set indentation settings using the standard 
way, but only with this plugin. To set indent settings, just open the 
configuration dialog under Edit -> Preferences -> Plugins -> Custom Indent 
-> Preferences and select the languages you which to change indent settings.
All settings are automatically applied once set. Finally, the plugin saves
all settings to a file named settings.pkl under the plugin directory. For some
reason, if the plugin does not initialize because the settings file is 
corrupted, you should delete it.


License
-------

Copyright (C) 2012 Leandro Vaz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
