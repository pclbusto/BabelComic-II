import os
import Entidades.Init
from Entidades.Entitiy_managers import Comicbooks_Info, Volumens, ArcosArgumentales
# from Entidades.Agrupado_Entidades import  Comicbook_Info
from Gui_gtk import Publisher_lookup_gtk
from Gui_gtk.Publisher_vine_search_gtk import Publisher_vine_search_gtk
import datetime
import  threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

class Comicbook_Info_Gtk():
    # todo implementar los botones de limpiar, guardar y borrar

    def __init__(self,  session=None,):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.comicbooks_manager = Comicbooks_Info(session=self.session)
        self.arcs_manager = ArcosArgumentales(session=self.session)
        self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext,
                         'getLast': self.getLast, 'seleccion_fecha': self.seleccion_fecha,
                         'boton_guardar': self.boton_guardar, 'click_limpiar':self.click_limpiar,
                         'click_cargar_desde_web': self.click_cargar_desde_web, 'combobox_change':self.combobox_change,
                         'menu_desplegado':self.menu_desplegado,'click_eliminar':self.click_eliminar,
                         'click_cover_anterior': self.click_cover_anterior,
                         'click_cover_siguiente': self.click_cover_siguiente,
                         'change_cover': self.change_cover}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Comicbook_info_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comicbook_info_gtk")
        self.linkbutton_volume = self.builder.get_object("linkbutton_volume")
        self.linkbutton_volume.set_label("Volumen")
        self.popover = self.builder.get_object("popover")

        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.label_nombre_volumen = self.builder.get_object("label_nombre_volumen")
        self.entry_orden = self.builder.get_object("entry_orden")
        self.entry_numero = self.builder.get_object("entry_numero")
        self.entry_titulo = self.builder.get_object("entry_titulo")
        self.label_fecha_tapa = self.builder.get_object("label_fecha_tapa")
        self.btn_link_api_url = self.builder.get_object("btn_link_api_url")
        self.btn_link_url = self.builder.get_object("btn_link_url")
        self.scale_raiting = self.builder.get_object("scale_raiting")
        self.text_resumen = self.builder.get_object("text_resumen")
        self.textbuffer = self.text_resumen.get_buffer()
        self.calendario = self.builder.get_object("calendario")
        self.cover_comic = self.builder.get_object("cover_comic")
        self.combo_paginas = self.builder.get_object("combo_paginas")
        self.liststore_covers = self.builder.get_object("liststore_covers")
        self.liststore_arcos_argumentales = self.builder.get_object("liststore_arcos_argumentales")
        self.spinner = Gtk.Spinner()
        self.box_cover = self.builder.get_object("box_cover")

        print("Creacion de formulario exitosa")
        # inicializamos el modelo con rotulos del manager

    def change_cover(self, widget):
        print("change_cover")
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:
            model = widget.get_model()
            index = widget.get_active()
            print("change_cover INDEX {}".format(widget.get_active()))
            self.comicbooks_manager.index_lista_covers = index
            self._load_cover()
        else:
            entry = widget.get_child()
            # print("Entered: %s" % entry.get_text())

    def click_eliminar(self,widget):
        print(datetime.date.fromordinal(self.comicbooks_manager.entidad.fecha_tapa).day)
        self.calendario.select_day(datetime.date.fromordinal(self.comicbooks_manager.entidad.fecha_tapa).day)
        self.calendario.month = datetime.date.fromordinal(self.comicbooks_manager.entidad.fecha_tapa).month + 1
        self.calendario.year = datetime.date.fromordinal(self.comicbooks_manager.entidad.fecha_tapa).year

    def menu_desplegado(self, widget):
        print(datetime.date.fromordinal(self.comicbooks_manager.entidad.fecha_tapa).day)
        self.calendario.select_day(datetime.date.fromordinal(self.comicbooks_manager.entidad.fecha_tapa).day)
        self.calendario.select_month(datetime.date.fromordinal(self.comicbooks_manager.entidad.fecha_tapa).month-1,
                                     datetime.date.fromordinal(self.comicbooks_manager.entidad.fecha_tapa).year)

    def set_volume(self, id_volume):
        self.comicbooks_manager.set_volume(id_volume=id_volume)
        volume_mamange = Volumens(session = self.session)
        volume = volume_mamange.get(id_volume)
        self.label_nombre_volumen.set_text(volume.nombre)

    def set_comicbook(self, id):
        #todo validar volumn seteado
        self.comicbooks_manager.get(id)
        print("Cargamos el voumen {}".format(id))
        self._copy_to_window(self.comicbooks_manager.entidad)

    def seleccion_fecha(self, widget):
        print(widget.get_date().year)
        self.label_fecha_tapa.set_text(datetime.date(year=widget.get_date().year, month=widget.get_date().month+1, day=widget.get_date().day).strftime("%d/%m/%Y"))
        self.comicbooks_manager.entidad.fecha_tapa = datetime.date(year=widget.get_date().year, month=widget.get_date().month+1, day=widget.get_date().day).toordinal()
        self.popover.popdown()

    def click_cover_anterior(self, widget):
        self.comicbooks_manager.get_prev_cover_complete_path()
        self.combo_paginas.set_active(self.comicbooks_manager.index_lista_covers)

    def click_cover_siguiente(self, widget):
        self.comicbooks_manager.get_next_cover_complete_path()
        # self.comicbooks_manager.index_lista_covers
        self.combo_paginas.set_active(self.comicbooks_manager.index_lista_covers)

    def combobox_change(self, widget):
        if widget.get_active_iter() is not None:
            self.publishers_manager.set_order(self.publishers_manager.lista_opciones[widget.get_model()[widget.get_active_iter()][0]])

    def boton_guardar(self,widget):
        self.copy_from_window_to_entity()
        self.comicbooks_manager.save()

    def click_cargar_desde_web(self, widget):
        publisher_vine_search = Publisher_vine_search_gtk(self.session)
        publisher_vine_search.window.show()

    def id_changed(self,widget, test):
        if self.entry_id.get_text()!='':
            publisher = self.publishers_manager.get(self.entry_id.get_text())
            self._copy_to_window(publisher)

    def return_lookup(self, id_publisher):
        if id_publisher  !='':
            self.entry_id.set_text(str(id_publisher))
            publisher = self.publishers_manager.get(self.entry_id.get_text())
            self._copy_to_window(publisher)

    def open_lookup(self, widget):
        lookup = Publisher_lookup_gtk.Publisher_lookup_gtk(self.session, self.return_lookup)
        lookup.window.show()

    def getFirst(self, widget):
        comicbook_info = self.comicbooks_manager.getFirst()
        self._copy_to_window(comicbook_info)

    def getPrev(self, widget):
        comicbook_info = self.comicbooks_manager.getPrev()
        self._copy_to_window(comicbook_info)

    def getNext(self, widget):
        comicbook_info = self.comicbooks_manager.getNext()
        self._copy_to_window(comicbook_info)

    def getLast(self, widget):
        publisher = self.comicbooks_manager.getLast()
        self._copy_to_window(publisher)

    def _copy_to_window(self, comicbook_info):
        print(comicbook_info)
        #self.clearWindow()
        if comicbook_info is not None:
            self.entry_orden.set_text(str(comicbook_info.orden))
            self.entry_numero.set_text(str(comicbook_info.numero))
            self.entry_titulo.set_text(comicbook_info.titulo)
            if comicbook_info.fecha_tapa > 0:
                self.label_fecha_tapa.set_text(datetime.date.fromordinal(comicbook_info.fecha_tapa).strftime("%d/%m/%Y"))
            else:
                self.label_fecha_tapa.set_text(
                    datetime.date.fromordinal(1).strftime("%d/%m/%Y"))
            self.btn_link_api_url.set_uri(comicbook_info.api_detail_url)
            self.btn_link_url.set_uri(comicbook_info.url)
            self.scale_raiting.get_adjustment().set_value(comicbook_info.rating)
            self.textbuffer.set_text(comicbook_info.resumen)
            print("self.comicbooks_manager.index_lista_covers {}".format(self.comicbooks_manager.index_lista_covers))
            self.combo_paginas.set_active(self.comicbooks_manager.index_lista_covers)
            self._load_cover()
            listore = Gtk.ListStore(int)
            self.liststore_covers.clear()
            for index, cover_nro in enumerate(self.comicbooks_manager.lista_covers):
                listore.append([index])
                self.liststore_covers.append([index, cover_nro.thumb_url])
            self.combo_paginas.set_model(listore)
            self.liststore_arcos_argumentales.clear()
            for arco in self.comicbooks_manager.lista_arcs:
                arco = self.arcs_manager.get(arco.id_arco_argumental)
                print("ARCO {}:".format(arco.nombre))
                self.liststore_arcos_argumentales.append([arco.id_arco_argumental, arco.nombre])
            # self.liststore_covers

    def _load_cover_background(self):
        # print("YA EN EL HILO")

        nombreThumnail = self.comicbooks_manager._get_cover_complete_path(self.update_cover_image_call_back)
        if (os.path.isfile(nombreThumnail)):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=nombreThumnail,
                width=150,
                height=250,
                preserve_aspect_ratio=True)
            self.box_cover.remove(self.cover_comic)
            self.box_cover.remove(self.spinner)
            self.box_cover.add(self.cover_comic)  # , 1, 0, 1, 1)
            self.cover_comic.set_from_pixbuf(pixbuf)
        else:
            self.box_cover.remove(self.cover_comic)
            self.box_cover.remove(self.spinner)
            self.box_cover.add(self.spinner)  # , 1, 0, 1, 1)
            self.spinner.start()
        GLib.idle_add(self.window.show_all)

    def update_cover_image_call_back(self, nombre_thumnail):
        if (os.path.isfile(nombre_thumnail)):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=nombre_thumnail,
                width=150,
                height=250,
                preserve_aspect_ratio=True)
            self.box_cover.remove(self.cover_comic)
            self.box_cover.remove(self.spinner)
            self.box_cover.add(self.cover_comic)  # , 1, 0, 1, 1)
            self.cover_comic.set_from_pixbuf(pixbuf)

    def _load_cover(self):
        print("INICIANDO THREAD")

        # threading.Thread(target=self._load_cover_background).start()
        self._load_cover_background()

    def copy_from_window_to_entity(self):
        self.comicbooks_manager.entidad.orden = self.entry_orden.get_text()
        self.comicbooks_manager.entidad.numero = self.entry_numero.get_text()
        self.comicbooks_manager.entidad.titulo = self.entry_titulo.get_text()
        # este campo lo tenemos actualizaco cada vez que se selecciona un valor de calendario
        # self.comicbooks_manager.entidad.fecha_tapa
        self.comicbooks_manager.entidad.rating = self.scale_raiting.get_adjustment().get_value()
        #self.volumens_manager.entidad.image_url = self.entry_url_cover.get_text()
        #self.volumens_manager.entidad.anio_inicio = self.entry_anio_inicio.get_text()
        #self.volumens_manager.entidad.cantidad_numeros = self.entry_cantidad_numeros.get_text()

    def click_limpiar(self, widget):
        print("dsldsa")
        self.entry_url.clear()
        # self.entradaNombre.delete(0, END)
        # self.entradaUrl.delete(0, END)
        # self.textoDescripcion.config(text='')


if __name__ == "__main__":

    cbi = Comicbook_Info_Gtk()
    cbi.set_volume('42721')
    cbi.set_comicbook(340148)
    cbi.window.show_all()
    cbi.window.connect("destroy", Gtk.main_quit)
    Gtk.main()