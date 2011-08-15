# vim: set expandtab set ts=4 tw=4

import os.path
from gi.repository import Nautilus, Gtk, GObject

from libbarabasclient.barabas import BarabasClient
import barabasnautilus.property_page

class BarabasPropertyPageProvider(GObject.GObject, Nautilus.PropertyPageProvider):
    def __init__(self):
        """Empty docstring"""
        self.__client = BarabasClient()

    def get_property_pages(self, files): 
        """Empty docstring"""
        if len(files) != 1:
            return

        file = files[0]

        if file.get_uri_scheme() != 'file':
            return

        self.property_label = Gtk.Label('Barabas')
        self.property_label.show()
        
        uibuilder = Gtk.Builder()
        ui_file = os.path.join(os.path.dirname(__file__), 'share', 'barabas.ui')
        uibuilder.add_from_file(ui_file)

        property_page = barabasnautilus.property_page.PropertyPage(
                            self.__client, uibuilder, file.get_uri())
        return Nautilus.PropertyPage(name="NautilusPython::barabas_info",
                                     label=self.property_label,
                                     page=property_page.get_tab()),
    
