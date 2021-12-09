import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GLib, GObject
from gi.repository import Gdk

import Entidades.Init
from Entidades.Agrupado_Entidades import Comicbook, Publisher, Volume, Comicbook_Info, Arcos_Argumentales_Comics_Reference, Comicbook_Detail
from Entidades.Agrupado_Entidades import Setup
from Entidades.Entitiy_managers import Volumens

from Gui_gtk.PublisherGuiGtk import Publisher_lookup_gtk
from Gui_gtk.VolumeGuiGtk import VolumeGuiGtk

from Gui_gtk.acerca_de_gtk import Acerca_de_gtk
from Gui_gtk.function_launcher_Gtk import Function_launcher_gtk
from Extras import BabelComics_Manager
import os.path
import math
from PIL import Image, ImageFile, ImageDraw
import threading, io
from PIL import ImageFont




class Volumens_gtk():

    def __init__(self, session=None):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

        self.load_setup()

        self.handlers = {'activar_busqueda': self.activar_busqueda,
                         'entrada_teclado_barra_busqueda': self.entrada_teclado_barra_busqueda,
                         'evento_busqueda': self.evento_busqueda,
                         'seleccion_volumen': self.seleccion_volumen,
                         'clicks': self.clicks}

        self.cataloged_pix = Pixbuf.new_from_file_at_size('../iconos/Cataloged.png', 32, 32)

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Volumens.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volumens")
        self.window.set_title("Series")
        self.app_icon = Pixbuf.new_from_file_at_size('../iconos/iconoBabelComics-buuf.png', 32, 32)
        self.window.set_icon_from_file('../iconos/iconoBabelComics-buuf.png')
        self.window.set_default_icon_list([self.app_icon])
        self.iconview_volumens = self.builder.get_object('iconview_volumens')
        self.barra_busqueda = self.builder.get_object('barra_busqueda')
        self.volumen_search_entry = self.builder.get_object('volumen_search_entry')
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
        self.manager = Volumens(session)
        self.dictionary = {}
        self.cantidad_thumnails_pendiente = 0
        #self.search_change(None)

        self.iconview_volumens.set_pixbuf_column(0)
        self.iconview_volumens.set_text_column(1)
        self.iconview_volumens.set_text_column(2)
        self.iconview_volumens.set_column_spacing(-1)
        self.iconview_volumens.set_item_padding(10)
        self.iconview_volumens.set_item_width(1)
        self.iconview_volumens.set_spacing(30)
        self.grey_cover = Image.new("RGB", (self.ancho_thumnail, int(self.ancho_thumnail*1.3)), (150, 150, 150))


        self.load_volumens()
        screen = Gdk.Screen.get_default()
        self.window.set_default_size(screen.width(), self.window.get_size()[1])

    def clicks(self, widget, event):
        print(event.get_click_count())
        if event.get_click_count().click_count == 2:
            selected_list = widget.get_selected_items()
            if len(selected_list) == 1:
                print("Nombre :", str(self.liststore[selected_list[0]][2]))
                volumen = VolumeGuiGtk()
                volumen.window.show_all()
                volumen.set_volumen_id(int(self.liststore[selected_list[0]][2]))

    def image2pixbuf(self, im):
        """Convert Pillow image to GdkPixbuf"""
        data = im.tobytes()
        w, h = im.size
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                              False, 8, w, h, w * 3)
        return pix

    def create_grey_tumnails(self, lista):


        for i in range(0, len(lista)):
            img_aux = self.grey_cover.copy()
            d1 = ImageDraw.Draw(img_aux)
            d1.text(((self.ancho_thumnail/2)-20, self.ancho_thumnail/2), str(i),  fill=(255, 255, 255))
            d1.polygon([(0, 0), (self.ancho_thumnail, 0), (self.ancho_thumnail, self.ancho_thumnail*2), (0, self.ancho_thumnail*2)], outline=(0, 0, 0))
            gdkpixbuff_thumnail = self.image2pixbuf(img_aux)
            #self.dictionary[str(i)] = ''
            GLib.idle_add(self.update_progess2, gdkpixbuff_thumnail, lista[i].nombre, lista[i].id_volume)

    def update_progess2(self, gdkpixbuff_thumnail, archivo_nombre, id_volume):
        self.liststore.append([gdkpixbuff_thumnail, archivo_nombre, id_volume])


    def load_setup(self):
        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + "coverIssuesThumbnails" + os.path.sep
        self.ancho_thumnail = self.session.query(Setup).first().anchoThumnail

    def load_volumens(self):
        self.liststore.clear()
        lista = self.manager.getList()
        #calcular las cantidades
        self.manager.get_cantidad_comics_asociados_a_volumenes()

        self.create_grey_tumnails(lista)
        threading.Thread(target=self.load_volumens_second_part, args=(lista,)).start()

    def load_volumens_second_part(self, lista):
        for index, volumen in enumerate(lista):
            threading.Thread(target=self.load_volumen_cover, args=(volumen, index,)).start()



    def seleccion_volumen(self, widget):
        selected_list = widget.get_selected_items()
        if len(selected_list) == 1:
            print("Nombre :", str(self.liststore[selected_list[0]][2]))

    def load_volumen_cover(self, volumen, index):
        try:
            image = Image.open(volumen.getImagePath()).convert("RGB")
        except:
            print("imagen de cover volumen {} {}".format(volumen.id_volume, volumen.getImagePath()))
            return
        size = (self.ancho_thumnail, int(image.size[1] * self.ancho_thumnail / image.size[0]))
        image.thumbnail(size, 3, 3)
        img_aux = image.copy()
        d1 = ImageDraw.Draw(img_aux)
        d1.rectangle([(0, 0), (size[0] - 1, size[1] - 1)], outline=(0, 0, 0), width=3)
        d1.rectangle([(0, 0), (size[0] - 1, size[1] - 1)], outline=(0, 0, 0), width=3)
        new_image = Image.new(mode='RGB', size=(img_aux.size[0], img_aux.size[1]+50))
        # new_image = Image.new(mode='RGB', size=(image.size[0], image.size[1]+50))
        d1 = ImageDraw.Draw(new_image)
        font = ImageFont.truetype('/home/pedro/PycharmProjects/BabelComic-II/Extras/fonts/Comic Book.otf', 26)
        if str(volumen.id_volume) in self.manager.cantidades_por_volumen.keys():
            d1.text((10, 20), "{}/{}".format(self.manager.cantidades_por_volumen[str(volumen.id_volume)][1], self.manager.cantidades_por_volumen[str(volumen.id_volume)][0]), font=font, fill=(200, 200, 200))
        else:
            d1.text((10, 20), "{}/{}".format(0, volumen.cantidad_numeros), font=font, fill=(200, 200, 200))

        new_image.paste(img_aux, (0, 50))
        # new_image.paste(image, (0, 50))
        gdkpixbuff_thumnail = self.image2pixbuf(new_image)
        GLib.idle_add(self.update_cover, gdkpixbuff_thumnail, index)

    def update_cover(self, pixbuf, index):
        self.liststore[index][0] = pixbuf

    def activar_busqueda(self, widget, event):
        self.barra_busqueda.set_search_mode(True)
        self.volumen_search_entry.grab_focus()

    def entrada_teclado_barra_busqueda(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.barra_busqueda.set_search_mode(False)
            self.volumen_search_entry.set_text('')
            self.iconview_volumens.grab_focus()

    def do_search(self):
        self.manager.set_filtro(Volume.nombre.like('%{}%'.format(self.volumen_search_entry.get_text())))
        self.load_volumens()

    def evento_busqueda(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self.do_search()


if __name__ == "__main__":
    GLib.set_prgname('Babelcomics')
    bc = Volumens_gtk()
    bc.window.connect("destroy", Gtk.main_quit)
    bc.window.show()
    bc.window.maximize()
    Gtk.main()