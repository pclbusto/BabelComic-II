
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from gi.repository import Gdk
import Entidades.Init
from Entidades.Entitiy_managers import Volumens
from Gui_gtk.Volumen_lookup_gtk import Volume_lookup_gtk
from Gui_gtk.Volumen_vine_search_gtk import Volumen_vine_search_Gtk
from Gui_gtk.Comicbook_info_Gtk import Comicbook_Info_Gtk
from Gui_gtk.Publisher_lookup_gtk import Publisher_lookup_gtk
from Gui_gtk.Comicbooks_info_gtk import Comicbooks_info_gtk

class VolumeGuiGtk():
    # todo implementar los botones de limpiar, guardar y borrar
    # todo clase que administre el comportamiento completo de alta, baja mdoficacion navegacion y borrado
    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'getFirst': self.getFirst, 'getLast': self.getLast, 'getPrev': self.getPrev, 'getNext': self.getNext,
                         'getLast': self.getLast, 'boton_cargar_desde_web_click': self.boton_cargar_desde_web_click,
                         'click_lookup_volume': self.click_lookup_volume,'change_id_volume': self.change_id_volume,
                         'click_nuevo': self.click_nuevo, 'combobox_change': self.combobox_change,
                         'selecion_pagina': self.selecion_pagina, 'click_guardar': self.click_guardar,
                         'evento': self.evento,
                         'click_eliminar': self.click_eliminar, 'click_derecho':self.click_derecho,
                         'click_lookup_editorial': self.click_lookup_editorial,
                         'pop_up_menu': self.pop_up_menu,
                         'abrir_covers': self.abrir_covers}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Volumen.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volume_gtk")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.stack = self.builder.get_object("stack")
        self.lista_items = [self.builder.get_object("item_0"), self.builder.get_object("item_1")]
        self.index = 0
        self.list_entry_id = [self.builder.get_object("entry_id"), self.builder.get_object("entry_id1")]
        self.list_entry_nombre = [self.builder.get_object("entry_nombre"), self.builder.get_object("entry_nombre1")]
        self.list_label_url = [self.builder.get_object("label_url"), self.builder.get_object("label_url1")]
        print(type(self.list_entry_id[self.index]))
        self.list_label_api_url = [self.builder.get_object("label_api_url"), self.builder.get_object("label_api_url1")]
        self.list_label_cover_url = [self.builder.get_object("label_cover_url"), self.builder.get_object("label_cover_url1")]
        self.list_entry_id_editorial = [self.builder.get_object("entry_id_editorial"), self.builder.get_object("entry_id_editorial1")]
        self.list_volumen_logo_image = [self.builder.get_object("volumen_logo_image"), self.builder.get_object("volumen_logo_image1")]
        # self.volumen_logo_image = self.builder.get_object("volumen_logo_image")

        self.list_label_nombre_editorial = [self.builder.get_object("label_nombre_editorial"), self.builder.get_object("label_nombre_editorial1")]
        self.list_entry_anio_inicio = [self.builder.get_object("entry_anio_inicio"), self.builder.get_object("entry_anio_inicio1")]
        self.list_entry_cantidad_numeros = [self.builder.get_object("entry_cantidad_numeros"), self.builder.get_object("entry_cantidad_numeros1")]
        self.list_liststore_combobox = [self.builder.get_object("liststore_combobox"), self.builder.get_object("liststore_combobox1")]
        self.list_resumen_volumen = [self.builder.get_object("resumen_volumen"), self.builder.get_object("resumen_volumen1")]
        self.list_liststore_comics_in_volume = [self.builder.get_object("liststore_comics_in_volume"), self.builder.get_object("liststore_comics_in_volume1")]
        self.list_treeview_comics_in_volumen = [self.builder.get_object("treeview_comics_in_volumen"), self.builder.get_object("treeview_comics_in_volumen1")]
        self.list_progressbar_procentaje_completado = [self.builder.get_object("progressbar_procentaje_completado"), self.builder.get_object("progressbar_procentaje_completado1")]
        self.list_label_cantidad_comics_asociados = [self.builder.get_object("label_cantidad_comics_asociados"), self.builder.get_object("label_cantidad_comics_asociados1")]

        self.volumens_manager = Volumens(session=self.session)
        self.volume = None
        # print(self.volume)
        # if self.volume is not None:
        #     self.loadVolume(self.volume)
        self.getFirst(None)

        # self.combobox_orden = self.builder.get_object("combobox_orden")
        self.offset = 0
        self.cantidadRegistros = self.volumens_manager.get_count()
        self.pagina_actual = 0
        self.menu = self.builder.get_object("menu")
        # # inicializamos el modelo con rotulos del manager
        # self.liststore_combobox.clear()
        # for clave in self.volumens_manager.lista_opciones.keys():
        #     self.liststore_combobox.append([clave])
        # self.combobox_orden.set_active(0)
        # self.getFirst("")

    def abrir_covers(self, widget):
        bc = Comicbooks_info_gtk(volumen_id=self.volumens_manager.entidad.id_volume)
        bc.window.show()
        self.menu.popdown()

    def pop_up_menu(self,widget):
        # self.popover.set_relative_to(button)
        self.menu.show_all()
        self.menu.popup()

    def getFirst(self, widget):
        volume = self.volumens_manager.getFirst()
        print(volume)
        # self.index = (self.index + 1)%2
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        if volume is not None:
            self.loadVolume(volume)


    def getLast(self, widget):
        volume = self.volumens_manager.getLast()
        print('volume')
        print(volume)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT )
        self.loadVolume(volume)

    def getNext(self, widget):
        volume = self.volumens_manager.getNext()
        print('volume')
        print(volume)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT   )
        self.loadVolume(volume)

    def getPrev(self, widget):
        volume = self.volumens_manager.getPrev()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT  )
        self.loadVolume(volume)

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
            model, treeiter = self.list_treeview_comics_in_volumen[self.index].get_selection().get_selected()
            cbi.set_comicbook(model[treeiter][4])
            cbi.window.show_all()

    def selecion_pagina(self, widget, page, page_num):
        self.pagina_actual = page_num
        if page_num == 1:
            comicbooks_in_volumen = self.volumens_manager.get_comicbook_info_by_volume()
            self.list_liststore_comics_in_volume[self.index].clear()
            for comicbook in comicbooks_in_volumen:
                #print(comicbook.id_comicbook_info, type(comicbook.id_comicbook_info))
                self.list_liststore_comics_in_volume[self.index].append([comicbook.numero, comicbook.titulo, comicbook.cantidad, comicbook.cantidad, comicbook.id_comicbook_info, comicbook.orden])

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

    def click_lookup_editorial(self, widget):
        print("Holaaaaaaaa")
        lookup = Publisher_lookup_gtk(self.session, self.return_lookup)
        lookup.window.show()

    def change_id_volume(self, widget, event):
        self.editorial = None
        self.set_volumen_id(self.list_entry_id[self.index].get_text())

    def set_volumen_id(self, volumen_id):
        print(volumen_id)
        if (self.list_entry_id[self.index].get_text() != ''):
            volume = self.volumens_manager.get(volumen_id)
            self.loadVolume(volume)

    def return_lookup(self, id_volume):
        if id_volume != '':
            self.goto(id_volume)

    def return_lookup_editorial(self, id_editorial):
        if id_editorial != '':
            self.volumens_manager.entidad.id_publisher = id_editorial

    def goto(self, id_volume):
        self.list_entry_id[self.index].set_text(str(id_volume))
        volume = self.volumens_manager.get(self.list_entry_id[self.index].get_text())
        self.loadVolume(volume)

    def loadVolume(self, volumen):
        if self.volume is not None:
            if volumen == self.volume:
                print("SON IGUALES")
                return
            else:
                print("NO SON IGUALES")

        self.volume = volumen
        self.clear()
        if self.volumens_manager.entidad is not None:
            #print("Volumen {}".format(self.volume))
            self.index += 1
            self.index %= 2
            self.list_entry_id[self.index].set_text(str(volumen.id_volume))
            self.list_entry_nombre[self.index].set_text(volumen.nombre)
            if len(volumen.url) >= 50:
                self.list_label_url[self.index].set_label(volumen.url[:50]+"...")
            else:
                self.list_label_url[self.index].set_label(volumen.url)
            self.list_label_url[self.index].set_uri(volumen.url)



            if len(volumen.get_api_url()) >= 50:
                self.list_label_api_url[self.index].set_label(volumen.get_api_url()[:50]+"...")
            else:
                self.list_label_api_url[self.index].set_label(volumen.get_api_url())
            self.list_label_api_url[self.index].set_uri(volumen.get_api_url())

            if len(volumen.image_url) >= 50:
                self.list_label_cover_url[self.index].set_label(volumen.image_url[:50]+"...")

            else:
                self.list_label_cover_url[self.index].set_label(volumen.image_url)
            self.list_label_cover_url[self.index].set_uri(volumen.image_url)
            #
            self.list_entry_id_editorial[self.index].set_text(volumen.id_publisher)
            self.list_label_nombre_editorial[self.index].set_text(volumen.publisher_name)
            self.list_entry_anio_inicio[self.index].set_text(str(volumen.anio_inicio))
            self.list_entry_cantidad_numeros[self.index].set_text(str(volumen.cantidad_numeros))
            self.list_resumen_volumen[self.index].set_text(volumen.descripcion)
            if volumen.cantidad_numeros>0:
                self.list_progressbar_procentaje_completado[self.index].set_fraction(self.volumens_manager.get_volume_status()/volumen.cantidad_numeros)
            else:
                self.list_progressbar_procentaje_completado[self.index].set_fraction(0)
            self.list_label_cantidad_comics_asociados[self.index].set_text(str(self.volumens_manager.get_cantidad_comics_asociados_al_volumen()))
            print("PATH: {}".format(volumen.getImagePath()))
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=volumen.getImagePath(),
                width=250,
                height=250,
                preserve_aspect_ratio=True)

            # # print(self.volumen_logo_image)
            self.list_volumen_logo_image[self.index].set_from_pixbuf(pixbuf)

            comicbooks_in_volumen = self.volumens_manager.get_comicbook_info_by_volume()
            print(self.list_liststore_comics_in_volume)
            self.list_liststore_comics_in_volume[0].clear()
            for comicbook in comicbooks_in_volumen:
                # print(comicbook.id_comicbook_info, type(comicbook.id_comicbook_info))
                self.list_liststore_comics_in_volume[0].append(
                    [comicbook.numero, comicbook.titulo, comicbook.cantidad, comicbook.cantidad,
                     comicbook.id_comicbook_info, comicbook.orden])
            self.stack.set_visible_child(self.lista_items[self.index])
            # if self.pagina_actual == 1:
            #     self.selecion_pagina(None, None, 1)




    def click_eliminar(self, widget):
        self.volumens_manager.rm()

    def clear(self):
        print(type(self.list_entry_id[self.index]))

        self.list_entry_id[self.index].set_text('')
        print(type(self.list_entry_id[self.index]))

        # self.entry_nombre.set_text('')
        # self.label_url.set_uri('')
        # self.list_label_api_url[self.index].set_uri('')
        # self.label_cover_url.set_uri('')
        # self.entry_id_editorial.set_text('')
        # self.label_nombre_editorial.set_text('')
        # self.entry_anio_inicio.set_text('')
        # self.entry_cantidad_numeros.set_text('')
        pass

    def copyFromWindowsToEntity(self):
        self.volumens_manager.entidad.nombre = self.list_entry_nombre[self.index].get_text()
        #self.volume.deck = self..get()
        # self.volumens_manager.entidad.descripcion = self.entradaId.get()
        self.volumens_manager.entidad.url = self.list_label_url[self.index].get_uri()
        self.volumens_manager.entidad.image_url = self.list_label_cover_url[self.index].get_uri()
        self.volumens_manager.entidad.anio_inicio = self.list_entry_anio_inicio[self.index].get_text()
        self.volumens_manager.entidad.cantidad_numeros = self.list_entry_cantidad_numeros[self.index].get_text()

    def click_guardar(self, widget):
        self.copyFromWindowsToEntity()
        self.volumens_manager.save()
        # self.session.add(self.volumens_manager.entidad)
        # self.session.commit()






    def click_nuevo(self, widget):
        self.volumens_manager.new_record()
        print(self.volumens_manager.entidad)
        self.loadVolume(self.volumens_manager.entidad)

if __name__ == "__main__":
    print("Hola")
    pub = VolumeGuiGtk()
    pub.window.show_all()
    pub.set_volumen_id(92557)
    pub.window.connect("destroy", Gtk.main_quit)
    Gtk.main()

