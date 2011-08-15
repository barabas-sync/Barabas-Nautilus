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

import dbus
from dbus.mainloop.glib import DBusGMainLoop

class BarabasClient:
    """Main Barabas DBus Client"""
    def __init__(self):
        """Empty docstring"""
        self.__bus = dbus.SessionBus(
               mainloop=DBusGMainLoop(set_as_default=False))
        self.__dbus_client = self.__bus.get_object(
                                 'be.ac.ua.comp.Barabas',
                                 '/be/ac/ua/comp/Barabas')
        self.__dbus_iface = dbus.Interface(
                                self.__dbus_client,
                                dbus_interface='be.ac.ua.comp.Barabas')
    
    def get_local_file_info(self, uri):
        """Empty docstring"""
        dbus_id = self.__dbus_iface.GetFileIdForUri(uri)
        
        local_file = self.__bus.get_object(
                         'be.ac.ua.comp.Barabas',
                         '/be/ac/ua/comp/Barabas/local_files/' + str(dbus_id))
        local_file_info = dbus.Interface(
                             local_file,
                             dbus_interface='be.ac.ua.comp.Barabas.LocalFile')
        return local_file_info, dbus_id
    
    def get_remote_file_info(self, file_id):
        """Empty docstring"""
        remote_file = self.__bus.get_object(
                         'be.ac.ua.comp.Barabas',
                         '/be/ac/ua/comp/Barabas/local_files/' + str(file_id) + '/synced_file')
        remote_file_info = dbus.Interface(
                             remote_file,
                             dbus_interface='be.ac.ua.comp.Barabas.SyncedFile')
                             
        remote_file_info.get_version = lambda version_id: self.get_synced_file_version(file_id, version_id)
        return remote_file_info
    
    def get_synced_file_version(self, file_id, version_id):
        """Empty docstring"""
        file_version = self.__bus.get_object(
                         'be.ac.ua.comp.Barabas',
                         '/be/ac/ua/comp/Barabas/local_files/' + str(file_id) + '/synced_file/versions/' + str(version_id))
        return dbus.Interface(file_version,
                              dbus_interface='be.ac.ua.comp.Barabas.SyncedFileVersion')
