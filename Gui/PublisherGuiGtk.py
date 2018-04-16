import Entidades.Init
from Entidades.Publishers import Publishers

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class PublisherGtk(Gtk.Window):
    window = None

    def __init__(self, session = None, **kw):
        Gtk.Window.__init__(self, **kw)
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        handlers = {"getFirst": self.getFirst}

        self.publishersManager = Publishers.Publishers()
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Formularios GTK-II.glade")
        self.builder.connect_signals(handlers)
        self.add(self.builder.get_object("PublisherGtk"))

    def getFirst(self, widget):

        publisher = self.publishersManager.getFirst()
        self._copy_to_window(publisher)

    def _copy_to_window(self,publisher):
        # self.clearWindow()
        if publisher is not None:
            self.window.nombre.insert(0, publisher.name)
            # self.entradaNombre.insert(0, publisher.name)
            # self.entradaUrl.insert(0, publisher.siteDetailUrl)
            # self.textoDescripcion.config(text=publisher.deck)
    def clearWindow(self):
        # self.entradaId.delete(0, END)
        # self.entradaNombre.delete(0, END)
        # self.entradaUrl.delete(0, END)
        # self.textoDescripcion.config(text='')
        pass

#
# builder = Gtk.Builder()
# builder.add_from_file("../Formularios GTK.glade")
# window = builder.get_object("PublisherGui")
pub = PublisherGtk()
pub.show_all()
Gtk.main()