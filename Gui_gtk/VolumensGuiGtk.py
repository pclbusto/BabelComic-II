import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GLib, GObject
from gi.repository import Gdk

import Entidades.Init
from Entidades.Agrupado_Entidades import Comicbook, Publisher, Volume, Comicbook_Info, Arcos_Argumentales_Comics_Reference, Comicbook_Detail
from Entidades.Agrupado_Entidades import Setup
from Gui_gtk.ScannerGtk import ScannerGtk
from Gui_gtk.PublisherGuiGtk import PublisherGtk
from Gui_gtk.VolumeGuiGtk import VolumeGuiGtk
#lo usamos para reutilizar la generacion de thumnails
from Entidades.Entitiy_managers import Commicbooks_detail

from Gui_gtk.Comicbook_Detail_Gtk import Comicbook_Detail_Gtk
from Gui_gtk.Comic_vine_cataloger_gtk import Comic_vine_cataloger_gtk
from Gui_gtk.config_gtk import Config_gtk
from Gui_gtk.acerca_de_gtk import Acerca_de_gtk
from Gui_gtk.function_launcher_Gtk import Function_launcher_gtk
from Extras import BabelComics_Manager
import os.path
import math
from PIL import Image, ImageFile
import threading



class Volumens_gtk():

    def __init__(self, session=None):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

        self.load_setup()

        self.handlers = {'activar_busqueda': self.activar_busqueda,
                         'entrada_teclado_barra_busqueda': self.entrada_teclado_barra_busqueda}

        self.cataloged_pix = Pixbuf.new_from_file_at_size('../iconos/Cataloged.png', 32, 32)

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Volumens.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volumens")
        self.app_icon = Pixbuf.new_from_file_at_size('../iconos/iconoBabelComics-buuf.png', 32, 32)
        self.window.set_icon_from_file('../iconos/iconoBabelComics-buuf.png')
        self.window.set_default_icon_list([self.app_icon])
        self.iconview_volumens = self.builder.get_object('iconview_volumens')
        self.barra_busqueda = self.builder.get_object('barra_busqueda')
        self.volumen_search_entry = self.builder.get_object('volumen_search_entry')
        self.thread_creacion_thumnails = None
        self.lista_comics_esperando_por_thumnail=[]
        self.updating_gui = False
        self.salir_thread = False

        self.liststore = Gtk.ListStore(Pixbuf, str)
        self.lista_pendientes = []
        self.filtro = ''
        self.limit = self.session.query(Setup).first().cantidadComicsPorPagina
        self.offset = 0
        self.query = None
        self.manager = BabelComics_Manager.BabelComics_Manager()

        self.cantidad_thumnails_pendiente=0
        #self.search_change(None)

        self.iconview_volumens.set_column_spacing(-1)
        self.iconview_volumens.set_item_padding(10)
        self.iconview_volumens.set_item_width(1)
        self.iconview_volumens.set_spacing(30)

    def load_setup(self):
        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + "coverIssuesThumbnails" + os.path.sep
        self.ancho_thumnail = self.session.query(Setup).first().anchoThumnail

    def activar_busqueda(self, widget, event):
        self.barra_busqueda.set_search_mode(True)
        self.volumen_search_entry.grab_focus()

    def entrada_teclado_barra_busqueda(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.barra_busqueda.set_search_mode(False)
            self.volumen_search_entry.set_text('')
            self.iconview_volumens.grab_focus()

if __name__ == "__main__":
    GLib.set_prgname('Babelcomics')
    bc = Volumens_gtk()
    bc.window.connect("destroy", Gtk.main_quit)
    bc.window.show()
    bc.window.maximize()
    Gtk.main()