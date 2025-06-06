import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf, Gdk
from Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
from gi.repository import GLib
import Entidades.Init
from Entidades.Entitiy_managers import Publishers, Comicbooks_Info
from Gui_gtk.Publisher_lookup_gtk import Publisher_lookup_gtk
from Entidades.Agrupado_Entidades import Comicbook_Info, Volume, Arcos_Argumentales_Comics_Reference, Arco_Argumental
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

        self.comic_vine_searcher = ComicVineSearcher(config.getClave('volumes'), session=self.session)
        self.comic_vine_searcher.setEntidad("volumes")
        self.publishers_manager = Publishers()

        self.handlers = {'click_lookup_editorial': self.click_lookup_editorial,
                         'click_buscar_serie': self.click_buscar_serie,
                         # 'click_buscar_mas_serie': self.click_buscar_mas_serie,
                         'click_aceptar': self.click_aceptar,
                         'entry_id_editorial_change': self.entry_id_editorial_change,
                         'seleccion': self.seleccion,
                         'click_detener': self.click_detener,
                         'intro_detection': self.intro_detection,
                         'tecla_presionada': self.tecla_presionada
                         }

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Volumen_vine_search_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volumen_vine_search_Gtk")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
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

    def intro_detection(self,  widget, event):
        if event.keyval == Gdk.KEY_Return :
            self.click_buscar_serie(None)

    def tecla_presionada(self, widget, args):
        if args.keyval == Gdk.KEY_Escape:
            self.window.close()

    def click_detener(self, widget):
        self.comic_vine_searcher.detener = True
        for hilo in self.comic_vine_searcher.lista_hilos_ejecucion.items():
            print(hilo)
            hilo[1].join(1)
            self.comic_vine_searcher.lock.acquire(True)
            self.comic_vine_searcher.cantidad_hilos -= 1
            self.comic_vine_searcher.lock.release()


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
            self.cargarResultado(self.comic_vine_searcher.listaBusquedaVine)
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
                self.cargarResultado(self.comic_vine_searcher.listaBusquedaVine)
        print("Publisher recueperado")

    def _buscarMas(self):
        self.comic_vine_searcher.vineSearchMore()
        GLib.idle_add(self.cargarResultado,self.comic_vine_searcher.listaBusquedaVine)
        # print(self.comic_vine_searcher.listaBusquedaVine)

    # def click_buscar_mas_serie(self, widget):
    #
    #     self.spinner.start()
    #     for i in range(self.comic_vine_searcher.cantidadPaginas-4):
    #         print("buscando mas")
    #         self.hilo1 = threading.Thread(target=self._buscarMas)
    #         self.hilo1.start()
    #         time.sleep(1)

    def _buscar(self):
        self.offset = 0
        self.comic_vine_searcher.clearFilter()
        self.comic_vine_searcher.setEntidad("volumes")
        lista_palabras = '+'.join(str(palabra) for palabra in self.entry_serie_nombre.get_text().split(' '))
        self.comic_vine_searcher.addFilter("name:" + lista_palabras)
        self.comic_vine_searcher.vine_Search_all()
        GLib.idle_add(self.cargarResultado, self.comic_vine_searcher.listaBusquedaVine)

    def click_buscar_serie(self, widget):
        self.spinner.start()
        self.listmodel_volumenes.clear()
        self.hilo1 = threading.Thread(target=self._buscar)
        self.hilo1.start()

    def cargar_mensaje_status(self, mensaje):
        self.label_status.set_text(mensaje)

    def hilo_cargar_volume(self, id_volume_externo):

        self.comic_vine_searcher.entidad = 'volume'
        volumen = self.comic_vine_searcher.getVineEntity(id_volume_externo)
        # recuperamos los isseues del volumen estan en una lista de comic_vine_searcher
        self.comic_vine_searcher.cargar_comicbook_info(volumen)
        while self.comic_vine_searcher.porcentaje_procesado != 100 and not self.comic_vine_searcher.detener:
            time.sleep(2)
            GLib.idle_add(self.cargar_mensaje_status, "Porcentaje completado {}%".format(self.comic_vine_searcher.porcentaje_procesado))
        if self.comic_vine_searcher.detener:
            GLib.idle_add(self.cargar_mensaje_status, "Proceso de descarga detenido")
            print("Proceso de descarga detenido")
            return
        self.comic_vine_searcher.insert_update_volumen(volumen)

        # cambio de lugar de funcionalidad. ahora lo hace el searcher
        # volumen_in_db = self.session.query(Volume).filter(Volume.id_volume == volumen.id_volume).first()
        # if volumen_in_db is not None:
        #     # actualizo la cantidad de ejemplares nada mas
        #     print(volumen)
        #     volumen_in_db.actualizar_con(volumen)
        #     volumen = volumen_in_db
        # self.session.add(volumen)
        # self.session.commit()
        # #print(volumen)
        # for comicbook_info in self.comic_vine_searcher.lista_comicbooks_info:
        #     cbi_db = self.session.query(Entidades.Agrupado_Entidades.Comicbook_Info).get(comicbook_info.id_comicbook_info)
        #     if cbi_db is not None and not cbi_db.actualizado_externamente:
        #         self.session.query(Comicbook_Info).filter(Comicbook_Info.id_comicbook_info == comicbook_info.id_comicbook_info).delete()
        #         self.session.commit()
        #         self.session.add(comicbook_info)
        #     elif cbi_db is not None  and cbi_db.actualizado_externamente:
        #         print("Actualizando info de comicbook_info DATOS A ACTUALIZAR")
        #         cbi_db.numero = comicbook_info.numero
        #         cbi_db.fecha_tapa = comicbook_info.fecha_tapa
        #         cbi_db.orden = comicbook_info.orden
        #         cbi_db.url = comicbook_info.url
        #         cbi_db.api_detail_url = comicbook_info.api_detail_url
        #
        #         for url_cover in comicbook_info.thumbs_url:
        #             copiar_cover = True;
        #             for url_cover_cbi in cbi_db.thumbs_url:
        #                 if url_cover.thumb_url == url_cover_cbi.thumb_url:
        #                     copiar_cover = False
        #                     break;
        #
        #             if copiar_cover:
        #                 cbi_db.thumbs_url.append(url_cover)
        #
        #
        #             # cbi_db.thumbs_url = comicbook_info.thumbs_url
        #         print(cbi_db)
        #     else:
        #         print("agregando comic por primera vez")
        #         print(cbi_db)
        #         self.session.add(comicbook_info)
        #     self.session.commit()
        # lista_arcos = []
        # for arco in self.comic_vine_searcher.lista_arcos:
        #     arco_db = self.session.query(Arco_Argumental).filter(Arco_Argumental.id_arco_argumental==arco.id_arco_argumental).first()
        #     if arco_db is not None:
        #         lista_arcos.append(arco_db)
        #         arco_db.lista_ids_comicbook_info_para_procesar = arco.lista_ids_comicbook_info_para_procesar
        #     else:
        #         self.session.add(arco)
        #         lista_arcos.append(arco)
        # self.session.commit()
        # # reemplazo todos los arcos por los que estan la base o los que acabo de guardar
        # self.comic_vine_searcher.lista_arcos = lista_arcos
        # # construimos la relacion para cada arco con la lista de comics.
        # for arco in self.comic_vine_searcher.lista_arcos:
        #     try:
        #         print("Lista de arcos de cv {}".format(arco.lista_ids_comicbook_info_para_procesar))
        #     except Exception:
        #         print("Arco con error {}".format(arco))
        #         raise
        #     for comicbook_info in self.comic_vine_searcher.lista_comicbooks_info:
        #         for pos, arco_comicbook_info in enumerate(arco.lista_ids_comicbook_info_para_procesar):
        #             # print("Comic Info {} tipo {} comic info arco {} tipo {}".format(comicbook_info.id_comicbook_info,
        #             #                                                                 type(comicbook_info.id_comicbook_info),
        #             #                                                                 arco_comicbook_info,
        #             #                                                                 type(arco_comicbook_info)))
        #             if int(comicbook_info.id_comicbook_info) == arco_comicbook_info:
        #                 comicbook_info_db = self.session.query(Comicbook_Info).get(comicbook_info.id_comicbook_info)
        #                 rel = self.session.query(Arcos_Argumentales_Comics_Reference).get((comicbook_info.id_comicbook_info, arco.id_arco_argumental))
        #                 if rel is None:
        #                     print("El comic book_info {} pertenece al arco {}".format(comicbook_info.id_comicbook_info, arco.id_arco_argumental))
        #                     arco_argumental_comicsbook_reference = Arcos_Argumentales_Comics_Reference()
        #                     arco_argumental_comicsbook_reference.orden = pos
        #                     arco_argumental_comicsbook_reference.ids_arco_argumental=arco
        #                     print("COMIC A RELACIONAR")
        #                     print(type(comicbook_info))
        #                     print(type(comicbook_info_db))
        #                     if comicbook_info_db is not None:
        #                         arco_argumental_comicsbook_reference.ids_comicbooks_info=comicbook_info_db
        #                     else:
        #                         arco_argumental_comicsbook_reference.ids_comicbooks_info=comicbook_info
        #                     self.session.add(arco_argumental_comicsbook_reference)
        #                     self.session.commit()
        #
        # # Descargamos los covers de los issues del volumen
        # for comicbook_info in self.comic_vine_searcher.lista_comicbooks_info:
        #     print('Bajando covers {}'.format(comicbook_info.id_comicbook_info))
        #     # comicbook_info.get_first_cover_complete_path()
        #     comicbooks_info_manager = Comicbooks_Info(session=self.session)
        #     comicbooks_info_manager.get(comicbook_info.id_comicbook_info)
        #     print(comicbooks_info_manager.get)
        #     threading.Thread(target=comicbooks_info_manager.get_first_cover_complete_path).start()

    def click_aceptar(self, widget):
        self.comic_vine_searcher.detener = False
        threading.Thread(target=self.hilo_cargar_volume, args=[self.volume.id_volume]).start()

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
        GLib.idle_add(self.cargar_mensaje_status, "")
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
                print("Editorial de fitro: {} Editorial Comics: {}".format(self.publisher.id_publisher,volume.id_publisher))
                if self.publisher.id_publisher==volume.id_publisher:
                    self.listaFiltrada.append(volume)
            else:
                self.listaFiltrada.append(volume)
        print("Longitud: {}".format(len(self.listaFiltrada)))
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
            if volume.anio_inicio is not None:
                if str.isdigit(volume.anio_inicio):
                    anio = int(volume.anio_inicio)

            if str.isdigit(volume.cantidad_numeros):
                cantidad_numeros=int(volume.cantidad_numeros)

            if volume.publisher_name is not None:
                publisher_name = volume.publisher_name
            print("cargand el volumen {}".format(str(idx) + " " +nombre))
            self.listmodel_volumenes.append([str(idx),nombre, cantidad_numeros,
                                             publisher_name, anio])

        self.label_status.set_text("Cantidad Resultados: {} - Cantidad Resultados sin filtro: {}- Cantidad Total de Res"
                                   "ultados en ComicVine: {}".format(len(self.listaFiltrada),
                                                                     len(self.comic_vine_searcher.listaBusquedaVine),
                                                                     self.comic_vine_searcher.cantidadResultados))
        self.spinner.stop()

if __name__ == "__main__":
    # from Entidades.Agrupado_Entidades import Arco_Argumental,Arcos_Argumentales_Comics_Reference,Volume
    # from Entidades.Agrupado_Entidades import Comicbook_Info_Cover_Url, Comicbook_Info
    #


    volumen = Volumen_vine_search_Gtk()
    volumen.window.show()
    volumen.entry_serie_nombre.set_text("uncanny avengers")
    volumen.window.connect("destroy", Gtk.main_quit)
    Gtk.main()


    # volumen.session.query(Arcos_Argumentales_Comics_Reference).delete()
    # volumen.session.query(Arco_Argumental).delete()
    # volumen.session.query(Volume).delete()
    # volumen.session.query(Comicbook_Info_Cover_Url).delete()
    # volumen.session.query(Comicbook_Info).delete()
    # volumen.session.query(Entidades.Agrupado_Entidades.Arcos_Argumentales_Comics_Reference).delete()
    # volumen.session.query(Entidades.Agrupado_Entidades.Arco_Argumental).delete()
    # volumen.session.query(Entidades.Agrupado_Entidades.Volume).delete()
    # volumen.session.query(Entidades.Agrupado_Entidades.Comics_In_Volume).delete()
    # volumen.session.query(Entidades.Agrupado_Entidades.Comicbook_Info).delete()
    # volumen.session.commit()
    # volumen.click_aceptar(None)
    # volumen.click_aceptar2(None)
    cadena = 'Adventures of superman'
    print('+'.join(str(palabra) for palabra in cadena.split(' ')))


