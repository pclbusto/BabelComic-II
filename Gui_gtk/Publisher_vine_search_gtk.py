from  Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
import Entidades.Init
from gi.repository import GLib
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import asyncio

class Publisher_vine_search_gtk():
    # todo implementar icono de progreso
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
        self.window = self.builder.get_object("Publisher_vine_search_Gtk")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.entry_nombre = self.builder.get_object('entry_nombre')
        self.spinner = self.builder.get_object('spinner')
        self.publisher_logo_image = self.builder.get_object('publisher_logo_image')
        self.listmodel_publishers = Gtk.ListStore(str, str)
        self.gtk_tree_view_publisher =  self.builder.get_object('gtk_tree_view_publisher')



    def selection(self,selection):
        (model, iter) = selection.get_selected()
        if iter:
            self.publisher = self.comicVineSearcher.listaBusquedaVine[int(model[iter][0])]
            self.spinner.start()
            self.publisher.getImageCover()
            self.spinner.stop()
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


    def _start(self):
        print("iniciando")


    def _buscar(self):
        if self.entry_nombre.get_text()!='':
            self.comicVineSearcher.clearFilter()
            self.comicVineSearcher.addFilter("name:"+self.entry_nombre.get_text())
            self.comicVineSearcher.vineSearch(0)
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)
        self.spinner.stop()

    def start(self):
        GLib.idle_add(self.spinner.start)

    def click_boton_buscar(self,widget):

        t = threading.Thread(target=self.start)
        t.run()
        # GLib.idle_add(self._start)
        # GLib.idle_add(self._buscar)


    def agregarEditorial(self):
        # self.session.add(self.publisher)
        # self.session.commit()
        self._stop()

    def search_changed(self,widget):
        print('buscando')
        # if (self.entradaNombreEditorial.get()!=''):
        #     self.comicVineSearcher.clearFilter()
        #     self.comicVineSearcher.addFilter("name:"+self.entradaNombreEditorial.get())
        #     self.comicVineSearcher.vineSearch(0)
        #     self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)

    def click_boton_buscar_mas(self,widget):
        self._start()
        #
        # if (self.entradaNombreEditorial.get()!=''):
        #     self.comicVineSearcher.clearFilter()
        #     self.comicVineSearcher.addFilter("name:"+self.entradaNombreEditorial.get())
        #     self.comicVineSearcher.vineSearch(0)
        #     self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)

    def click_boton_aceptar(self,widget):

        if self.publisher:
            self.session.add(self.publisher)
            self.session.commit()
        # self.window.close()

    def cargarResultado(self,listaPublishers):
        self.listmodel_publishers.clear()
        for index,publisher in  enumerate(listaPublishers):
            self.listmodel_publishers.append([str(index), publisher.name])
        self.gtk_tree_view_publisher.set_model(self.listmodel_publishers)


if __name__ == '__main__':
    volumen_vine_search = Publisher_vine_search_gtk()
    volumen_vine_search.window.connect("destroy", Gtk.main_quit)
    volumen_vine_search.window.show()
    Gtk.main()

