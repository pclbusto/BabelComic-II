import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
from gi.repository import GLib
import Entidades.Init
from Entidades.Entitiy_managers import Publishers
from Gui_gtk.Publisher_lookup_gtk import Publisher_lookup_gtk
from Entidades.Agrupado_Entidades import Comics_In_Volume, Comicbook_Info, Volume
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
        self.volume_logo_image = self.builder.get_object("volumen_logo_image")
        self.spinner = self.builder.get_object("spinner")
        self.volume = None
        self.publisher = None
        self.cargarResultado(self.listmodel_volumenes)
        # self.entry_id_editorial.set_text('2707')
        # self.entry_serie_nombre.set_text('iron man')

    def _copy_to_window(self):
        if self.publisher:
            self.entry_id_editorial.set_text(str(self.publisher.id_publisher))
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
        print(self.publisher)

    def click_lookup_editorial(self, widget):
        lookup = Publisher_lookup_gtk(self.session, self.return_lookup_editorial)
        lookup.window.show()

    def return_lookup_editorial(self, id_publisher):
        if id_publisher is not None:
            self.publisher = None
            self.publisher = self.publishers_manager.get(id_publisher)
            self._copy_to_window()
            if self.publisher is not None or self.entry_id_editorial.get_text() == '':
                self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)
        print("Publisher recueperado")

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

    def cargar_mensaje_status(self, mensaje):
        self.label_status.set_text(mensaje)

    def hilo_cargar_volume(self, id_volume_externo):
        cnf = Config(self.session)
        cv = ComicVineSearcher(cnf.getClave('volume'), self.session)
        cv.entidad = 'volume'
        volumenAndIssues = cv.getVineEntity(id_volume_externo)
        # volumenAndIssues = cv.getVineEntity(106705)
        while cv.porcentaje_procesado!=100:
            time.sleep(2)
            GLib.idle_add(self.cargar_mensaje_status, "Porcentaje completado {}%".format(cv.porcentaje_procesado))
        volume = volumenAndIssues[0]
        volumen_in_db = self.session.query(Volume).filter(Volume.id_volume == volume.id_volume).first()
        if volumen_in_db:
            # actualizo la cantidad de ejemplares nada mas
            volumen_in_db.cantidadNumeros = volume.cantidadNumeros
            volume = volumen_in_db
        self.session.add(volume)
        self.session.commit()
        print(volume)
        self.session.query(Comics_In_Volume).filter(Comics_In_Volume.id_volume == volume.id_volume).delete()
        self.session.commit()
        # for index, numeroComic in enumerate(volumenAndIssues[1], start=0):
        #     print(numeroComic)
        #     self.session.add(numeroComic)
        # self.session.commit()
        # limpiamos los comics info del volumen
        self.session.query(Comicbook_Info).filter(Comicbook_Info.id_volume == volume.id_volume).delete()
        self.session.commit()
        for comicbook_info in cv.lista_comicbooks_info:
            comicbook_info.id_volume = volume.id_volume
            comicbook_info.nombre_volumen = volume.nombre
            self.session.add(comicbook_info)
        self.session.commit()

    def click_aceptar(self, widget):
        # threading.Thread(target=self.hilo_cargar_volume, args=[self.volume.id_volume_externo]).start()
    #     86343
        threading.Thread(target=self.hilo_cargar_volume, args=['106705']).start()

    def _seleccion(self):
        self.volume.localLogoImagePath = self.volume.getImageCover()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=self.volume.getImagePath(),
            width=250,
            height=250,
            preserve_aspect_ratio=True)
        self.spinner.stop()
        GLib.idle_add(self.volume_logo_image.set_from_pixbuf, pixbuf)
        # self.volume_logo_image.set_from_pixbuf(pixbuf)

    def seleccion(self, selection):
        self.spinner.start()
        (model, iter) = selection.get_selected()
        if iter:
            self.volume = self.listaFiltrada[int(model[iter][0])]
            self.hilo1 = threading.Thread(target=self._seleccion)
            self.hilo1.start()

    def cargarResultado(self,listavolumes):
        self.listmodel_volumenes.clear()
        self.listaFiltrada.clear()
        for volume in listavolumes:
            if self.publisher is not None:
                print("Editorial de fitro: {} Editorial Comics: {}".format(self.publisher.id_publisher_externo,volume.id_publisher_externo))
                if self.publisher.id_publisher_externo==volume.id_publisher_externo:
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
    from Entidades.Agrupado_Entidades import Arco_Argumental,Arcos_Argumentales_Comics_Reference,Volume
    from Entidades.Agrupado_Entidades import Comicbook_Info_Cover_Url, Comicbook_Info

    volumen = Volumen_vine_search_Gtk()
    volumen.window.show()
    volumen.window.connect("destroy", Gtk.main_quit)
    volumen.session.query(Arcos_Argumentales_Comics_Reference).delete()
    volumen.session.query(Arco_Argumental).delete()
    volumen.session.query(Volume).delete()
    volumen.session.query(Comicbook_Info_Cover_Url).delete()
    volumen.session.query(Comicbook_Info).delete()
    volumen.session.commit()
    volumen.click_aceptar(None)
    Gtk.main()

