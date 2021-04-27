import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GLib, GObject
from gi.repository import Gdk

import Entidades.Init
from Entidades.Agrupado_Entidades import Comicbook, Publisher, Volume, Comicbook_Info, Arcos_Argumentales_Comics_Reference, Comicbook_Detail
from Entidades.Agrupado_Entidades import Setup
from Entidades.Entitiy_managers import Comicbooks

from Gui_gtk.PublisherGuiGtk import Publisher_lookup_gtk
from Gui_gtk.VolumeGuiGtk import VolumeGuiGtk

from Gui_gtk.acerca_de_gtk import Acerca_de_gtk
from Gui_gtk.function_launcher_Gtk import Function_launcher_gtk
from Extras import BabelComics_Manager
import os.path
from PIL import ImageFont
from PIL import Image, ImageFile, ImageDraw
import threading, io
import json





class Comicbook_editor_gtk():

    CREANDO_GLOBO = 1
    GUARDANDO_COORDS = 2

    def __init__(self, session=None, lista_comics_id=None):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

        self.handlers = {'Guardar': self.Guardar,
                         'click_mouse': self.click_mouse,
                         'crear_globo': self.crear_globo,
                         'actualizar_imagen': self.actualizar_imagen,
                         'seleccion_arbol': self.seleccion_arbol,
                         'guardar_coordenadas': self.guardar_coordenadas,
                         'mover_texto': self.mover_texto,
                         'delete_nodo': self.delete_nodo}

        self.cataloged_pix = Pixbuf.new_from_file_at_size('../iconos/Cataloged.png', 32, 32)

        self.comicbooks_manager = Comicbooks(session=self.session, lista_comics_id=lista_comics_id)

        builder = Gtk.Builder()
        builder.add_from_file("../Glade_files/Comicbook_Editor.glade")
        builder.connect_signals(self.handlers)
        self.window = builder.get_object("Comicbook_editor")
        self.imagen_pagina = builder.get_object("imagen_pagina")
        self.spinner_pos_x_0 = builder.get_object("spinner_pos_x_0")
        self.spinner_pos_y_0 = builder.get_object("spinner_pos_y_0")
        self.spinner_pos_x_1 = builder.get_object("spinner_pos_x_1")
        self.spinner_pos_y_1 = builder.get_object("spinner_pos_y_1")
        self.arbol = builder.get_object('arbol')
        self.liststore_arbol = builder.get_object("liststore_arbol")
        self.entry_text = builder.get_object("entry_text")
        self.labels_coords = builder.get_object('labels_coords')

        self.event_box = builder.get_object("event_box")
        self.window.set_title("Editor")
        self.app_icon = Pixbuf.new_from_file_at_size('../iconos/iconoBabelComics-buuf.png', 32, 32)
        self.window.set_icon_from_file('../iconos/iconoBabelComics-buuf.png')
        self.window.set_default_icon_list([self.app_icon])
        self.comicbook = None
        self.last_id_used = 0
        self.diccionario_globos = {}
        self.current_node = 0

        #atributos para capturar y crear los globos de texto
        self.cantidad_clicks = 0
        self.modo = self.CREANDO_GLOBO
        self.lista_clicks = [0, 0, 0, 0]


        if lista_comics_id is not None:
            self.load_page(lista_comics_id[0])
        self.load_json_file()

    def delete_nodo(self, widget):
        model, treeiter = self.arbol.get_selection().get_selected()
        del(self.diccionario_globos[str(model[treeiter][0])])
        model.remove(treeiter)
        self._load_page_picture()

    def mover_texto(self, widget, event):
        print("moviendo {}".format(event.x))
        delta_x = 0
        delta_y = 0
        ancho_event_box = self.event_box.get_allocated_width()
        alto_event_box = self.event_box.get_allocated_height()
        ancho_page = self.comicbook.getImagePage().size[0]
        alto_page = self.comicbook.getImagePage().size[1]

        if ancho_page < ancho_event_box:
            delta_x = int((ancho_event_box - ancho_page) / 2)
        if alto_page < alto_event_box:
            delta_y = int((alto_event_box - alto_page) / 2)

        self.diccionario_globos[self.current_node]['texto']['coordenadas'] = [int(event.x - delta_x),
                                                                              int(event.y - delta_y)]
        self.load_node_data(self.current_node)
        self.actualizar_imagen(None)

    def seleccion_arbol(self, selection):
        model, treeiter = selection.get_selection().get_selected()
        if treeiter is not None:
            self.load_node_data(str(model[treeiter][0]))
        self._load_page_picture()

    def guardar_coordenadas(self, widget):
        self.modo = self.GUARDANDO_COORDS

    def load_node_data(self, index):
        self.current_node = index
        print(self.diccionario_globos[index])
        self.spinner_pos_x_0.set_value(self.diccionario_globos[index]['lista'][0])
        self.spinner_pos_y_0.set_value(self.diccionario_globos[index]['lista'][1])
        self.spinner_pos_x_1.set_value(self.diccionario_globos[index]['lista'][2])
        self.spinner_pos_y_1.set_value(self.diccionario_globos[index]['lista'][3])
        self.entry_text.set_text(self.diccionario_globos[str(index)]['texto']['esp'])
        coords = self.diccionario_globos[str(index)]['texto']['coordenadas']
        self.labels_coords.set_text('({},{})'.format(coords[0], coords[1]))

    def set_node_data(self, index):
        self.diccionario_globos[index]['lista'][0] = self.spinner_pos_x_0.get_value()
        self.diccionario_globos[index]['lista'][1] = self.spinner_pos_y_0.get_value()
        self.diccionario_globos[index]['lista'][2] = self.spinner_pos_x_1.get_value()
        self.diccionario_globos[index]['lista'][3] = self.spinner_pos_y_1.get_value()
        self.diccionario_globos[index]['texto']['esp'] = self.entry_text.get_text()

    def actualizar_imagen(self, widget):
        self.set_node_data(self.current_node)
        self._load_page_picture()

    def crear_globo(self, widget):
        self.cantidad_clicks = 0
        self.lista_clicks = [0, 0, 0, 0]
        self.modo = self.CREANDO_GLOBO
        self.liststore_arbol.append([self.get_next_id()])
        self.diccionario_globos[self.last_id_used] = {'lista': [0, 0, 0, 0], 'color': [255, 255, 255], 'texto': {'ing': '', 'esp': '', 'coordenadas': [0, 0]}}
        self.current_node = self.last_id_used

    def load_json_file(self):
        print('{}.json'.format(self.comicbook.id_comicbook))
        fp = open('{}.json'.format(self.comicbook.id_comicbook), 'r')
        self.diccionario_globos = json.loads(fp.read())
        fp.close()
        print(self.diccionario_globos)
        self.last_id_used = 0
        for key in self.diccionario_globos.keys():
            if self.last_id_used < int(key):
                self.last_id_used = int(key)

            self.liststore_arbol.append([int(key)])
        self._load_page_picture()


    def click_mouse(self, widget, event):
        print(event.x, event.y)
        ancho_event_box = self.event_box.get_allocated_width()
        alto_event_box = self.event_box.get_allocated_height()

        print(self.comicbook.getImagePage().size[0])
        ancho_page = self.comicbook.getImagePage().size[0]
        alto_page = self.comicbook.getImagePage().size[1]
        print(self.event_box.get_allocated_width())
        delta_x = 0
        delta_y = 0
        if ancho_page < ancho_event_box:
            delta_x = int((ancho_event_box - ancho_page) / 2)
        if alto_page < alto_event_box:
            delta_y = int((alto_event_box - alto_page)/2)

        if self.modo == self.CREANDO_GLOBO:
            if self.cantidad_clicks < 4:
                print(self.cantidad_clicks)
                if self.cantidad_clicks == 0:
                    self.lista_clicks[0] = int(event.x - delta_x)
                if self.cantidad_clicks == 1:
                    self.lista_clicks[1] = int(event.y - delta_y)
                if self.cantidad_clicks == 2:
                    self.lista_clicks[2] = int(event.x - delta_x)
                if self.cantidad_clicks == 3:
                    self.lista_clicks[3] = int(event.y - delta_y)
                    self.diccionario_globos[self.current_node]['lista'] = self.lista_clicks
                    self._load_page_picture()
                self.cantidad_clicks += 1
        if self.modo == self.GUARDANDO_COORDS:
            print(event.x, event.y)
            self.diccionario_globos[self.current_node]['texto']['coordenadas'] = [int(event.x - delta_x), int(event.y - delta_y)]
            self.load_node_data(self.current_node)
            self.actualizar_imagen(None)


    def get_next_id(self):
        self.last_id_used += 1
        return self.last_id_used

    def load_page(self, comicbook_id):
        self.comicbook = self.comicbooks_manager.get(comicbook_id)
        print(self.comicbook)

        self._load_page_picture()
        self.load_zip_file()

    def Guardar(self, widget):
        fp = open('{}.json'.format(self.comicbook.id_comicbook), 'w')

        json.dump(self.diccionario_globos, fp)

        fp.close()


    def _load_page_picture(self):
        self.comicbook.openCbFile()
        self.comicbook.goto(14)
        stream = self.comicbook.getImagePage()
        draw = ImageDraw.Draw(stream)
        for key in self.diccionario_globos.keys():
            print(key, self.current_node)
            if key == self.current_node:
                draw.ellipse(self.diccionario_globos[key]['lista'], width=10, outline=(55, 255, 255))
                print("iguales")
            else:
                draw.ellipse(self.diccionario_globos[key]['lista'], width=10, fill=(255, 255, 255))
            font = ImageFont.truetype('/home/pedro/PycharmProjects/BabelComic-II/Extras/fonts/Comic Book.otf', 26)
            coords = self.diccionario_globos[key]['texto']['coordenadas']
            draw.multiline_text((coords[0], coords[1]), self.diccionario_globos[key]['texto']['esp'], (0, 0, 0), font=font, spacing=-5, align='center', anchor='ls')

        self.imagen_pagina.set_from_pixbuf(self.image2pixbuf(stream))

    def image2pixbuf(self, im):
        """Convert Pillow image to GdkPixbuf"""
        data = im.tobytes()
        w, h = im.size
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                              False, 8, w, h, w * 3)
        return pix

    def create_thumnails(self):
        lista_archivos = self.comicbook.name_list()
        lista_nombre_archivos = [nombre_archivo for nombre_archivo in lista_archivos if
                                 nombre_archivo[-3:] in ['jpg', 'png']]
        for index, archivo_nombre in enumerate(lista_nombre_archivos):
            print(archivo_nombre)
            t = threading.Thread(name=archivo_nombre, args=(archivo_nombre, index,), target=self.create_thumnail)
            t.start()

    def load_zip_file(self):
        self.comicbook.openCbFile()
        lista_archivos = self.comicbook.name_list()
        lista_nombre_archivos = [nombre_archivo for nombre_archivo in lista_archivos if nombre_archivo[-3:] in ['jpg', 'png']]
        # self.create_grey_tumnails(len(lista_nombre_archivos))
        # t = threading.Thread(name='my_service', target=self.create_thumnails)
        # t.start()



if __name__ == "__main__":
    GLib.set_prgname('Editor')
    bc= Comicbook_editor_gtk(lista_comics_id=[249])
    bc.window.connect("destroy", Gtk.main_quit)
    bc.window.show()
    bc.window.maximize()
    Gtk.main()