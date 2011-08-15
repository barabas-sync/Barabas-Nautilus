# vim: set expandtab set ts=4 tw=4

from gi.repository import Nautilus, Gtk

class ShareInfoMenuItem(gobject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        pass

    def menu_activate_cb(self, menu, file):
        print "CLICK"

    def get_file_items(self, window, files):
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
        item = Nautilus.MenuItem(name='NautilusPython::view_lpf_item',
                              label='View sharing info' ,
                             tip='View sharing info of %s' % file.get_name())
        item.connect('activate', self.menu_activate_cb, file)
        return item,
