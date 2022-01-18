import os
# import Entidades.Init
# from Entidades.Entitiy_managers import Publishers
# from Entidades.Agrupado_Entidades import  Setup
from Gui_gtk4.Publisher_lookup_Gtk4 import Publisher_lookup_gtk
from Gui_gtk4.Publisher_Vine_Search_gtk4 import Publisher_vine_search_gtk

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GdkPixbuf

class PublisherGtk():
    # todo implementar los botones de limpiar, guardar y borrar

    def __init__(self,  session=None,):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        # self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext,
        #                  'getLast': self.getLast, 'click_lookup_button':self.open_lookup, 'id_changed': self.id_changed,
        #                  'click_cargar_desde_web':self.click_cargar_desde_web, 'click_nuevo': self.click_nuevo,
        #                  'combobox_change':self.combobox_change, 'click_guardar': self.click_guardar,
        #                  'pop_up_menu': self.pop_up_menu}
        self.handlers = {}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Publisher_gtk4.glade")
        # self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("PublisherGtk")
        # self.window.set_icon_from_file('../iconos/BabelComic.png')
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
        self.publisher = None
        # inicializamos el modelo con rotulos del manager
        self.liststore_combobox.clear()
        # for clave in self.publishers_manager.lista_opciones.keys():
        #     self.liststore_combobox.append([clave])

    def pop_up_menu(self,widget):
        # self.popover.set_relative_to(button)
        self.menu.show_all()
        self.menu.popup()

    def combobox_change(self,widget):
        if widget.get_active_iter() is not None:
            self.publishers_manager.set_order(self.publishers_manager.lista_opciones[widget.get_model()[widget.get_active_iter()][0]])

    def click_guardar(self, widget):
        self.publishers_manager.save()

    def click_nuevo(self, widget):
        self.publishers_manager.new_record()
        print(self.publishers_manager.entidad)
        self.load_publisher(self.publishers_manager.entidad)


    def click_cargar_desde_web(self, widget):
        publisher_vine_search = Publisher_vine_search_gtk(self.session)
        publisher_vine_search.window.show()

    def id_changed(self,widget, test):
        if self.list_entry_id[self.index].get_text()!='':
            publisher = self.publishers_manager.get(self.list_entry_id[self.index].get_text())
            self.load_publisher(publisher)

    def return_lookup(self, id_publisher):
        if id_publisher != '':
            self.goto(id_publisher)

    def goto(self, id_publisher):
        self.list_entry_id[self.index].set_text(str(id_publisher))
        publisher = self.publishers_manager.get(self.list_entry_id[self.index].get_text())
        self.load_publisher(publisher)

    def open_lookup(self, widget):
        lookup = Publisher_lookup_gtk(self.session, self.return_lookup)
        lookup.window.show()

    def getFirst(self, widget):
        publisher = self.publishers_manager.getFirst()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        print(publisher)
        self.load_publisher(publisher)

    def getPrev(self, widget):
        publisher = self.publishers_manager.getPrev()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        print(publisher)
        self.load_publisher(publisher)

    def getNext(self, widget):
        publisher = self.publishers_manager.getNext()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        print(publisher)
        self.load_publisher(publisher)

    def getLast(self, widget):
        publisher = self.publishers_manager.getLast()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        print(publisher)
        self.load_publisher(publisher)

    def load_publisher(self, publisher):
        if self.publisher is not None:
            if publisher == self.publisher:
                return
        self.publisher = publisher
        self.clear()
        if publisher is not None:
            self.index += 1
            self.index %= 2
            self.list_entry_id[self.index].set_text(str(publisher.id_publisher))
            self.list_entry_nombre[self.index].set_text(publisher.name)
            self.list_entry_url[self.index].set_text(publisher.siteDetailUrl)
            if publisher.hasImageCover():
                localLogoImagePath = publisher.getImageCoverPath()
                if localLogoImagePath[-3].lower() == 'gif':
                    gif = GdkPixbuf.PixbufAnimation.new_from_file(localLogoImagePath).get_static_image()
                    self.list_publisher_logo_image[self.index].set_from_pixbuf(gif.scale_simple(250, 250, 3))
                else:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        filename=publisher.getImageCoverPath(),
                        width=250,
                        height=250,
                        preserve_aspect_ratio=True)
                    self.list_publisher_logo_image[self.index].set_from_pixbuf(pixbuf)
            else:
                print("NO TIENE COVER")
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename=self.publishers_manager.pahThumnails + "sin_caratula_publisher.jpg",
                    width=250,
                    height=250,
                    preserve_aspect_ratio=True)
                self.list_publisher_logo_image[self.index].set_from_pixbuf(pixbuf)
            self.list_label_resumen[self.index].set_text(publisher.deck)

            self.stack.set_visible_child(self.lista_items[self.index])

    def clear(self):
        self.list_entry_id[self.index].set_text('')
        self.list_entry_nombre[self.index].set_text('')
        self.list_entry_id_externo[self.index].set_text('')
        self.list_entry_url[self.index].set_text('')
        # self.list_publisher_logo_image = [self.builder.get_object('publisher_logo_image'),
        #                                   self.builder.get_object('publisher_logo_image1')]
        self.list_label_resumen[self.index].set_text('')


    def click_limpiar(self, widget):
        print("dsldsa")
        self.entry_url.clear()
        # self.entradaNombre.delete(0, END)
        # self.entradaUrl.delete(0, END)
        # self.textoDescripcion.config(text='')

def activate(app):
    win = Gtk.ApplicationWindow(application=app)

    title = Gtk.Label()
    title.set_text("Editorial")
    header = Gtk.HeaderBar()
    header.set_title_widget(title)
    boton_first = Gtk.Button.new_from_icon_name("go-first")
    boton_prev = Gtk.Button.new_from_icon_name("go-previous")
    boton_next = Gtk.Button.new_from_icon_name("go-next")
    boton_last = Gtk.Button.new_from_icon_name("go-last")
    boton_open_menu = Gtk.Button.new_from_icon_name("open-menu")
    header.pack_end(boton_open_menu)
    header.pack_end(boton_last)
    header.pack_end(boton_next)
    header.pack_end(boton_prev)
    header.pack_end(boton_first)
    win.set_titlebar(header)
    label_id = label_creator(label="Id")
    label_nombre = label_creator(label="Nombre")
    lable_id_externo = label_creator(label="Id. Externo")
    lable_url = label_creator(label="Url")
    lable_resumen = label_creator(label="Resumen")
    grid = Gtk.Grid()
    grid.set_row_spacing(6)
    grid.set_column_spacing(6)
    grid.set_margin_top(6)
    grid.set_margin_bottom(6)
    grid.set_margin_start(6)
    grid.set_margin_end(6)
    win.set_child(grid)

    grid.attach(label_id,0,0,1,1)
    grid.attach(label_nombre,0,1,1,1)
    grid.attach(lable_id_externo,0,2,1,1)
    grid.attach(lable_url,0,3,1,1)
    grid.attach(lable_resumen,0,4,1,1)

    entry_id = Gtk.Entry()
    entry_nombre = Gtk.Entry()
    entry_id_externo = Gtk.Entry()
    entry_url = Gtk.Entry()

    grid.attach_next_to(entry_id, label_id, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach_next_to(entry_nombre, label_nombre, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach_next_to(entry_id_externo, lable_id_externo, Gtk.PositionType.RIGHT, 1, 1)
    grid.attach_next_to(entry_url, lable_url, Gtk.PositionType.RIGHT, 1, 1)

    boton_lookup_publisher = Gtk.Button.new_from_icon_name("edit-find-symbolic")
    boton_lookup_publisher.set_halign(Gtk.Align.START)
    boton_edit_resumen = Gtk.Button.new_from_icon_name("edit-symbolic")
    boton_edit_resumen.set_halign(Gtk.Align.START)
    grid.attach_next_to(boton_lookup_publisher, entry_id, Gtk.PositionType.RIGHT,1,1)
    grid.attach_next_to(boton_edit_resumen, lable_resumen, Gtk.PositionType.RIGHT,1,1)

    scroll_window_resumen= Gtk.ScrolledWindow()
    text_view_resumen = Gtk.TextView()
    text_view_resumen.set_halign(Gtk.Align.FILL)
    text_view_resumen.set_valign(Gtk.Align.FILL)
    scroll_window_resumen.set_vexpand(True)
    scroll_window_resumen.set_hexpand(True)
    # text_view_resumen.set_size_request(100, 200)
    scroll_window_resumen.set_child(text_view_resumen)

    grid.attach_next_to(scroll_window_resumen, lable_resumen, Gtk.PositionType.BOTTOM, 10, 4)

    win.show()

def label_creator(label)->Gtk.Label:
    label = Gtk.Label(label=label)
    label.set_halign(Gtk.Align.END)
    return label

if __name__ == "__main__":
    app = Gtk.Application(application_id="test.BabelComics")
    app.connect("activate", activate)
    app.run()

    # pub = PublisherGtk()
    # # pub.window.show_all()
    # help(pub.window)
    # # pub.window.connect("destroy", Gtk.main_quit())
    # Gtk.main()