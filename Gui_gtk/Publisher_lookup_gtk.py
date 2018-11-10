from Entidades.Entitiy_managers import Publishers
from Entidades.Agrupado_Entidades import Publisher
import Entidades.Init
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class Publisher_lookup_gtk():
    # todo implementar seleccion por doble click
    
    def __init__(self, session=None, campo_retorno=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'clicked_aceptar': self.clicked_aceptar, 'buscar':self.buscarPublisher,
                         'seleccion':self.seleccion_publisher, 'combobox_change':self.combobox_change}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Publisher_lookup_gtk.glade")
        self.builder.connect_signals(self.handlers)

        self.window = self.builder.get_object("Publisher_lookup_gtk")
        self.liststore_combobox = self.builder.get_object("liststore_combobox")
        self.combobox_orden = self.builder.get_object('combobox_orden')
        self.gtk_tree_view_editorial =  self.builder.get_object('gtk_tree_view_editorial')
        self.listmodel_publishers = Gtk.ListStore(int, str)
        self.publishers_manager = Publishers(session=self.session)
        self.search_entry = self.builder.get_object('search_entry')
        self._load_data()
        if campo_retorno is None:
            print("error campo retorno requerido")
        self.campo_retorno = campo_retorno

        # inicializamos el modelo con rotulos del manager
        self.liststore_combobox.clear()
        for clave in self.publishers_manager.lista_opciones.keys():
            self.liststore_combobox.append([clave])
        self.combobox_orden.set_active(0)

    def combobox_change(self,widget):
        if widget.get_active_iter() is not None:
            self.publishers_manager.set_order(self.publishers_manager.lista_opciones[widget.get_model()[widget.get_active_iter()][0]])
            self._load_data()

    def _load_data(self):
        self.listmodel_publishers.clear()
        for publisher in self.publishers_manager.getList():
            self.listmodel_publishers.append([publisher.id_publisher, publisher.name])
        self.gtk_tree_view_editorial.set_model(self.listmodel_publishers)

    def getPublisher(self):

        print('retornando serie: ' + self.publisher.name)
        return self.publisher

    def seleccion_publisher(self, selection):
        (model, iter) = selection.get_selected()
        if iter:
            self.publisher = self.publishers_manager.get(model[iter][0])

    def clicked_aceptar(self,widget):
        self.campo_retorno(self.publisher.id_publisher)
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
