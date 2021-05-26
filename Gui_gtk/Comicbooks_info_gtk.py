import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GLib, GObject
from gi.repository import Gdk

import Entidades.Init
from Entidades.Agrupado_Entidades import Comicbook, Publisher, Volume, Comicbook_Info, Arcos_Argumentales_Comics_Reference, Comicbook_Detail
from Entidades.Agrupado_Entidades import Setup
from Entidades.Entitiy_managers import Comicbooks_Info, Volumens

from Gui_gtk.PublisherGuiGtk import Publisher_lookup_gtk

from Gui_gtk.acerca_de_gtk import Acerca_de_gtk
from Gui_gtk.function_launcher_Gtk import Function_launcher_gtk
from Extras import BabelComics_Manager
import os.path
import math
from PIL import Image, ImageFile, ImageDraw
import threading, io
from PIL import ImageFont




class Comicbooks_info_gtk():

    def __init__(self, session=None, volumen_id=None):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session
        self.volumens_manager = Volumens(session)

        #Nos posicionamos en algun volumen ya se el pasado por parametro si existo o el primero
        if volumen_id is None:
            self.volumens_manager.getFirst()
        else:
            volumen = self.volumens_manager.get(volumen_id)
            if volumen is None:
                self.volumens_manager.getFirst()

        self.load_setup()

        self.handlers = {'click_derecho': self.click_derecho,
                         'cambio_seleccion': self.cambio_seleccion,
                         'get_prev_cover': self.get_prev_cover,
                         'get_next_cover': self.get_next_cover}

        self.cataloged_pix = Pixbuf.new_from_file_at_size('../iconos/Cataloged.png', 32, 32)

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Comicbooks_info.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comicbooks_info")
        self.menu = self.builder.get_object("menu")
        self.window.set_title("Comicbooks info")
        self.app_icon = Pixbuf.new_from_file_at_size('../iconos/iconoBabelComics-buuf.png', 32, 32)
        self.window.set_icon_from_file('../iconos/iconoBabelComics-buuf.png')
        self.window.set_default_icon_list([self.app_icon])
        self.iconview_Comicbooks_info = self.builder.get_object('iconview_Comicbooks_info')
        self.thread_creacion_thumnails = None
        self.lista_comics_esperando_por_thumnail=[]
        self.updating_gui = False
        self.salir_thread = False

        self.liststore = self.builder.get_object('liststore')
        self.lista_pendientes = []
        self.filtro = ''
        self.limit = self.session.query(Setup).first().cantidadComicsPorPagina
        self.offset = 0
        self.query = None
        self.comicbooks_info_manager = {}
        self.dictionary = {}
        self.cantidad_thumnails_pendiente = 0
        #self.search_change(None)

        self.iconview_Comicbooks_info.set_pixbuf_column(0)
        self.iconview_Comicbooks_info.set_text_column(1)
        self.iconview_Comicbooks_info.set_text_column(2)
        self.iconview_Comicbooks_info.set_column_spacing(-1)
        self.iconview_Comicbooks_info.set_item_padding(10)
        self.iconview_Comicbooks_info.set_item_width(1)
        self.iconview_Comicbooks_info.set_spacing(30)


        self.load_comicbooks_info()
        screen = Gdk.Screen.get_default()
        self.window.set_default_size(screen.width(), self.window.get_size()[1])

    def get_prev_cover(self, wiget):
        self.cambio_cover(False)
    def get_next_cover(self, wiget):
        self.cambio_cover(True)

    def cambio_cover(self, siguiente):
        selected_list = self.iconview_Comicbooks_info.get_selected_items()
        if len(selected_list) == 1:
            if siguiente:
                image = Image.open(self.comicbooks_info_manager[str(selected_list[0])].get_next_cover_complete_path()).convert("RGB")
                self.update_cover(str(selected_list[0]), image)
            else:
                image = Image.open(self.comicbooks_info_manager[str(selected_list[0])].get_prev_cover_complete_path()).convert("RGB")
                self.update_cover(str(selected_list[0]), image)

    def cambio_seleccion(self, widget):
        print('dsdhskdhsd')
        selected_list = widget.get_selected_items()
        if len(selected_list) == 1:
            print("Nombre :", self.comicbooks_info_manager[str(selected_list[0])].lista_covers)


    def click_derecho(self, widget, event):
        if event.button == 3:
            rect = Gdk.Rectangle()
            rect.height = 10
            rect.width = 10
            rect.x = int(event.x)
            #por bug o funciona asi pero el click en iconview trae las coordenadas sin tener en cuenta que es una scroll
            #como resultado si no ajustamos se correr el popup
            rect.y = int(event.y-self.iconview_Comicbooks_info.get_vadjustment().get_value())

            p = self.iconview_Comicbooks_info.get_path_at_pos(rect.x, rect.y)
            if p is not None:
                self.iconview_Comicbooks_info.select_path(p)

            self.menu.set_pointing_to(rect)
            self.menu.set_position(3)
            self.menu.set_relative_to(widget)
            self.menu.popup()

    def doble_click(self, widget, event):
        print(event.get_click_count())
        if event.get_click_count().click_count == 2:
            pass

    def image2pixbuf(self, im):
        """Convert Pillow image to GdkPixbuf"""
        data = im.tobytes()
        w, h = im.size
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB, False, 8, w, h, w * 3)
        return pix

    def create_grey_tumnails(self, lista):
        img = Image.new("RGB", (self.ancho_thumnail, int(self.ancho_thumnail*1.3)), (150, 150, 150))
        for i in range(0, len(lista)):
            img_aux = img.copy()
            d1 = ImageDraw.Draw(img_aux)
            font = ImageFont.truetype('../Extras/fonts/Comic Book.otf', 26)
            d1.text(((self.ancho_thumnail/2)-20, self.ancho_thumnail/2), str(i),  font=font, fill=(255, 255, 255))
            d1.polygon([(0, 0), (self.ancho_thumnail, 0), (self.ancho_thumnail, self.ancho_thumnail*2), (0, self.ancho_thumnail*2)], outline=(0, 0, 0))
            gdkpixbuff_thumnail = self.image2pixbuf(img_aux)
            # print(lista[i].titulo, lista[i].id_volume)
            GLib.idle_add(self.update_progess2, gdkpixbuff_thumnail, lista[i].titulo, lista[i].id_comicbook_info)

    def update_progess2(self, gdkpixbuff_thumnail, archivo_nombre, id_volume):
        self.liststore.append([gdkpixbuff_thumnail, archivo_nombre, id_volume])


    def load_setup(self):
        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + "coverIssuesThumbnails" + os.path.sep
        self.ancho_thumnail = self.session.query(Setup).first().anchoThumnail

    def load_comicbooks_info(self):
        self.liststore.clear()
        comicbook_info_manager = Comicbooks_Info(self.session)
        comicbook_info_manager.set_filtro(Comicbook_Info.id_volume == self.volumens_manager.entidad.id_volume)
        lista = comicbook_info_manager.getList()
        # print(lista)

        self.create_grey_tumnails(lista)
        t = threading.Thread(target=self.load_comicbooks_info_second_part, args=(lista,))
        t.start()

    def load_comicbooks_info_second_part(self, lista):

        for index, comicbook_info in enumerate(lista):
            self.comicbooks_info_manager[str(index)] = Comicbooks_Info(self.session)
            t = threading.Thread(target=self.load_comicbook_info_cover, args=(comicbook_info, index,))
            t.start()


    def seleccion_volumen(self, widget):
        selected_list = widget.get_selected_items()
        if len(selected_list) == 1:
            print("Nombre :", str(self.liststore[selected_list[0]][2]))

    def load_comicbook_info_cover(self, comicbook_info, index):
        #se hace local el manager para que casa hilo pueda buscar la info sin compartir el manager de comicbooks_info
        self.comicbooks_info_manager[str(index)].get(comicbook_info.id_comicbook_info)
        image = Image.open(self.comicbooks_info_manager[str(index)].get_first_cover_complete_path()).convert("RGB")
        # size = (self.ancho_thumnail, int(image.size[1] * self.ancho_thumnail / image.size[0]))
        # image.thumbnail(size, 3, 3)
        # img_aux = image.copy()
        # d1 = ImageDraw.Draw(img_aux)
        # d1.rectangle([(0, 0), (size[0] - 1, size[1] - 1)], outline=(0, 0, 0), width=3)
        # d1.rectangle([(0, 0), (size[0] - 1, size[1] - 1)], outline=(0, 0, 0), width=3)
        # new_image = Image.new(mode='RGB', size=(img_aux.size[0], img_aux.size[1]+50))
        # d1 = ImageDraw.Draw(new_image)
        # #pregunto por el ancho para saber si puedo poner o no todo el contenido
        # if size[0] > 120:
        #     font = ImageFont.truetype('/home/pedro/PycharmProjects/BabelComic-II/Extras/fonts/Comic Book.otf', 26)
        #     d1.text((10, 10), "{}/{}".format(10, 100), font=font,  fill=(200, 200, 200))
        #     font = ImageFont.truetype('/home/pedro/PycharmProjects/BabelComic-II/Extras/fonts/Comic Book.otf', 18)
        #     d1.text((size[0]-35, 10), "{}/{}".format(1, len(self.comicbooks_info_manager[str(index)].lista_covers)), font=font, fill=(200, 200, 200))
        #
        # # else:
        # #    d1.text((10, 20), "{}/{}".format(0, volumen.cantidad_numeros), font=font, fill=(200, 200, 200))
        #
        # new_image.paste(img_aux, (0, 50))
        # gdkpixbuff_thumnail = self.image2pixbuf(new_image)
        GLib.idle_add(self.update_cover,  index, image)


    def update_cover(self, index, image):
        size = (self.ancho_thumnail, int(image.size[1] * self.ancho_thumnail / image.size[0]))
        image.thumbnail(size, 3, 3)
        img_aux = image.copy()
        d1 = ImageDraw.Draw(img_aux)
        d1.rectangle([(0, 0), (size[0] - 1, size[1] - 1)], outline=(0, 0, 0), width=3)
        d1.rectangle([(0, 0), (size[0] - 1, size[1] - 1)], outline=(0, 0, 0), width=3)
        new_image = Image.new(mode='RGB', size=(img_aux.size[0], img_aux.size[1] + 50))
        d1 = ImageDraw.Draw(new_image)
        # pregunto por el ancho para saber si puedo poner o no todo el contenido
        if size[0] > 120:
            font = ImageFont.truetype('/home/pedro/PycharmProjects/BabelComic-II/Extras/fonts/Comic Book.otf', 26)
        d1.text((10, 10), "{}/{}".format(10, 100), font=font, fill=(200, 200, 200))
        font = ImageFont.truetype('/home/pedro/PycharmProjects/BabelComic-II/Extras/fonts/Comic Book.otf', 18)
        d1.text((size[0] - 35, 10), "{}/{}".format(self.comicbooks_info_manager[str(index)].index_lista_covers+1, len(self.comicbooks_info_manager[str(index)].lista_covers)),
                font=font, fill=(200, 200, 200))
        new_image.paste(img_aux, (0, 50))
        gdkpixbuff_thumnail = self.image2pixbuf(new_image)
        self.liststore[index][0] = gdkpixbuff_thumnail

    def activar_busqueda(self, widget, event):
        self.barra_busqueda.set_search_mode(True)
        self.volumen_search_entry.grab_focus()

    def entrada_teclado_barra_busqueda(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.barra_busqueda.set_search_mode(False)
            self.volumen_search_entry.set_text('')
            self.iconview_volumens.grab_focus()

    def evento_busqueda(self, event):
        self.manager.set_filtro(Volume.nombre.like('%{}%'.format(self.volumen_search_entry.get_text())))
        self.load_volumens()

if __name__ == "__main__":
    GLib.set_prgname('Babelcomics')
    bc = Comicbooks_info_gtk(volumen_id=91273)
    bc.window.connect("destroy", Gtk.main_quit)
    bc.window.show()
    bc.window.maximize()
    Gtk.main()