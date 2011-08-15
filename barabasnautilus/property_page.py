# vim: set expandtab set ts=4 tw=4

from gi.repository import Nautilus, Gtk

class PropertyPage:
    def __init__(self, client, uibuilder, uri):
        self.client = client
        self.uibuilder = uibuilder
        self.uri = uri
        self.local_file, self.local_file_dbus_id = client.get_local_file_info(uri)
        self.local_file.connect_to_signal("Synced", self.on_local_synced)
        self.remote_file = None
        
        uibuilder.connect_signals(self)
        self.box = uibuilder.get_object('propertyPageGrid')
        self.taglist_model = uibuilder.get_object('taglist_model')
        self.versions_model = uibuilder.get_object('version_model')
        
        self.delete_selected_tag_button = uibuilder.get_object('delete_selected_tag_button')
        self.taglist = uibuilder.get_object('taglist')
        self.taglist.get_selection().connect('changed', self.tag_selection_changed)
        self.tagnamecolumn = uibuilder.get_object('tagnamecolumn')
        self.tagnamecolumn.set_sort_order(Gtk.SortType.ASCENDING)
        self.tagnamecolumn.clicked()
        
        self.__initialized_sync = False 
        if (self.local_file.IsSynced()):
            self.remote_file = client.get_remote_file_info(self.local_file_dbus_id)
            self.prepare_remote_file()
        #self.local_file.connect_to_signal("Tagged", self.on_new_tag)
        #self.local_file.connect_to_signal("Untagged", self.on_deleted_tag)
        #self.local_file.connect_to_signal("StatusChanged", self.on_status_changed)
        #self.local_file.connect_to_signal("SyncStarted", self.on_sync_started)
        #self.local_file.connect_to_signal("SyncStopped", self.on_sync_stopped)
        #self.local_file.connect_to_signal("SyncProgress", self.on_sync_progress)
        
        

        
        
        #for version_id in self.local_file.Versions():
        #	version = client.get_version_info(version_id)
        #	self.versions_model.append((str(version.GetDatetimeEdited()), version.GetId()))
        #self.local_file.connect_to_signal("VersionAdded", self.on_version_added)
        #self.taglist = uibuilder.get_object('taglist')
        #self.taglist.get_selection().connect('changed', self.tag_selection_changed)
        #self.tagnamecolumn = uibuilder.get_object('tagnamecolumn')
        #self.tagnamecolumn.set_sort_order(Gtk.SortType.ASCENDING)
        #self.tagnamecolumn.clicked()
        #self.delete_selected_tag_button = uibuilder.get_object('delete_selected_tag_button')
        #self.status_label = uibuilder.get_object('statusLabel')
        #self.on_status_changed(self.local_file.GetFuckingStatus())
        
        #TODO: this should be in the glade file IMHO, but I don't think this
		# is already exposed in GLade's UI.        
        uibuilder.get_object('tagsScrolledWindow').get_style_context().set_junction_sides(Gtk.JunctionSides.BOTTOM)
        uibuilder.get_object('manageTagsToolbar').get_style_context().set_junction_sides(Gtk.JunctionSides.TOP)
        uibuilder.get_object('manageTagsToolbar').get_style_context().add_class("inline-toolbar")

    def prepare_remote_file(self):
        self.remote_file.connect_to_signal("Tagged", self.on_new_tag)
        self.remote_file.connect_to_signal("VersionAdded", self.on_version_added)
        self.remote_file.connect_to_signal("VersionRemoved", self.on_version_removed)
        if self.__initialized_sync == False:
            self.set_initial_tags()
        self.set_initial_versions()

    def set_initial_tags(self):
        if self.remote_file == None:
            return
        
        for tag in self.remote_file.Tags():
            self.taglist_model.append((tag, False))
    
    def set_initial_versions(self):
        for version_id in self.remote_file.Versions():
            self.on_version_added(version_id)
    
    def get_remote_file(self):
         self.remote_file = self.client.get_remote_file_info(self.local_file_dbus_id)
    
    def on_local_synced(self):
        if (self.remote_file == None):
            self.get_remote_file()
        self.prepare_remote_file()
    
    def on_version_added(self, new_version_id):
        version = self.remote_file.get_version(new_version_id)
        
        iter = self.versions_model.append((version.GetName(),
                                           0, False))
        version.connect_to_signal("UploadStarted", lambda: self.on_upload_started(iter))
        version.connect_to_signal("UploadProgressed", lambda p, t: self.on_upload_progress(p, t, iter))
        version.connect_to_signal("UploadStopped", lambda: self.on_upload_stopped(iter))

    def on_version_removed(self, old_version_id):
        print "Removing ", old_version_id

    def on_upload_started(self, iter):
        self.versions_model.set_value(iter, 2, True)

    def on_upload_stopped(self, iter):
        self.versions_model.set_value(iter, 2, False)

    def on_upload_progress(self, progress, total, iter):
        percent = int((progress * 100.0) // total)
        self.versions_model.set_value(iter, 1, percent)

    def on_status_changed(self, status):
        if status == 0:
            self.status_label.set_text("Not synchronized")
        elif status == 1:
            self.status_label.set_text("Up To Date")
        elif status == 2:
            self.status_label.set_text("Locally changed")
        elif status == 3:
            self.status_label.set_text("Out of sync")
        elif status == 4:
            self.status_label.set_text("Synchronizing")

    def get_tab(self):
        return self.box
    
    def on_new_tag(self, tag):
        found = False

        iter = self.taglist_model.get_iter_first()
        while iter != None and found == False:
          if self.taglist_model.get(iter, 0) == (tag, ):
            found = True
          iter = self.taglist_model.iter_next(iter)

        if not found:
          self.taglist_model.append((tag, False))
    
    def on_deleted_tag(self, tag, local):
        def check_and_delete(model, path, iter, userdata):
            if model.get_value(iter, 0) == tag:
                self.taglist_model.remove(iter)
    
        self.taglist_model.foreach(check_and_delete, None)

    def new_tag(self, button):
        iter = self.taglist_model.append(('New tag', True))
        self.taglist.set_cursor(self.taglist_model.get_path(iter),
                                 self.tagnamecolumn,
                                 True)
    
    def tag_edited(self, cell_renderer, path, new_text):
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
        treeview, selected_iter = self.taglist.get_selection().get_selected()
        tag_name, = self.taglist_model.get(selected_iter, 0)
        self.__remove_tag_from_model(selected_iter)
    
    def tag_selection_changed(self, selection):
        treeview, selected_iter = selection.get_selected()
        self.delete_selected_tag_button.set_sensitive(selected_iter != None)
    
    def delete_current_tag(self, button = None):
        # TODO: ask confirmation?
        treeview, selected_iter = self.taglist.get_selection().get_selected()
        tag_name, = self.taglist_model.get(selected_iter, 0)
        self.__remove_tag_from_model(selected_iter)
        
        self.remote_file.Untag(tag_name)
    
    def __remove_tag_from_model(self, iter):
        self.taglist_model.remove(iter)
        self.delete_selected_tag_button.set_sensitive(False)

