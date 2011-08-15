# vim: set expandtab set ts=4 tw=4
#
# This file is part of Barabas Nautilus Plugin.
#
# Copyright (C) 2011 Nathan Samson
# Barabas Nautilus Plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Barabas Nautilus Plugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Barabas Nautilus Plugin. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Nautilus, Gtk

class ShareInfoMenuItem(gobject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        """Empty docstring"""
        pass

    def menu_activate_cb(self, menu, file):
        """Empty docstring"""
        print "CLICK"

    def get_file_items(self, window, files):
        """Empty docstring"""
        if len(files) != 1:
          return

        file = files[0]
        if not file.is_directory() or file.get_uri_scheme() != 'file':
         return

        item = Nautilus.MenuItem(name='NautilusPython::view_lpf_file_item',
                                label='View sharing info' ,
                                 tip='View sharing info of %s' % file.get_name())
        item.connect('activate', self.menu_activate_cb, file)
        return item,

    def get_background_items(self, window, file):
        """Empty docstring"""
        item = Nautilus.MenuItem(name='NautilusPython::view_lpf_item',
                              label='View sharing info' ,
                             tip='View sharing info of %s' % file.get_name())
        item.connect('activate', self.menu_activate_cb, file)
        return item,
