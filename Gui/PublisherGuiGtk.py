import os
import Entidades.Init
from Entidades.Publishers import Publishers
from Entidades.Setups. Setup import  Setup
from Gui import Publisher_lookup_gtk
from Gui.Publisher_vine_search_gtk import Publisher_vine_search_gtk

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class PublisherGtk():

    def __init__(self,  session=None,):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext,
                         'getLast': self.getLast, 'click_lookup_button':self.open_lookup, 'id_changed':self.id_changed,
                         'click_cargar_desde_web':self.click_cargar_desde_web,'boton_guardar':self.boton_guardar}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Publisher.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("PublisherGtk")
        self.publishers_manager = Publishers.Publishers()
        self.entry_id  = self.builder.get_object('entry_id')
        self.entry_nombre =  self.builder.get_object('entry_nombre')
        self.entry_url =  self.builder.get_object('entry_url')
        self.publisher_logo_image = self.builder.get_object('publisher_logo_image')
        self.label_resumen = self.builder.get_object('label_resumen')
        self.path_publisher_logo = self.session.query(Setup).first().directorioBase+ os.path.sep + "images" + os.path.sep + "logo publisher" + os.path.sep

    def boton_guardar(self,widget):
        pass

    def click_cargar_desde_web(self, widget):
        publisher_vine_search = Publisher_vine_search_gtk(self.session)
        publisher_vine_search.window.show()

    def id_changed(self,widget):
        publisher = self.publishers_manager.get(self.entry_id.get_text())
        self._copy_to_window(publisher)

    def open_lookup(self, widget):
        print('dasds')
        lookup = Publisher_lookup_gtk.Publisher_lookup_gtk(self.session,self.entry_id)
        lookup.window.show()

    def getFirst(self, widget):
        publisher = self.publishers_manager.getFirst()
        self._copy_to_window(publisher)

    def getPrev(self, widget):
        publisher = self.publishers_manager.getPrev()
        self._copy_to_window(publisher)

    def getNext(self, widget):
        publisher = self.publishers_manager.getNext()
        self._copy_to_window(publisher)

    def getLast(self, widget):
        publisher = self.publishers_manager.getLast()
        self._copy_to_window(publisher)

    def _copy_to_window(self,publisher):
        # self.clearWindow()
        if publisher is not None:
            print("cargan valores")
            self.entry_id.set_text(publisher.id_publisher)
            self.entry_nombre.set_text( publisher.name)
            self.entry_url.set_text(publisher.siteDetailUrl)
            publisher.localLogoImagePath = publisher.getImageCoverPath()
            if publisher.localLogoImagePath:
                if publisher.localLogoImagePath[-3].lower()=='gif':
                    gif = GdkPixbuf.PixbufAnimation.new_from_file(publisher.localLogoImagePath).get_static_image()
                    self.publisher_logo_image.set_from_pixbuf(gif.scale_simple(250, 250, 3))
                else:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        filename=publisher.getImageCoverPath(),
                        width=250,
                        height=250,
                        preserve_aspect_ratio=True)
                    self.publisher_logo_image.set_from_pixbuf(pixbuf)

            self.label_resumen.set_text(publisher.deck)

    def clearWindow(self):
        # self.entradaId.delete(0, END)
        # self.entradaNombre.delete(0, END)
        # self.entradaUrl.delete(0, END)
        # self.textoDescripcion.config(text='')
        pass


if __name__ == "__main__":
    pub = PublisherGtk()
    pub.window.show_all()
    pub.window.connect("destroy", Gtk.main_quit)
    Gtk.main()