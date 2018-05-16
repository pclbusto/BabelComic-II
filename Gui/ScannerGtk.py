import os
import Entidades.Init
from Entidades.Publishers import Publishers
from Entidades.Setups. Setup import  Setup

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class ScannerGtk():

    def __init__(self,  session=None,):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext, 'getLast': self.getLast}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Formularios GTK.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("ScannerGtk")
        # self.window.connect("delete-event", self.salir)


    def salir(self,arg1,arg2):
        return True

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
            # if publisher.localLogoImagePath

            if publisher.localLogoImagePath:
                if publisher.localLogoImagePath[-3].lower()=='gif':
                    gif = GdkPixbuf.PixbufAnimation.new_from_file(publisher.localLogoImagePath).get_static_image()
                    self.publisher_logo_image.set_from_pixbuf(gif.scale_simple(250, 250, 3))
                else:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        filename=self.path_publisher_logo+publisher.localLogoImagePath,
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
    pub = ScannerGtk()
    pub.window.show_all()
    Gtk.main()