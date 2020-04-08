import os
import Entidades.Init
from Entidades.Entitiy_managers import Publishers
from Entidades.Agrupado_Entidades import  Setup
from Gui_gtk import Publisher_lookup_gtk
from Gui_gtk.Publisher_vine_search_gtk import Publisher_vine_search_gtk

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class PublisherGtk():
    # todo implementar los botones de limpiar, guardar y borrar

    def __init__(self,  session=None,):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext,
                         'getLast': self.getLast, 'click_lookup_button':self.open_lookup, 'id_changed':self.id_changed,
                         'click_cargar_desde_web':self.click_cargar_desde_web, 'boton_guardar':self.boton_guardar,
                         'combobox_change':self.combobox_change, 'click_limpiar':self.click_limpiar,
                         'pop_up_menu': self.pop_up_menu}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Publisher.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("PublisherGtk")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.liststore_combobox = self.builder.get_object("liststore_combobox")
        self.publishers_manager = Publishers(session=self.session)
        self.stack = self.builder.get_object('stack')
        self.index = 0
        self.menu = self.builder.get_object("menu")
        self.lista_items = [self.builder.get_object("item_0"), self.builder.get_object("item_1")]
        self.list_entry_id = [self.builder.get_object('entry_id'), self.builder.get_object('entry_id1')]
        self.list_entry_nombre = [self.builder.get_object('entry_nombre'), self.builder.get_object('entry_nombre1')]
        self.list_entry_id_externo = [self.builder.get_object('entry_id_externo'), self.builder.get_object('entry_id_externo1')]
        self.list_entry_url = [self.builder.get_object('entry_url'), self.builder.get_object('entry_url1')]
        self.list_publisher_logo_image = [self.builder.get_object('publisher_logo_image'), self.builder.get_object('publisher_logo_image1')]
        self.list_label_resumen = [self.builder.get_object('label_resumen'), self.builder.get_object('label_resumen1')]
        # self.list_combobox_orden = self.builder.get_object('combobox_orden')
        self.path_publisher_logo = self.session.query(Setup).first().directorioBase+ os.path.sep + "images" + os.path.sep + "logo publisher" + os.path.sep

        # inicializamos el modelo con rotulos del manager
        self.liststore_combobox.clear()
        for clave in self.publishers_manager.lista_opciones.keys():
            self.liststore_combobox.append([clave])
        # self.combobox_orden.set_active(0)
    def pop_up_menu(self,widget):
        # self.popover.set_relative_to(button)
        self.menu.show_all()
        self.menu.popup()

    def combobox_change(self,widget):
        if widget.get_active_iter() is not None:
            self.publishers_manager.set_order(self.publishers_manager.lista_opciones[widget.get_model()[widget.get_active_iter()][0]])

    def boton_guardar(self,widget):
        self.publishers_manager.save()

    def click_cargar_desde_web(self, widget):
        publisher_vine_search = Publisher_vine_search_gtk(self.session)
        publisher_vine_search.window.show()

    def id_changed(self,widget, test):
        if self.list_entry_id[self.index].get_text()!='':
            publisher = self.publishers_manager.get(self.list_entry_id[self.index].get_text())
            self._copy_to_window(publisher)

    def return_lookup(self, id_publisher):
        if id_publisher  !='':
            self.list_entry_id[self.index].set_text(str(id_publisher))
            publisher = self.publishers_manager.get(self.entry_id.get_text())
            self._copy_to_window(publisher)

    def open_lookup(self, widget):
        lookup = Publisher_lookup_gtk.Publisher_lookup_gtk(self.session, self.return_lookup)
        lookup.window.show()

    def getFirst(self, widget):
        publisher = self.publishers_manager.getFirst()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        print(publisher)
        self._copy_to_window(publisher)

    def getPrev(self, widget):
        publisher = self.publishers_manager.getPrev()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        print(publisher)
        self._copy_to_window(publisher)

    def getNext(self, widget):
        publisher = self.publishers_manager.getNext()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        print(publisher)
        self._copy_to_window(publisher)

    def getLast(self, widget):
        publisher = self.publishers_manager.getLast()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        print(publisher)
        self._copy_to_window(publisher)

    def _copy_to_window(self,publisher):
        # self.clearWindow()
        if publisher is not None:
            self.index += 1
            self.index %= 2
            self.list_entry_id[self.index].set_text(str(publisher.id_publisher))
            self.list_entry_nombre[self.index].set_text(publisher.name)
            # self.entry_id_externo.set_text(publisher.id_publisher_externo)
            self.list_entry_url[self.index].set_text(publisher.siteDetailUrl)

            if publisher.hasImageCover():
                publisher.localLogoImagePath = publisher.getImageCoverPath()
                if publisher.localLogoImagePath[-3].lower()=='gif':
                    gif = GdkPixbuf.PixbufAnimation.new_from_file(publisher.localLogoImagePath).get_static_image()
                    self.list_publisher_logo_image[self.index].set_from_pixbuf(gif.scale_simple(250, 250, 3))
                else:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        filename=publisher.getImageCoverPath(),
                        width=250,
                        height=250,
                        preserve_aspect_ratio=True)
                    self.list_publisher_logo_image[self.index].set_from_pixbuf(pixbuf)
            else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename=self.publishers_manager.pahThumnails + "sin_caratula_publisher.jpg",
                    width=250,
                    height=250,
                    preserve_aspect_ratio=True)
                self.list_publisher_logo_image[self.index].set_from_pixbuf(pixbuf)
            self.list_label_resumen[self.index].set_text(publisher.deck)

            self.stack.set_visible_child(self.lista_items[self.index])

    def click_limpiar(self, widget):
        print("dsldsa")
        self.entry_url.clear()
        # self.entradaNombre.delete(0, END)
        # self.entradaUrl.delete(0, END)
        # self.textoDescripcion.config(text='')


if __name__ == "__main__":

    pub = PublisherGtk()
    pub.window.show_all()
    pub.window.connect("destroy", Gtk.main_quit)
    Gtk.main()