import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GLib, GObject
from gi.repository import Gdk
import Entidades.Init
from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Publishers.Publisher import Publisher
from Entidades.Setups.Setup import Setup
from Gui_gtk.ScannerGtk import ScannerGtk
from Gui_gtk.PublisherGuiGtk import PublisherGtk
from Gui_gtk.VolumeGuiGtk import VolumeGuiGtk
from Gui_gtk.Comic_vine_cataloger_gtk import Comic_vine_cataloger_gtk
from Gui_gtk.config_gtk import Config_gtk
import os.path
from PIL import Image
from rarfile import NotRarFile, BadRarFile

import threading

icons = ["edit-cut", "edit-paste", "edit-copy"]

class BabelComics_main_gtk():

    def __init__(self):

        self.session = Entidades.Init.Session()
        self.listaEditoriales = self.session.query(Publisher).all()

        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                            "coverIssuesThumbnails" + os.path.sep

        self.handlers = {'click_editorial': self.click_editorial,'click_boton_serie':self.click_boton_serie,
                         'item_seleccionado': self.item_seleccionado,'click_derecho':self.click_derecho,
                         'click_boton_refresh':self.click_boton_refresh,'click_catalogar':self.click_catalogar,
                         'click_boton_open_scanear':self.click_boton_open_scanear,
                         'click_boton_edit':self.click_boton_edit,
                         'click_boton_config':self.click_boton_config}


        # , 'selection': self.selection,
        #                  'click_boton_aceptar': self.click_boton_aceptar, 'click_boton_buscar': self.click_boton_buscar}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../BabelComic_main_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("BabelComics_main_gtk")
        self.boton_refresh= self.builder.get_object('boton_refresh')
        self.iconview = self.builder.get_object('iconview')
        # self.publisher_logo_image = self.builder.get_object('publisher_logo_image')
        self.tree_left = self.builder.get_object("tree_left")
        self.gtk_tree_view_publisher = self.builder.get_object('gtk_tree_view_publisher')
        self.menu_comic = self.builder.get_object("menu_comic")

        self.list_navegacion = self.builder.get_object('list_navegacion')
        self.list_navegacion.clear()

        for editorial in self.listaEditoriales:
            self.list_navegacion.append([editorial.name])
            print(editorial.id_publisher)

        self.liststore = Gtk.ListStore(Pixbuf, str, int)
        self.lista_pendientes = []
        self.loadAndCreateThumbnails()

        self.iconview.set_column_spacing(-1)
        self.iconview.set_item_padding(10)
        self.iconview.set_item_width(1)
        self.iconview.set_spacing(30)
        #
        # header = Gtk.HeaderBar()
        # self.opciones = Gtk.Button(label = 'Opciones')
        # self.opciones.connect("clicked", self.on_click_me_clicked)
        #
        # header.pack_end(self.opciones)
        # # self.set_titlebar(header)
        #
        # self.popover = Gtk.Popover()
        # vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # boton_scan = Gtk.ModelButton()
        # icono = Gtk.Image.new_from_icon_name("gtk-preferences",Gtk.IconSize.DIALOG  )
        # boton_scan.set_image(icono)
        # boton_scan.set_always_show_image(True)
        # #gtk-preferences
        # boton_scan.connect("clicked", self.on_click_scanner)
        # vbox.pack_start(boton_scan, False, True, 10)
        # # vbox.pack_start(boton_scan, False, True, 10)
        # # vbox.pack_start(Gtk.Label("Item 2"), False, True, 10)
        # self.popover.add(vbox)
        # self.popover.set_position(Gtk.PositionType.BOTTOM)


    def click_boton_config(self,widget):
        config = Config_gtk()
        config.window.show()

    def click_boton_open_scanear(self,widget):
        scanner = ScannerGtk(funcion_callback=self.loadAndCreateThumbnails)
        # scanner.window.connect("destroy", Gtk.main_quit)
        scanner.window.show()


    def click_catalogar(self,widget):
        comics = []
        for path in self.iconview.get_selected_items():
            indice  = path
            comics.append(self.listaComics[indice[0]])
            # print(self.listaComics[indice[0]])
        cvs = Comic_vine_cataloger_gtk(comics)
        cvs.window.show()
        self.menu_comic.popdown()

    def click_boton_refresh(self,widget):

        self.loadAndCreateThumbnails()

    def click_boton_edit(self, widget):
        # print("click refresh")
        # self.menu_comic.set_relative_to(widget)
        # self.menu_comic.show_all()
        # self.menu_comic.popup()
        comics = []
        for path in self.iconview.get_selected_items():
            indice = path
            comics.append(self.listaComics[indice[0]])
            # print(self.listaComics[indice[0]])
        cvs = Comic_vine_cataloger_gtk(comics)
        cvs.window.show()
        self.menu_comic.popdown()


    def click_derecho(self, widget, event):
        # click derecho
        if event.button == 3:
            print(self.tree_left.get_allocation().width)
            # print('mostrando menu')
            # help(event)
            # self.menu_comic.set_relative_to(None)
            rect = Gdk.Rectangle()
            rect.height=100
            rect.width= 100
            rect.x= event.x_root-self.tree_left.get_allocation().width
            # print(self.iconview.get_item_at_pos(event.x_root, event.y_root))
            # print(self.iconview.get_item_at_pos(event.x, event.y)[1])
            # print(event.x_root,event.y_root)
            self.menu_comic.set_pointing_to(rect)
            self.menu_comic.set_position(3)
            # self.menu_comic.show_all()
            self.menu_comic.popup()



    def item_seleccionado(self,selected):
        for path in self.iconview.get_selected_items():
            indice  = path
            print(self.listaComics[indice[0]])


    def click_boton_serie(self, widget):
        serie = VolumeGuiGtk(self.session)
        serie.window.show()

    def click_editorial(self, widget):
        print("hola")
        editorial = PublisherGtk(self.session)
        editorial.window.show()

    def on_click_scanner(self, button):
        # pub = ScannerGtk(self.loadAndCreateThumbnails)
        pub = ScannerGtk()
        pub.window.show()

    def on_click_me_clicked(self, button):
        self.popover.set_relative_to(self.opciones)
        self.popover.show_all()
        self.popover.popup()

    def crear_thumnails_background(self):
        print('iniciando crear_thumnails_background')
        for item in self.lista_pendientes:
            print(item)
            comic = item[0]
            nombreThumnail = item[1]
            iter = item[2]
            imagen_height_percent = 150 / comic.getImagePage().size[1]
            self.size = self.size = (int(imagen_height_percent * comic.getImagePage().size[0]), int(150))
            cover = comic.getImagePage().resize(self.size, Image.LANCZOS)
            cover.save(nombreThumnail)
            cover = Pixbuf.new_from_file(nombreThumnail)

            GLib.idle_add(self.crear_thumnail_background, cover, iter)
        print('termiando crear_thumnails_background')

    def crear_thumnail_background(self, cover, iter):

        self.liststore.set_value(iter, 0, cover)

    # def load_thumnails_in_background(self):
    #     # proceso que recorre la lista hasta que se terminen de cargar todos los thumnails
    #     while len(self.lista_pendientes) > 0:
    #         GLib.idle_add(self.load_thumnail_in_background)
    #         time.sleep(1)
    #         print(len(self.lista_pendientes))
    # def load_thumnail_in_background(self):
    #     # proceso que recorre la lista de pendientes y carga tod o thumnails que exista en el disco
    #     for item in self.lista_pendientes:
    #         if (os.path.isfile(item[1])):
    #             try:
    #                 cover = Pixbuf.new_from_file(item[1])
    #                 # self.liststore.append([cover, item[0].getNombreArchivo()])
    #                 self.liststore.set_value(item[2], 0, cover)
    #                 self.lista_pendientes.remove(item)
    #             except:
    #                 print("No se pudo leer el archivo")

    def loadAndCreateThumbnails(self):
        self.liststore.clear()
        self.lista_pendientes.clear()
        self.listaComics = self.session.query(ComicBook).order_by(ComicBook.path).all()
        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.cantidadThumnailsAGenerar = len(self.listaComics)
        self.cantidadThumnailsGenerados = 0
        print('iniciando thumnails')
        for index, comic in enumerate(self.listaComics):
            self.cantidadThumnailsGenerados += 1
            try:
                comic.openCbFile()
                nombreThumnail = self.pahThumnails + str(comic.comicId) + comic.getPageExtension()
                print(nombreThumnail)
                cover = None
                if (not os.path.isfile(nombreThumnail)):
                    cover = Pixbuf.new_from_file(self.pahThumnails + "sin_caratula.jpg")
                    iter = self.liststore.append([cover, comic.getNombreArchivo(), index])
                    self.lista_pendientes.append((comic, nombreThumnail, iter))
                else:
                    # print(nombreThumnail)
                    cover = Pixbuf.new_from_file(nombreThumnail)
                    self.liststore.append([cover, comic.getNombreArchivo(), index])

            except NotRarFile:
                print('error en el archivo ' + comic.path)
            except BadRarFile:
                print('error en el archivo ' + comic.path)
        print('terminando thumnails')
        thread_create = threading.Thread(target=self.crear_thumnails_background)
        thread_create.daemon = True
        thread_create.start()

if __name__ == "__main__":
    bc = BabelComics_main_gtk()
    bc.window.connect("destroy", Gtk.main_quit)
    bc.window.show()
    bc.window.maximize()
    Gtk.main()
