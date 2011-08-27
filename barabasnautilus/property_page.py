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

from gi.repository import Gtk

class PropertyPage:
    """The property page that gives Barabas status information for this file"""
    def __init__(self, client, uibuilder, uri):
        """Constructor"""
        self.client = client
        self.uibuilder = uibuilder
        self.uri = uri
        self.local_file, self.local_file_dbus_id = \
                client.get_local_file_info(uri)
        self.local_file.connect_to_signal("Synced", self.on_local_synced)
        self.remote_file = None
        self.version_ids_to_iter_map = {}
        
        uibuilder.connect_signals(self)
        self.box = uibuilder.get_object('propertyPageGrid')
        self.box.connect('destroy', self.on_property_page_quit)
        self.taglist_model = uibuilder.get_object('taglist_model')
        self.versions_model = uibuilder.get_object('version_model')
        
        self.delete_selected_tag_button = \
                uibuilder.get_object('delete_selected_tag_button')
        self.taglist = uibuilder.get_object('taglist')
        self.taglist.get_selection().connect('changed',
                                             self.tag_selection_changed)
        self.tagnamecolumn = uibuilder.get_object('tagnamecolumn')
        self.tagnamecolumn.set_sort_order(Gtk.SortType.ASCENDING)
        self.tagnamecolumn.clicked()
        
        self.__initialized_sync = False 
        if (self.local_file.IsSynced()):
            self.remote_file = client.get_remote_file_info(
                    self.local_file_dbus_id)
            self.prepare_remote_file()
        
        #TODO: this should be in the glade file IMHO, but I don't think this
		# is already exposed in GLade's UI.        
        uibuilder.get_object('tagsScrolledWindow').get_style_context().\
                set_junction_sides(Gtk.JunctionSides.BOTTOM)
        uibuilder.get_object('manageTagsToolbar').get_style_context().\
                set_junction_sides(Gtk.JunctionSides.TOP)
        uibuilder.get_object('manageTagsToolbar').get_style_context().\
                add_class("inline-toolbar")

    def on_property_page_quit(self, property_page):
        """The property page quits"""
        self.local_file.Release()

    def prepare_remote_file(self):
        """Called when the remote file is available. Connects to signals etc"""
        self.remote_file.connect_to_signal("Tagged",
                                           self.on_new_tag)
        self.remote_file.connect_to_signal("VersionAdded",
                                           self.on_version_added)
        self.remote_file.connect_to_signal("VersionRemoved",
                                           self.on_version_removed)
        if self.__initialized_sync == False:
            self.set_initial_tags()
        self.set_initial_versions()

    def set_initial_tags(self):
        """Empty docstring"""
        if self.remote_file == None:
            return
        
        for tag in self.remote_file.Tags():
            self.taglist_model.append((tag, False))
    
    def set_initial_versions(self):
        """Empty docstring"""
        for version_id in self.remote_file.Versions():
            self.on_version_added(version_id)
    
    def get_remote_file(self):
        """Empty docstring"""
        self.remote_file = self.client.get_remote_file_info(
                self.local_file_dbus_id)
    
    def on_local_synced(self):
        """Empty docstring"""
        if (self.remote_file == None):
            self.get_remote_file()
        self.prepare_remote_file()
    
    def on_version_added(self, new_version_id):
        """Empty docstring"""
        version = self.remote_file.get_version(new_version_id)
        
        iter = self.versions_model.append((version.GetName(), 0, False))
        self.version_ids_to_iter_map[new_version_id] = iter
        version.connect_to_signal("UploadStarted",
                                  lambda: self.on_upload_started(iter))
        version.connect_to_signal("UploadProgressed",
                                  lambda p, t: self.on_upload_progress(p, t, iter))
        version.connect_to_signal("UploadStopped",
                                  lambda: self.on_upload_stopped(iter))

    def on_version_removed(self, old_version_id):
        """Empty docstring"""
        version_iter = self.version_ids_to_iter_map[old_version_id]
        del self.version_ids_to_iter_map[old_version_id]
        self.versions_model.remove(version_iter)

    def on_upload_started(self, iter):
        """Empty docstring"""
        self.versions_model.set_value(iter, 2, True)

    def on_upload_stopped(self, iter):
        """Empty docstring"""
        self.versions_model.set_value(iter, 2, False)

    def on_upload_progress(self, progress, total, iter):
        """Empty docstring"""
        percent = int((progress * 100.0) // total)
        self.versions_model.set_value(iter, 1, percent)

    #def on_status_changed(self, status):
    #    if status == 0:
    #        self.status_label.set_text("Not synchronized")
    #    elif status == 1:
    #        self.status_label.set_text("Up To Date")
    #    elif status == 2:
    #        self.status_label.set_text("Locally changed")
    #    elif status == 3:
    #        self.status_label.set_text("Out of sync")
    #    elif status == 4:
    #        self.status_label.set_text("Synchronizing")

    def get_tab(self):
        """Empty docstring"""
        return self.box
    
    def on_new_tag(self, tag):
        """Empty docstring"""
        found = False

        iter = self.taglist_model.get_iter_first()
        while iter != None and found == False:
            if self.taglist_model.get(iter, 0) == (tag, ):
                found = True
            iter = self.taglist_model.iter_next(iter)

        if not found:
            self.taglist_model.append((tag, False))
    
    def on_deleted_tag(self, tag, local):
        """Empty docstring"""
        def check_and_delete(model, path, iter, userdata):
            """Empty docstring"""
            if model.get_value(iter, 0) == tag:
                self.taglist_model.remove(iter)
    
        self.taglist_model.foreach(check_and_delete, None)

    def new_tag(self, button):
        """Empty docstring"""
        iter = self.taglist_model.append(('New tag', True))
        self.taglist.set_cursor(self.taglist_model.get_path(iter),
                                 self.tagnamecolumn,
                                 True)
    
    def tag_edited(self, cell_renderer, path, new_text):
        """Empty docstring"""
        if (self.remote_file == None):
            # We have to initiate sync first
            self.__initialized_sync = True
            self.local_file.Sync()
            self.get_remote_file()
    
        iter = self.taglist_model.get_iter(path)
        self.taglist_model.set_value(iter, 0, new_text)
        self.taglist_model.set_value(iter, 1, False)
        self.delete_selected_tag_button.set_sensitive(True)
        if not self.remote_file.Tag(new_text):
            self.__remove_tag_from_model(iter)
            
    
    def tag_editing_canceled(self, cell_renderer):
        """Empty docstring"""
        treeview, selected_iter = self.taglist.get_selection().get_selected()
        tag_name, = self.taglist_model.get(selected_iter, 0)
        self.__remove_tag_from_model(selected_iter)
    
    def tag_selection_changed(self, selection):
        """Empty docstring"""
        treeview, selected_iter = selection.get_selected()
        self.delete_selected_tag_button.set_sensitive(selected_iter != None)
    
    def delete_current_tag(self, button = None):
        """Empty docstring"""
        # TODO: ask confirmation?
        treeview, selected_iter = self.taglist.get_selection().get_selected()
        tag_name, = self.taglist_model.get(selected_iter, 0)
        self.__remove_tag_from_model(selected_iter)
        
        self.remote_file.Untag(tag_name)
    
    def __remove_tag_from_model(self, iter):
        """Empty docstring"""
        self.taglist_model.remove(iter)
        self.delete_selected_tag_button.set_sensitive(False)

