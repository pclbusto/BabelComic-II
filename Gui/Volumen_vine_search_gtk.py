import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

from  Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
from PIL import Image, ImageTk
import Entidades.Init
from Entidades.Publishers.Publishers import Publishers
from Entidades.Publishers.Publisher import Publisher
from Gui.Publisher_lookup_gtk import Publisher_lookup_gtk
from Entidades.Volumes.ComicsInVolume import ComicInVolumes

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
        # self.gtk_tree_view_volumens = self.builder.get_object("gtk_tree_view_volumens")
        self.listmodel_volumenes = self.builder.get_object('listmodel_volumenes')
        self.label_status = self.builder.get_object("label_status")
        self.volumen_logo_image = self.builder.get_object("volumen_logo_image")
        self.spinner = self.builder.get_object("spinner")
        self.volume = None
        self.publisher = None

    def _copy_to_window(self,publisher):
        if publisher:
            self.entry_id_editorial.set_text(publisher.id_publisher)
            self.label_descripcion_editorial.set_text(publisher.name)
        else:
            self.label_descripcion_editorial.set_text('')

    def entry_id_editorial_change(self,widget):
        publisher = None
        publisher = self.publishers_manager.get(self.entry_id_editorial.get_text())
        self._copy_to_window(publisher)

    def click_lookup_editorial(self, widget):
        lookup = Publisher_lookup_gtk(self.session, self.entry_id_editorial)
        lookup.window.show()

    def click_buscar_mas_serie(self, widget):
        pass

    def click_buscar_serie(self, widget):
        self.offset = 0
        self.comicVineSearcher.clearFilter()
        self.comicVineSearcher.addFilter("name:" + self.entry_serie_nombre.get_text())
        self.comicVineSearcher.vineSearch(self.offset)
        self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)


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

    def int(self,t):
        if t[0].isdigit():
            return(int(t[0]))
        return 0

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        if col in['count_of_issues','start_year']:
            l.sort(reverse=reverse,key=self.int)
        else:
            l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        # reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def openLookupPublisher(self):
        window = Toplevel()
        self.publisher = Publisher()
        lk = PublisherLookupGui(window, self.publisher)
        lk.grid(sticky=(E, W, S, N))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.geometry("+0+0")
        window.wm_title(string="Editoriales")
        self.wait_window(window)
        self.publisher = lk.getPublisher()
        self.entradaNombreEditorial.insert(0,self.publisher.name)

    def buscarMas(self):
        self.comicVineSearcher.vineSearchMore()
        self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)


    def __buscar__(self):
        print("buscando....")
        if (self.entradaNombreVolume.get() != ''):
            print("BUSCANDO....")
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)
    def buscar(self):
        self.offset = 0
        self.comicVineSearcher.clearFilter()
        self.comicVineSearcher.addFilter("name:" + self.entradaNombreVolume.get())
        self.comicVineSearcher.vineSearch(self.offset)
        self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)
        # self.cargarResultado('')

    def seleccion(self, selection):
        (model, iter) = selection.get_selected()
        if iter:
            self.volumen = self.comicVineSearcher.listaBusquedaVine[int(model[iter][0])]
            self.spinner.start()
            self.volumen.localLogoImagePath = self.volumen.getImageCover()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=self.volumen.getImagePath(),
                width=250,
                height=250,
                preserve_aspect_ratio=True)
            self.volumen_logo_image.set_from_pixbuf(pixbuf)

    def cargarResultado(self,listavolumes):
        self.listmodel_volumenes.clear()
        for volume in listavolumes:
            if self.publisher is not None:
                if self.publisher.id_publisher==volume.publisherId:
                    self.listaFiltrada.append(volume)
            else:
                self.listaFiltrada.append(volume)
        for idx, volume in enumerate(self.listaFiltrada):
            anio = 0
            cantidad_numeros = 0

            if str.isdigit(volume.AnioInicio):
                anio = int(volume.AnioInicio)

            if str.isdigit(volume.cantidadNumeros):
                cantidad_numeros=int(volume.cantidadNumeros)

            self.listmodel_volumenes.append([str(idx),volume.nombre, cantidad_numeros,
                                            volume.publisher_name, anio])

        self.label_status.set_text("Cantidad Resultados: {} - Cantidad Resultados sin filtro: {}- Cantidad Total de Res"
                                   "ultados en ComicVine: {}".format(len(self.listaFiltrada),
                                                                     len(self.comicVineSearcher.listaBusquedaVine),
                                                                     self.comicVineSearcher.cantidadResultados))

if __name__ == "__main__":
    volumen = Volumen_vine_search_Gtk()
    volumen.window.show()
    volumen.window.connect("destroy", Gtk.main_quit)
    Gtk.main()

