from Entidades.Publishers.Publisher import Publisher
import Entidades.Init
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from Entidades.Volumes.Volume import Volume
from Gui.Publisher_lookup_gtk import Publisher_lookup_gtk


class Volume_lookup_gtk():
    def __init__(self, session=None, campo_retorno=None):
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

        self.handlers = {'search_volumen': self.search_volumen, 'search_editorial': self.search_editorial,
                         'click_lookup_editorial': self.click_lookup_editorial,
                         'seleccion_volumen':self.seleccion_volumen, 'click_boton_aceptar':self.click_boton_aceptar,
                         'gtk_tree_view_volumen_double_click':self.gtk_tree_view_volumen_double_click}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Volumen_lookup_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volumen_lookup_gtk")
        self.search_entry_editorial = self.builder.get_object("search_entry_editorial")
        self.imagen_cover_volumen = self.builder.get_object("imagen_cover_volumen")
        self.gtk_tree_view_volumen = self.builder.get_object('gtk_tree_view_volumen')
        self.listmodel_volumens =self.builder.get_object("listmodel_volumens")
        self.label_nombre_editorial = self.builder.get_object("label_nombre_editorial")
        self.volumens = self.session.query(Volume).all()
        self.search_entry_volumen = self.builder.get_object('search_entry_volumen')
        self.search_entry_editorial = self.builder.get_object('search_entry_editorial')
        self._load_data()
        if campo_retorno is None:
            print("error campo retorno requerido")
        self.campo_retorno = campo_retorno
        self.publisher=None
        self.volume = None

    def gtk_tree_view_volumen_double_click(self,widget, event):
        if event.get_click_count()[1]==2:
            self.click_boton_aceptar(widget)

    def search_volumen(self, widget):
        if self.search_entry_volumen.get_text()=='' and not self.publisher:
            self.volumens = self.session.query(Volume).all()
        elif self.search_entry_volumen.get_text()=='' and self.publisher:
            self.volumens = self.session.query(Volume).filter(Volume.publisherId==self.publisher.id_publisher)
        elif self.search_entry_volumen.get_text() != '' and not self.publisher:
            self.volumens = self.session.query(Volume).filter(Volume.nombre.like('%{}%'.format(self.search_entry_volumen.get_text())))
        else:
            self.volumens = self.session.query(Volume).filter(Volume.nombre.like(
                '%{}%'.format(self.search_entry_volumen.get_text())),Volume.publisherId==self.publisher.id_publisher)
        self._load_data()

    def search_editorial(self, widget):
        if self.search_entry_editorial.get_text()=='':
            self.publisher = None
        else:
            self.publisher = self.session.query(Publisher).filter(Publisher.id_publisher==self.search_entry_editorial.get_text()).first()
            if self.publisher:
                self.label_nombre_editorial.set_text(self.publisher.name)
        self.search_volumen(widget)

    def click_lookup_editorial(self, widget):
        lookup = Publisher_lookup_gtk(self.session,self.search_entry_editorial)
        lookup.window.show()

    def _load_data(self):
        self.listmodel_volumens.clear()
        for index,volume in enumerate(self.volumens):
            self.listmodel_volumens.append(
                [volume.id, volume.nombre, volume.cantidadNumeros, volume.publisher_name, volume.AnioInicio, index])
            # self.listmodel_volumens.append(
            #     [volume.id, volume.nombre, volume.cantidadNumeros, volume.publisher_name, volume.AnioInicio])
        self.gtk_tree_view_volumen.set_model(self.listmodel_volumens)

    def getSerie(self):
        print('retornando serie: ' + self.serie.nombre)
        return self.serie

    def seleccion_volumen(self, selection):
        (model, iter) = selection.get_selected()
        if iter:
            self.volume = self.volumens[model[iter][5]]
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=self.volume.getImagePath(),
                width=250,
                height=250,
                preserve_aspect_ratio=True)
            self.imagen_cover_volumen.set_from_pixbuf(pixbuf)

    def click_boton_aceptar(self,widget):
        self.campo_retorno.set_text(self.volume.id)
        self.window.close()


if (__name__ == '__main__'):
    volumens_lookup = Volume_lookup_gtk(campo_retorno="")
    volumens_lookup.window.show_all()
    volumens_lookup.window.connect("destroy", Gtk.main_quit)
    Gtk.main()