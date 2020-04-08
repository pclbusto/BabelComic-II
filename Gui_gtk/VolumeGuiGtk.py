
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from gi.repository import Gdk
import Entidades.Init
from Entidades.Entitiy_managers import Volumens
import Entidades.Init
from Gui_gtk.Volumen_lookup_gtk import Volume_lookup_gtk
from Gui_gtk.Volumen_vine_search_gtk import Volumen_vine_search_Gtk
from Gui_gtk.Comicbook_info_Gtk import Comicbook_Info_Gtk
from bs4 import BeautifulSoup

class VolumeGuiGtk():
    # todo implementar los botones de limpiar, guardar y borrar
    # todo clase que administre el comportamiento completo de alta, baja mdoficacion navegacion y borrado
    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext,
                         'getLast': self.getLast, 'boton_cargar_desde_web_click': self.boton_cargar_desde_web_click,
                         'click_lookup_volume': self.click_lookup_volume,'change_id_volume': self.change_id_volume,
                         'click_nuevo': self.click_nuevo, 'combobox_change': self.combobox_change,
                         'selecion_pagina': self.selecion_pagina, 'click_guardar': self.click_guardar,
                         'evento': self.evento,
                         'click_eliminar': self.click_eliminar, 'click_derecho':self.click_derecho}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Volumen.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volume_gtk")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.entry_id = self.builder.get_object("entry_id")
        self.entry_nombre = self.builder.get_object("entry_nombre")
        self.label_url = self.builder.get_object("label_url")
        self.label_api_url = self.builder.get_object("label_api_url")
        self.label_cover_url = self.builder.get_object("label_cover_url")
        self.entry_id_editorial = self.builder.get_object("entry_id_editorial")
        self.label_nombre_editorial = self.builder.get_object("label_nombre_editorial")
        self.entry_anio_inicio = self.builder.get_object("entry_anio_inicio")
        self.entry_cantidad_numeros = self.builder.get_object("entry_cantidad_numeros")
        self.volumen_logo_image = self.builder.get_object("volumen_logo_image")
        self.liststore_combobox = self.builder.get_object("liststore_combobox")
        self.resumen_volumen = self.builder.get_object("resumen_volumen")
        self.liststore_comics_in_volume = self.builder.get_object("liststore_comics_in_volume")
        self.treeview_comics_in_volumen = self.builder.get_object("treeview_comics_in_volumen")
        self.progressbar_procentaje_completado = self.builder.get_object("progressbar_procentaje_completado")
        self.label_cantidad_comics_asociados = self.builder.get_object("label_cantidad_comics_asociados")


        self.volumens_manager = Volumens(session=self.session)
        self.combobox_orden = self.builder.get_object("combobox_orden")
        self.offset = 0
        self.cantidadRegistros = self.volumens_manager.get_count()
        self.pagina_actual = 0
        # inicializamos el modelo con rotulos del manager
        self.liststore_combobox.clear()
        for clave in self.volumens_manager.lista_opciones.keys():
            self.liststore_combobox.append([clave])
        self.combobox_orden.set_active(0)
        self.getFirst("")

    def pop_up_menu(self,widget):
        # self.popover.set_relative_to(button)
        self.menu.show_all()
        self.menu.popup()

    def evento(self, widget, args):
        print(args.keyval)
        if args.keyval == Gdk.KEY_Escape:
            self.window.close()

    def click_derecho(self,widget, event):
        print("ACA ESTAMOS {}".format(event.get_click_count()))
        if event.get_click_count()[1] == 2:
            cbi = Comicbook_Info_Gtk()
            #seteamos el volumen para poder navegar entre los comicbooks info
            cbi.set_volume(self.volumens_manager.entidad.id_volume)
            model, treeiter = self.treeview_comics_in_volumen.get_selection().get_selected()
            cbi.set_comicbook(model[treeiter][4])
            cbi.window.show_all()

    def selecion_pagina(self, widget, page, page_num):
        self.pagina_actual = page_num
        if page_num == 1:
            comicbooks_in_volumen = self.volumens_manager.get_comicbook_info_by_volume()
            self.liststore_comics_in_volume.clear()
            for comicbook in comicbooks_in_volumen:
                #print(comicbook.id_comicbook_info, type(comicbook.id_comicbook_info))
                self.liststore_comics_in_volume.append([comicbook.numero, comicbook.titulo, comicbook.cantidad, comicbook.cantidad, comicbook.id_comicbook_info, comicbook.orden])

    def combobox_change(self, widget):
        if widget.get_active_iter() is not None:
            self.volumens_manager.set_order(
                self.volumens_manager.lista_opciones[widget.get_model()[widget.get_active_iter()][0]])

    def boton_cargar_desde_web_click(self,widget):
        volumen_vine_search = Volumen_vine_search_Gtk(self.session)
        volumen_vine_search.window.show()

    def click_lookup_volume(self, widget):
        lookup = Volume_lookup_gtk(self.session, self.return_lookup)
        lookup.window.show()

    def change_id_volume(self, widget, event):
        self.editorial = None
        self.set_volumen_id(self.entry_id.get_text())

    def set_volumen_id(self, volumen_id):
        print(volumen_id)
        if (self.entry_id.get_text() != ''):
            volume = self.volumens_manager.get(volumen_id)
            self.loadVolume(volume)
    def return_lookup(self, id_volume):
        if id_volume!='':
            self.entry_id.set_text(str(id_volume))
            print("Recuperando info: {}".format(id_volume))
            volume = self.volumens_manager.get(self.entry_id.get_text())
            self.loadVolume(volume)

    def loadVolume(self, volumen):
        self.clear()
        if self.volumens_manager.entidad is not None:
            #print("Volumen {}".format(self.volume))
            self.entry_id.set_text(str(volumen.id_volume))
            self.entry_nombre.set_text(volumen.nombre)
            self.label_api_url.set_uri(volumen.get_api_url())
            if len(volumen.get_api_url()) >= 50:
                self.label_api_url.set_label(volumen.get_api_url()[:50]+"...")
            else:
                self.label_api_url.set_label(volumen.get_api_url())

            self.label_url.set_uri(volumen.url)
            if len(volumen.url) >= 50:
                self.label_url.set_label(volumen.url[:50]+"...")
            else:
                self.label_url.set_label(volumen.url)
            self.label_cover_url.set_uri(volumen.image_url)
            if len(volumen.image_url) >= 50:
                self.label_cover_url.set_label(volumen.image_url[:50]+"...")
            else:
                self.label_cover_url.set_label(volumen.image_url)

            self.entry_id_editorial.set_text(volumen.id_publisher)
            self.label_nombre_editorial.set_text(volumen.publisher_name)
            self.entry_anio_inicio.set_text(str(volumen.anio_inicio))
            self.entry_cantidad_numeros.set_text(str(volumen.cantidad_numeros))
            self.resumen_volumen.set_text(BeautifulSoup(volumen.descripcion, features="lxml").get_text("\n"))
            if volumen.cantidad_numeros>0:
                self.progressbar_procentaje_completado.set_fraction(self.volumens_manager.get_volume_status()/volumen.cantidad_numeros)
            else:
                self.progressbar_procentaje_completado.set_fraction(0)
            self.label_cantidad_comics_asociados.set_text(str(self.volumens_manager.get_cantidad_comics_asociados_al_volumen()))
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=volumen.getImagePath(),
                width=250,
                height=250,
                preserve_aspect_ratio=True)

            # print(self.volumen_logo_image)
            self.volumen_logo_image.set_from_pixbuf(pixbuf)
            if self.pagina_actual == 1:
                self.selecion_pagina(None, None, 1)


    def getFirst(self,widget):
        volume = self.volumens_manager.getFirst()
        print(volume)
        if volume is not None:
            self.loadVolume(volume)

    def click_eliminar(self, widget):
        self.volumens_manager.rm()

    def clear(self):
        self.entry_nombre.set_text('')
        self.label_url.set_uri('')
        self.label_api_url.set_uri('')
        self.label_cover_url.set_uri('')
        self.entry_id_editorial.set_text('')
        self.label_nombre_editorial.set_text('')
        self.entry_anio_inicio.set_text('')
        self.entry_cantidad_numeros.set_text('')

    def getNext(self, widget):
        volume = self.volumens_manager.getNext()
        print('volume')
        print(volume)
        self.loadVolume(volume)

    def copyFromWindowsToEntity(self):
        self.volumens_manager.entidad.nombre = self.entry_nombre.get_text()
        #self.volume.deck = self..get()
        # self.volumens_manager.entidad.descripcion = self.entradaId.get()
        self.volumens_manager.entidad.url = self.label_url.get_uri()
        self.volumens_manager.entidad.image_url = self.label_cover_url.get_uri()
        self.volumens_manager.entidad.anio_inicio = self.entry_anio_inicio.get_text()
        self.volumens_manager.entidad.cantidad_numeros = self.entry_cantidad_numeros.get_text()

    def click_guardar(self, widget):
        self.copyFromWindowsToEntity()
        self.session.add(self.volumens_manager.entidad)
        self.session.commit()

    def getPrev(self,widget):
        volume = self.volumens_manager.getPrev()
        self.loadVolume(volume)

    def getLast(self,widget):
        volume = self.volumens_manager.getLast()
        self.loadVolume(volume)

    def click_nuevo(self, widget):
        self.volumens_manager.new_record()
        print(self.volumens_manager.entidad)
        self.loadVolume(self.volumens_manager.entidad)

if __name__ == '__main__':

    if __name__ == "__main__":
        pub = VolumeGuiGtk()
        pub.window.show_all()
        pub.window.connect("destroy", Gtk.main_quit)
        Gtk.main()

