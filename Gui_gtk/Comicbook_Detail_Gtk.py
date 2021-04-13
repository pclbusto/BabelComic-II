import os
import Entidades.Init
from Entidades.Entitiy_managers import Commicbooks_detail, Comicbook_Detail, Comicbooks, Comicbook
import datetime
from PIL import Image, ImageDraw

import threading, io


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib

class Comicbook_Detail_Gtk():
    # todo implementar los botones de limpiar, guardar y borrar

    def __init__(self,  session=None, lista_comics_id=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.comicbooks_detail_manager = Commicbooks_detail(session=self.session)
        self.comicbooks_manager = Comicbooks(session=self.session, lista_comics_id=lista_comics_id)

        self.handlers = {"seleccion_fila": self.seleccion_fila,
                         "click_marcar_como_cover": self.click_marcar_como_cover,
                         "click_marcar_como_page": self.click_marcar_como_page,
                         'click_derecho': self.click_derecho,
                         'pop_up_menu': self.pop_up_menu,
                         'get_first': self.get_first,
                         'get_prev': self.get_prev,
                         'get_next': self.get_next,
                         'get_last': self.get_last,
                         }

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Comicbook_Detail_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comicbook_Detail")
        self.imagen_pagina = self.builder.get_object("imagen_pagina")
        self.liststore_comicbook = self.builder.get_object("liststore_comicbook")
        self.entry_id_comicbook = self.builder.get_object("entry_id_comicbook")
        self.entry_id_comicbook_info = self.builder.get_object("entry_id_comicbook_info")
        self.entry_path = self.builder.get_object("entry_path")
        self.menu_comic = self.builder.get_object("menu_comic")
        self.tree_view_paginas = self.builder.get_object("tree_view_paginas")
        self.menu_principal = self.builder.get_object('menu_principal')
        self.stack = self.builder.get_object('stack')
        self.iconview = self.builder.get_object("iconview_paginas")
        self.liststore1 = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        self.iconview.set_model(self.liststore1)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.set_text_column(2)
        self.iconview.set_column_spacing(-1)
        self.iconview.set_item_padding(10)
        self.iconview.set_item_width(1)
        self.iconview.set_spacing(30)
        self.thumnail_height = 80
        self.dictionary = {}


        self.comicbook = None
        self.labels = ["Página", "Cover"]
        print("Creacion de formulario exitosa")
        # inicializamos el modelo con rotulos del manager

    def set_filter(self, cadena):
        self.comicbooks_manager.set_filtro(Comicbook.path.like("%{}%".format(cadena)))

    def get_first(self, widget):
        comicbook = self.comicbooks_manager.getFirst()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        print('------------------------------------------------')
        print(comicbook)
        self.set_comicbook(comicbook.id_comicbook)

    def get_next(self, widget):
        comicbook = self.comicbooks_manager.getNext()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT   )
        self.set_comicbook(comicbook.id_comicbook)

    def get_prev(self, widget):
        comicbook = self.comicbooks_manager.getPrev()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT  )
        self.set_comicbook(comicbook.id_comicbook)

    def get_last(self, widget):
        comicbook = self.comicbooks_manager.getLast()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self.set_comicbook(comicbook.id_comicbook)

    def pop_up_menu(self, widget):
        self.menu_principal.show_all()

    def click_marcar_como_cover(self, widget):
        self._marcar_como(widget, Comicbook_Detail.PAGE_TYPE_COVER)

    def click_marcar_como_page(self, widget):
        self._marcar_como(widget, Comicbook_Detail.PAGE_TYPE_COMMON_PAGE)

    def _marcar_como(self, widget, tipo):
        # model, treeiter = self.tree_view_paginas.get_selection().get_selected()
        # if treeiter is not None:
        #     self.comicbooks_detail_manager.set_page_type(model[treeiter][0], tipo)
        #     self.liststore_comicbook[model[treeiter][0]][3] = self.labels[tipo]
        #     if tipo == Comicbook_Detail.PAGE_TYPE_COVER:
        #         self.comicbooks_detail_manager.crear_thumnail_cover(True)
        selected_list = self.iconview.get_selected_items()
        if len(selected_list) == 1:
            print(selected_list)
            index = selected_list[0].get_indices()[0]
            self.comicbook.goto(index)
            self.comicbooks_detail_manager.set_page_type(index, tipo)
            #self.liststore_comicbook[model[treeiter][0]][3] = self.labels[tipo]
            if tipo == Comicbook_Detail.PAGE_TYPE_COVER:
                self.comicbooks_detail_manager.crear_thumnail_cover(True)
        self.menu_comic.popdown()

    def seleccion_fila(self, widget):
        #print(widget)
        #model, treeiter = widget.get_selection().get_selected()
        #if treeiter is not None:
            # self.comicbook.goto(model[treeiter][0])
            # #print("You selected", model[treeiter][0])
        selected_list = widget.get_selected_items()
        # print(selected_list[0])
        if len(selected_list) == 1:
            print("Nombre :", self.dictionary[str(selected_list[0].get_indices()[0])])
            self.comicbook.goto_page_by_name(self.dictionary[str(selected_list[0].get_indices()[0])])
            # self.comicbook.goto(selected_list[0].get_indices()[0])
        self._load_page_picture()



    def _load_page_picture(self):
        stream = self.comicbook.get_image_page_gtk()
        #print(stream)
        ancho = (500.0 / stream.get_width())
        self.imagen_pagina.set_from_pixbuf(
            #vamos a mostrar las paginas en el mismo tamaño
            stream.scale_simple(int(stream.get_width() * ancho), int(stream.get_height() * ancho), 1))

    def set_comicbook(self, comicbook_id):
        self.comicbook = self.comicbooks_manager.get(comicbook_id)
        self.entry_id_comicbook.set_text(str(self.comicbook.id_comicbook))
        self.entry_id_comicbook_info.set_text(self.comicbook.id_comicbook_info)
        self.entry_path.set_text(self.comicbook.path)

        tiene_detalle = self.comicbooks_manager.tiene_detalle()
        lista_paginas = []
        self.comicbooks_detail_manager.set_comicbook(comicbook_id)
        if tiene_detalle:
            self.comicbooks_detail_manager.set_filtro(Comicbook_Detail.comicbook_id == comicbook_id)
            lista_paginas = self.comicbooks_detail_manager.getList()
        self.comicbook.openCbFile()
        self._load_page_picture()
        cantidad_paginas = self.comicbook.getCantidadPaginas()
        self.liststore_comicbook.clear()
        if not tiene_detalle:
            cbdtl = Commicbooks_detail()
            for elemento in range(0, cantidad_paginas):
                cbdtl.new_record()
                cbdtl.entidad.comicbook_id = comicbook_id
                cbdtl.entidad.indicePagina = elemento
                cbdtl.entidad.ordenPagina = elemento
                cbdtl.entidad.tipoPagina = 0
                cbdtl.save()
                self.liststore_comicbook.append([elemento, "pagina {}".format(elemento), 0, 'Página'])
        else:
            for elemento in lista_paginas:
                self.liststore_comicbook.append([elemento.ordenPagina, "pagina {}".format(elemento.ordenPagina), 0, self.labels[elemento.tipoPagina]])
        self.load_zip_file()

    def image2pixbuf(self, im):
        """Convert Pillow image to GdkPixbuf"""
        data = im.tobytes()
        w, h = im.size
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                              False, 8, w, h, w * 3)
        return pix


    def create_thumnail(self, archivo_nombre, index):
        #archivo_nombre: es el nombre del archivo dentro del zip
        data = self.comicbook.cbFile.read(archivo_nombre)
        image = Image.open(io.BytesIO(data)).convert("RGB")
        size = (self.thumnail_height, int(image.size[1] * self.thumnail_height / image.size[0]))
        image.thumbnail(size, 3, 3)
        img_aux = image.copy()
        d1 = ImageDraw.Draw(img_aux)
        d1.polygon([(0, 0), (size[0]-1, 0), (size[0]-1, size[1]-1), (0, size[1]-1)], outline=(0, 0, 0))

        gdkpixbuff_thumnail = self.image2pixbuf(img_aux)

        GLib.idle_add(self.update_progess, gdkpixbuff_thumnail, index, archivo_nombre)


    def update_progess(self, gdkpixbuff_thumnail, index, nombre_archivo):

        self.liststore1[index][0] = gdkpixbuff_thumnail
        self.liststore1[index][2] = nombre_archivo
        self.dictionary[str(index)] = nombre_archivo

    def update_progess2(self, gdkpixbuff_thumnail, archivo_nombre):
        self.liststore1.append([gdkpixbuff_thumnail, archivo_nombre, archivo_nombre])

    def create_grey_tumnails(self, cantidad):
        img = Image.new("RGB", (self.thumnail_height, self.thumnail_height*2), (150, 150, 150))
        for i in range(0, cantidad):
            img_aux = img.copy()
            d1 = ImageDraw.Draw(img_aux)
            d1.text(((self.thumnail_height/2)-20, self.thumnail_height/2), str(i),  fill=(255, 255, 255))
            d1.polygon([(0, 0), (self.thumnail_height, 0), (self.thumnail_height, self.thumnail_height*2), (0, self.thumnail_height*2)], outline=(0, 0, 0))
            gdkpixbuff_thumnail = self.image2pixbuf(img_aux)
            self.dictionary[str(i)] = ''
            GLib.idle_add(self.update_progess2, gdkpixbuff_thumnail, str(i))

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
        self.create_grey_tumnails(len(lista_nombre_archivos))
        t = threading.Thread(name='my_service', target=self.create_thumnails)
        t.start()

    def click_derecho(self, widget, event):
        if event.button == 3:
            rect = Gdk.Rectangle()
            rect.height = 10
            rect.width = 10
            rect.x = int(event.x)
            #por bug o funciona asi pero el click en iconview trae las coordenadas sin tener en cuenta que es una scroll
            #como resultado si no ajustamos se correr el popup
            rect.y = int(event.y-self.iconview.get_vadjustment().get_value())
            # print(event.x_root,event.y_root)
            self.menu_comic.set_pointing_to(rect)
            self.menu_comic.set_position(3)
            self.menu_comic.set_relative_to(widget)
            self.menu_comic.popup()

    def change_cover(self, widget):
        print("change_cover")
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:
            model = widget.get_model()
            index = widget.get_active()
            print("change_cover INDEX {}".format(widget.get_active()))
            self.comicbooks_detail_manager_manager.index_lista_covers = index
            self._load_cover()
        else:
            entry = widget.get_child()
            print("Entered: %s" % entry.get_text())


    def _copy_to_window(self, comicbook_info):
        print(comicbook_info)
        #self.clearWindow()
        if comicbook_info is not None:
            self.entry_orden.set_text(str(comicbook_info.orden))
            self.entry_numero.set_text(str(comicbook_info.numero))
            self.entry_titulo.set_text(comicbook_info.titulo)
            if comicbook_info.fecha_tapa>0:
                self.label_fecha_tapa.set_text(datetime.date.fromordinal(comicbook_info.fecha_tapa).strftime("%d/%m/%Y"))
            else:
                self.label_fecha_tapa.set_text(
                    datetime.date.fromordinal(1).strftime("%d/%m/%Y"))
            self.entry_api_url.set_text(comicbook_info.api_detail_url)
            self.entry_url.set_text(comicbook_info.url)
            self.scale_raiting.get_adjustment().set_value(comicbook_info.rating)
            self.textbuffer.set_text(comicbook_info.resumen)
            #print("self.comicbooks_manager.index_lista_covers {}".format(self.comicbooks_manager.index_lista_covers))
            self.combo_paginas.set_active(self.comicbooks_manager.index_lista_covers)
            self._load_cover()
            listore = Gtk.ListStore(int)
            for index, cover_nro in enumerate(self.comicbooks_manager.lista_covers):
                listore.append([index])
            self.combo_paginas.set_model(listore)

    def _load_cover_background(self):
        nombreThumnail = self.comicbooks_manager._get_cover_complete_path()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=nombreThumnail,
            width=150,
            height=250,
            preserve_aspect_ratio=True)
        self.cover_comic.set_from_pixbuf(pixbuf)

    def _load_cover(self):

        self._load_cover_background()

    def copy_from_window_to_entity(self):
        self.comicbooks_manager.entidad.orden = self.entry_orden.get_text()
        self.comicbooks_manager.entidad.numero = self.entry_numero.get_text()
        self.comicbooks_manager.entidad.titulo = self.entry_titulo.get_text()
        # este campo lo tenemos actualizaco cada vez que se selecciona un valor de calendario
        # self.comicbooks_manager.entidad.fecha_tapa
        self.comicbooks_manager.entidad.rating = self.scale_raiting.get_adjustment().get_value()
        #self.volumens_manager.entidad.image_url = self.entry_url_cover.get_text()
        #self.volumens_manager.entidad.anio_inicio = self.entry_anio_inicio.get_text()
        #self.volumens_manager.entidad.cantidad_numeros = self.entry_cantidad_numeros.get_text()

    def click_limpiar(self, widget):
        print("dsldsa")
        self.entry_url.clear()
        # self.entradaNombre.delete(0, END)
        # self.entradaUrl.delete(0, END)
        # self.textoDescripcion.config(text='')


if __name__ == "__main__":
    id = "48847"

    cbi = Comicbook_Detail_Gtk()
    cbi.window.connect("destroy", Gtk.main_quit)
    cbi.set_comicbook(id)
    cbi.window.show()

    Gtk.main()