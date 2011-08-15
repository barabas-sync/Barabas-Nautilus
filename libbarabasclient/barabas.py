# vim: set expandtab set ts=4 tw=4

import dbus
from dbus.mainloop.glib import DBusGMainLoop

class BarabasClient:
    def __init__(self):
        self.__bus = dbus.SessionBus(
               mainloop=DBusGMainLoop(set_as_default=False))
        self.__dbus_client = self.__bus.get_object(
                                 'be.ac.ua.comp.Barabas',
                                 '/be/ac/ua/comp/Barabas')
        self.__dbus_iface = dbus.Interface(
                                self.__dbus_client,
                                dbus_interface='be.ac.ua.comp.Barabas')
    
    def get_local_file_info(self, uri):
        dbus_id = self.__dbus_iface.GetFileIdForUri(uri)
        
        local_file = self.__bus.get_object(
                         'be.ac.ua.comp.Barabas',
                         '/be/ac/ua/comp/Barabas/local_files/' + str(dbus_id))
        local_file_info = dbus.Interface(
                             local_file,
                             dbus_interface='be.ac.ua.comp.Barabas.LocalFile')
        return local_file_info, dbus_id
    
    def get_remote_file_info(self, file_id):
        remote_file = self.__bus.get_object(
                         'be.ac.ua.comp.Barabas',
                         '/be/ac/ua/comp/Barabas/local_files/' + str(file_id) + '/synced_file')
        remote_file_info = dbus.Interface(
                             remote_file,
                             dbus_interface='be.ac.ua.comp.Barabas.SyncedFile')
                             
        remote_file_info.get_version = lambda version_id: self.get_synced_file_version(file_id, version_id)
        return remote_file_info
    
    def get_synced_file_version(self, file_id, version_id):
        file_version = self.__bus.get_object(
                         'be.ac.ua.comp.Barabas',
                         '/be/ac/ua/comp/Barabas/local_files/' + str(file_id) + '/synced_file/versions/' + str(version_id))
        return dbus.Interface(file_version,
                              dbus_interface='be.ac.ua.comp.Barabas.SyncedFileVersion')
