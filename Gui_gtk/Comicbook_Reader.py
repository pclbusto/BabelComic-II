import os
import Entidades.Init
from Entidades.Entitiy_managers import Commicbooks_detail, Comicbooks, Comicbook
from Entidades.Agrupado_Entidades import  Setup
from Gui_gtk import Publisher_lookup_gtk
from Gui_gtk.Publisher_vine_search_gtk import Publisher_vine_search_gtk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk



class ComickBook_Reader_Gtk():
    # todo implementar los botones de limpiar, guardar y borrar

    def __init__(self,  session=None, id_comicbook=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.handlers = {'mouse_move': self.mouse_move,
                         'click': self.click}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Comicbook_Reader.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comicbook_Reader")
        self.pagina = self.builder.get_object("pagina")
        self.header = self.builder.get_object("header")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.window.resize(900, 900)
        self.window.maximize()
        self.over = self.builder.get_object("over")
       
        if id_comicbook is not None:
            self.comicbooks_manager = Comicbooks(session=self.session, lista_comics_id=[id_comicbook])
            self.id_comicbook = id_comicbook
            self.load_comic()

        self.scale = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.boton = Gtk.Button()
        self.scale.add(self.boton)
        self.scale.set_valign(Gtk.Align.CENTER)
        self.scale.set_halign(Gtk.Align.CENTER)
        self.scale.set_size_request(400, 1000)
        self.scale.set_hexpand(True)

    def mouse_move(self, widget, args):
        pass

    def load_comic(self):
        self.comicbook = self.comicbooks_manager.getFirst()
        self.comicbook.openCbFile()
        self._load_page_picture()

    def _load_page_picture(self):
        stream = self.comicbook.get_image_page_gtk()
        print(self.window.is_maximized())
        alto = ((1440.0-90) / stream.get_height())
        self.pagina.set_from_pixbuf(
            #vamos a mostrar las paginas en el mismo tamaño
            stream.scale_simple(int(stream.get_width() * alto), int(stream.get_height() * alto), 1))
    def clear(self):
        self.list_entry_id[self.index].set_text('')
        self.list_entry_nombre[self.index].set_text('')
        self.list_entry_id_externo[self.index].set_text('')
        self.list_entry_url[self.index].set_text('')
        # self.list_publisher_logo_image = [self.builder.get_object('publisher_logo_image'),
        #                                   self.builder.get_object('publisher_logo_image1')]
        self.list_label_resumen[self.index].set_text('')


    def click(self, widget, event):
        print(event)
        if event.keyval == Gdk.KEY_Right:
            self.comicbook.next_page()
        if event.keyval == Gdk.KEY_Left:
            self.comicbook.prev_page()

        self._load_page_picture()



if __name__ == "__main__":
    pub = ComickBook_Reader_Gtk(id_comicbook=223)
    pub.window.show_all()
    pub.window.connect("destroy", Gtk.main_quit)
    Gtk.main()