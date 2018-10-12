import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
from gi.repository import GLib
import Entidades.Init
from Entidades.Publishers.Publishers import Publishers
from Entidades.Publishers.Publisher import Publisher
from Gui_gtk.Publisher_lookup_gtk import Publisher_lookup_gtk
from Entidades.Volumes.ComicsInVolume import ComicInVolumes
import threading
import time
class Volumen_vine_search_Gtk():
    def __init__(self, session=None):


        config = Config()

        self.listaFiltrada=[]
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session
        self.comicVineSearcher = ComicVineSearcher(config.getClave('volumes'),session=self.session)
        self.comicVineSearcher.setEntidad("volumes")
        self.publishers_manager = Publishers()

        self.handlers = {'click_lookup_editorial':self.click_lookup_editorial,
                         'click_buscar_serie':self.click_buscar_serie,
                         'click_buscar_mas_serie':self.click_buscar_mas_serie,
                         'click_aceptar':self.click_aceptar,
                         'entry_id_editorial_change':self.entry_id_editorial_change,
                         'seleccion':self.seleccion
                         }

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Volumen_vine_search_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volumen_vine_search_Gtk")
        self.entry_serie_nombre = self.builder.get_object("entry_serie_nombre")
        self.label_descripcion_editorial = self.builder.get_object("label_descripcion_editorial")
        self.entry_id_editorial = self.builder.get_object("entry_id_editorial")
        self.gtk_tree_view_volumens = self.builder.get_object("gtk_tree_view_volumens")
        self.listmodel_volumenes = self.builder.get_object('listmodel_volumenes')
        self.listmodel_volumenes.clear()

        self.label_status = self.builder.get_object("label_status")
        self.volumen_logo_image = self.builder.get_object("volumen_logo_image")
        self.spinner = self.builder.get_object("spinner")
        self.volume = None
        self.publisher = None
        self.cargarResultado(self.listmodel_volumenes)
        # self.entry_id_editorial.set_text('2707')
        # self.entry_serie_nombre.set_text('iron man')

    def _copy_to_window(self):
        if self.publisher:
            self.entry_id_editorial.set_text(self.publisher.id_publisher)
            self.label_descripcion_editorial.set_text(self.publisher.name)
        else:
            self.label_descripcion_editorial.set_text('')

    def entry_id_editorial_change(self,widget):
        self.publisher = None
        self.publisher = self.publishers_manager.get(self.entry_id_editorial.get_text())
        self._copy_to_window()
        if self.publisher is not None or self.entry_id_editorial.get_text()=='':
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)
        print("Publisher recueperado")

    def click_lookup_editorial(self, widget):
        lookup = Publisher_lookup_gtk(self.session, self.entry_id_editorial)
        lookup.window.show()


    def _buscarMas(self):
        self.comicVineSearcher.vineSearchMore()
        GLib.idle_add(self.cargarResultado,self.comicVineSearcher.listaBusquedaVine)
        # print(self.comicVineSearcher.listaBusquedaVine)

    def click_buscar_mas_serie(self, widget):
        self.spinner.start()
        for i in range(self.comicVineSearcher.cantidadPaginas-4):
            print("buscando mas")
            self.hilo1 = threading.Thread(target=self._buscarMas)
            self.hilo1.start()
            time.sleep(1)

    def _buscar(self):
        self.offset = 0
        self.comicVineSearcher.clearFilter()
        self.comicVineSearcher.addFilter("name:" + self.entry_serie_nombre.get_text())
        self.comicVineSearcher.vine_Search_all()
        GLib.idle_add(self.cargarResultado, self.comicVineSearcher.listaBusquedaVine)



    def click_buscar_serie(self, widget):
        self.spinner.start()
        self.listmodel_volumenes.clear()
        self.hilo1 = threading.Thread(target=self._buscar)
        self.hilo1.start()
        # GLib.idle_add(self._buscar)

    def click_aceptar(self, widget):
        cnf = Config(self.session)
        cv = ComicVineSearcher(cnf.getClave('volume'), self.session)
        cv.entidad = 'volume'
        volumenAndIssues = cv.getVineEntity(self.volumen.id)

        self.session.query(ComicInVolumes).filter(ComicInVolumes.volumeId == self.volumen.id).delete()
        for index, numeroComic in enumerate(volumenAndIssues[1], start=0):
            numeroComic.offset = int(index / 100)
            self.session.add(numeroComic)

        self.session.add(volumenAndIssues[0])
        self.session.commit()


    def _seleccion(self):
        self.volumen.localLogoImagePath = self.volumen.getImageCover()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=self.volumen.getImagePath(),
            width=250,
            height=250,
            preserve_aspect_ratio=True)
        self.spinner.stop()
        GLib.idle_add(self.volumen_logo_image.set_from_pixbuf, pixbuf)
        # self.volumen_logo_image.set_from_pixbuf(pixbuf)

    def seleccion(self, selection):
        self.spinner.start()
        (model, iter) = selection.get_selected()
        if iter:
            self.volumen = self.listaFiltrada[int(model[iter][0])]
            self.hilo1 = threading.Thread(target=self._seleccion)
            self.hilo1.start()

    def cargarResultado(self,listavolumes):



        self.listmodel_volumenes.clear()
        self.listaFiltrada.clear()
        for volume in listavolumes:
            if self.publisher is not None:
                print("Editorial de filtor: {} Editorial Comics: {}".format(self.publisher.id_publisher,volume.publisherId))
                if self.publisher.id_publisher==volume.publisherId:
                    self.listaFiltrada.append(volume)
            else:
                self.listaFiltrada.append(volume)

        if len(self.listaFiltrada) > 1400:
            self.label_status.set_text("La cantidad de registros es mayor a 1400. Trate de filtrar la consulta.")
            return


        for idx, volume in enumerate(self.listaFiltrada):
            nombre = ''
            cantidad_numeros = 0
            anio = 0
            publisher_name=""
            if volume.nombre is not None:
                nombre = volume.nombre
            if volume.AnioInicio is not None:
                if str.isdigit(volume.AnioInicio):
                    anio = int(volume.AnioInicio)

            if str.isdigit(volume.cantidadNumeros):
                cantidad_numeros=int(volume.cantidadNumeros)

            if volume.publisher_name is not None:
                publisher_name = volume.publisher_name
            print("cargand el volumen {}".format(str(idx) + " " +nombre))
            self.listmodel_volumenes.append([str(idx),nombre, cantidad_numeros,
                                             publisher_name, anio])

        self.label_status.set_text("Cantidad Resultados: {} - Cantidad Resultados sin filtro: {}- Cantidad Total de Res"
                                   "ultados en ComicVine: {}".format(len(self.listaFiltrada),
                                                                     len(self.comicVineSearcher.listaBusquedaVine),
                                                                     self.comicVineSearcher.cantidadResultados))
        self.spinner.stop()

if __name__ == "__main__":
    volumen = Volumen_vine_search_Gtk()
    volumen.window.show()
    volumen.window.connect("destroy", Gtk.main_quit)
    Gtk.main()

