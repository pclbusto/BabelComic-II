from Entidades.Publishers.Publisher import Publisher
from PIL import Image, ImageTk
import Entidades.Init
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class PublisherLookupData():
    ATRIBUTO_ID = 'id'
    ATRIBUTO_NOMBRE = 'nombre'
    ATRIBUTO_DESCRIPCION = 'descripcion'
    ATRIBUTO_ANIO = 'AnioInicio'

    def __init__(self):
        self.atributoBusqueda = PublisherLookupData.ATRIBUTO_NOMBRE


class Publisher_lookup_gtk():
    def __init__(self, session=None, campo_retorno=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'clicked_aceptar': self.clicked_aceptar, 'buscar':self.buscarPublisher,
                         'seleccion':self.seleccion_publisher}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Editorial_lookup.glade")
        self.builder.connect_signals(self.handlers)

        self.window = self.builder.get_object("Editorial_lookup_gtk")
        self.gtk_tree_view_editorial =  self.builder.get_object('gtk_tree_view_editorial')
        # self.gtk_tree_view_editorial.get_selection().connect("changed", self.buscarPublisher)
        # self.window.connect("destroy", Gtk.main_quit)
        self.listmodel_publishers = Gtk.ListStore(str, str)
        self.publishers = self.session.query(Publisher)
        self.search_entry = self.builder.get_object('search_entry')
        self._load_data()
        if campo_retorno is None:
            print("error campo retorno requerido")
        self.campo_retorno = campo_retorno


    def _load_data(self):
        self.listmodel_publishers.clear()
        for publisher in self.publishers:
            self.listmodel_publishers.append([publisher.id_publisher, publisher.name])
        self.gtk_tree_view_editorial.set_model(self.listmodel_publishers)

    def getPublisher(self):

        print('retornando serie: ' + self.publisher.name)
        return self.publisher

    def seleccion_publisher(self, selection):
        (model, iter) = selection.get_selected()
        if iter:
            self.publisher = self.session.query(Publisher).filter(
                Publisher.id_publisher==model[iter][0]).first()

    def clicked_aceptar(self,widget):
        print('cerramdp')
        self.campo_retorno.set_text(self.publisher.id_publisher)
        self.window.close()

    def buscarPublisher(self, widget):
        if self.search_entry.get_text()=='':
            self.publishers = self.session.query(Publisher)

        else:
            self.publishers = self.session.query(Publisher).filter(Publisher.name.like('%'+self.search_entry.get_text()+'%'))
        self._load_data()


if (__name__ == '__main__'):
    pub = Publisher_lookup_gtk()
    pub.window.show_all()
    Gtk.main()
