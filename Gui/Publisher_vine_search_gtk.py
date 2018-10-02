from Entidades.Publishers import Publishers
from  Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
import Entidades.Init
from Entidades.Publishers.Publisher import Publisher

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class Publisher_vine_search_gtk():
    def __init__(self,  session=None):
        config = Config()
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.comicVineSearcher = ComicVineSearcher(config.getClave('publishers'), session=self.session)
        self.comicVineSearcher.setEntidad("publishers")

        self.handlers = {'click_boton_buscar_mas': self.click_boton_buscar_mas,'selection':self.selection,
                         'click_boton_aceptar': self.click_boton_aceptar, 'click_boton_buscar':self.click_boton_buscar}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Publisher_vine_search_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volume_vine_search_Gtk")
        self.search_entry = self.builder.get_object('search_entry')
        self.publisher_logo_image = self.builder.get_object('publisher_logo_image')
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename="/home/pedro/PycharmProjects/BabelComic-II/images/logo publisher/5825355-3357700787-c1a90.jpg",
            width=250,
            height=250,
            preserve_aspect_ratio=True)
        self.publisher_logo_image.set_from_pixbuf(pixbuf)



        self.listmodel_publishers = Gtk.ListStore(str, str)
        self.gtk_tree_view_publisher =  self.builder.get_object('gtk_tree_view_publisher')

    def selection(self,selection):
        (model, iter) = selection.get_selected()
        if iter:
            self.publisher = self.comicVineSearcher.listaBusquedaVine[int(model[iter][0])]
            self.publisher.getImageCover()
            self.publisher.localLogoImagePath = self.publisher.getImageCoverPath()
            if self.publisher.localLogoImagePath[-3].lower() == 'gif':
                gif = GdkPixbuf.PixbufAnimation.new_from_file(self.publisher.localLogoImagePath).get_static_image()
                self.publisher_logo_image.set_from_pixbuf(gif.scale_simple(250, 250, 3))
            else:
                print(self.publisher.getImageCoverPath())
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename=self.publisher.getImageCoverPath(),
                    width=250,
                    height=250,
                    preserve_aspect_ratio=True)
                self.publisher_logo_image.set_from_pixbuf(pixbuf)


            # imagen = self.publisher.getImageCover()
            # self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            # self.labelImagen['image'] = self.cover


    def click_boton_buscar(self,widget):
        if self.search_entry.get_text()!='':
            self.comicVineSearcher.clearFilter()
            self.comicVineSearcher.addFilter("name:"+self.search_entry.get_text())
            self.comicVineSearcher.vineSearch(0)
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)

    def agregarEditorial(self):
        self.session.add(self.publisher)
        self.session.commit()

    def search_changed(self,widget):
        print('buscando')
        # if (self.entradaNombreEditorial.get()!=''):
        #     self.comicVineSearcher.clearFilter()
        #     self.comicVineSearcher.addFilter("name:"+self.entradaNombreEditorial.get())
        #     self.comicVineSearcher.vineSearch(0)
        #     self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)

    def click_boton_buscar_mas(self,widget):
        if (self.entradaNombreEditorial.get()!=''):
            self.comicVineSearcher.clearFilter()
            self.comicVineSearcher.addFilter("name:"+self.entradaNombreEditorial.get())
            self.comicVineSearcher.vineSearch(0)
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)

    def click_boton_aceptar(self,widget):
        if self.publisher:
            self.comicVineSearcher.clearFilter()
            self.comicVineSearcher.addFilter("name:"+self.entradaNombreEditorial.get())
            self.comicVineSearcher.vineSearch(0)
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)


    def itemClicked(self, event):
        if (self.grillaPublishers.selection()):
            seleccion = self.grillaPublishers.selection()
            self.publisher = self.comicVineSearcher.listaBusquedaVine[self.grillaPublishers.index(seleccion[0])]
            self.grillaPublishers.index(seleccion[0])
            imagen = self.publisher.getImageCover()
            self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            self.labelImagen['image'] = self.cover

    def cargarResultado(self,listaPublishers):
        self.listmodel_publishers.clear()
        for index,publisher in  enumerate(listaPublishers):
            self.listmodel_publishers.append([str(index), publisher.name])
        self.gtk_tree_view_publisher.set_model(self.listmodel_publishers)


if __name__ == '__main__':
    pub = Publisher_vine_search_gtk()
    pub.window.connect("destroy", Gtk.main_quit)
    pub.window.show_all()
    Gtk.main()

