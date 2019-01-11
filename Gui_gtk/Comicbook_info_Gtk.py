import os
import Entidades.Init
from Entidades.Entitiy_managers import Comicbooks_Info, Volumens
from Entidades.Agrupado_Entidades import  Comicbook_Info
from Gui_gtk import Publisher_lookup_gtk
from Gui_gtk.Publisher_vine_search_gtk import Publisher_vine_search_gtk
import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class Comicbook_Info_Gtk():
    # todo implementar los botones de limpiar, guardar y borrar

    def __init__(self,  session=None,):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.comicbooks_manager = Comicbooks_Info(session=self.session)

        self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext,
                         'getLast': self.getLast, 'seleccion_fecha': self.seleccion_fecha,
                         'boton_guardar': self.boton_guardar, 'click_limpiar':self.click_limpiar,
                         'click_cargar_desde_web': self.click_cargar_desde_web, 'combobox_change':self.combobox_change}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Comicbook_info_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comicbook_info_gtk")
        self.linkbutton_volume = self.builder.get_object("linkbutton_volume")
        self.linkbutton_volume.set_label("Volumen")
        self.popover = self.builder.get_object("popover")

        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.label_nombre_volumen = self.builder.get_object("label_nombre_volumen")
        self.entry_orden= self.builder.get_object("entry_orden")
        self.entry_numero= self.builder.get_object("entry_numero")
        self.entry_titulo= self.builder.get_object("entry_titulo")
        self.label_fecha_tapa = self.builder.get_object("label_fecha_tapa")
        self.entry_api_url = self.builder.get_object("entry_api_url")
        self.entry_url = self.builder.get_object("entry_url")
        self.scale_raiting = self.builder.get_object("scale_raiting")
        self.text_resumen = self.builder.get_object("text_resumen")
        self.textbuffer = self.text_resumen.get_buffer()

        # inicializamos el modelo con rotulos del manager

    def set_volume(self, id_volume):
        self.comicbooks_manager.set_volume(id_volume=id_volume)
        volume_mamange = Volumens(session = self.session)
        volume = volume_mamange.get(id_volume)
        self.label_nombre_volumen.set_text(volume.nombre)

    def set_comicbook_number(self, numero):
        #todo validar volumn seteado
        self.comicbooks_manager.set_filtro(Comicbook_Info.numero == numero)

        self.comicbooks_manager.getFirst()

    def seleccion_fecha(self, widget):
        print(widget.get_date().year)
        self.label_fecha_tapa.set_text(datetime.date(year=widget.get_date().year, month=widget.get_date().month+1, day=widget.get_date().day).strftime("%d/%m/%Y"))
        self.popover.popdown()
    def combobox_change(self,widget):
        if widget.get_active_iter() is not None:
            self.publishers_manager.set_order(self.publishers_manager.lista_opciones[widget.get_model()[widget.get_active_iter()][0]])

    def boton_guardar(self,widget):
        self.publishers_manager.save()

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
            self.label_fecha_tapa.set_text(datetime.date.fromordinal(comicbook_info.fecha_tapa).strftime("%d/%m/%Y"))
            self.entry_api_url.set_text(comicbook_info.api_detail_url)
            self.entry_url.set_text(comicbook_info.url)
            self.scale_raiting.set_value_pos(comicbook_info.rating)
            self.textbuffer.set_text("comicbook_info.resumen")

            # if publisher.hasImageCover():
            #     publisher.localLogoImagePath = publisher.getImageCoverPath()
            #     if publisher.localLogoImagePath[-3].lower()=='gif':
            #         gif = GdkPixbuf.PixbufAnimation.new_from_file(publisher.localLogoImagePath).get_static_image()
            #         self.publisher_logo_image.set_from_pixbuf(gif.scale_simple(250, 250, 3))
            #     else:
            #         pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            #             filename=publisher.getImageCoverPath(),
            #             width=250,
            #             height=250,
            #             preserve_aspect_ratio=True)
            #         self.publisher_logo_image.set_from_pixbuf(pixbuf)
            # else:
            #     pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            #         filename=self.publishers_manager.pahThumnails + "sin_caratula_publisher.jpg",
            #         width=250,
            #         height=250,
            #         preserve_aspect_ratio=True)
            #     self.publisher_logo_image.set_from_pixbuf(pixbuf)
            # self.label_resumen.set_text(publisher.deck)

    def click_limpiar(self, widget):
        print("dsldsa")
        self.entry_url.clear()
        # self.entradaNombre.delete(0, END)
        # self.entradaUrl.delete(0, END)
        # self.textoDescripcion.config(text='')


if __name__ == "__main__":

    cbi = Comicbook_Info_Gtk()
    cbi.set_volume('2050')
    cbi.set_comicbook_number(1)
    cbi.window.show_all()
    cbi.window.connect("destroy", Gtk.main_quit)
    Gtk.main()