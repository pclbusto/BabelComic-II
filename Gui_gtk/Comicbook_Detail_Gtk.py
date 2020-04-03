import os
import Entidades.Init
from Entidades.Entitiy_managers import Commicbooks_detail, Comicbook_Detail, Commicbooks
import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
from bs4 import BeautifulSoup

class Comicbook_Detail_Gtk():
    # todo implementar los botones de limpiar, guardar y borrar

    def __init__(self,  session=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.comicbooks_detail_manager = Commicbooks_detail(session=self.session)
        self.comicbooks_manager = Commicbooks(session=self.session)

        self.handlers = {"seleccion_fila": self.seleccion_fila,
                         "click_marcar_como_cover": self.click_marcar_como_cover,
                         "click_marcar_como_page": self.click_marcar_como_page,
                         'click_derecho': self.click_derecho}

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

        self.comicbook = None
        self.labels = ["Página", "Cover"]
        print("Creacion de formulario exitosa")
        # inicializamos el modelo con rotulos del manager

    def click_marcar_como_cover(self, widget):
        self._marcar_como(widget, Comicbook_Detail.PAGE_TYPE_COVER)

    def click_marcar_como_page(self, widget):
        self._marcar_como(widget, Comicbook_Detail.PAGE_TYPE_COMMON_PAGE)

    def _marcar_como(self, widget, tipo):
        model, treeiter = self.tree_view_paginas.get_selection().get_selected()
        if treeiter is not None:
            self.comicbooks_detail_manager.set_page_type(model[treeiter][0], tipo)
            self.liststore_comicbook[model[treeiter][0]][3] = self.labels[tipo]
            if tipo == Comicbook_Detail.PAGE_TYPE_COVER:
                self.comicbooks_detail_manager.crear_thumnail_cover(True)
        self.menu_comic.popdown()

    def seleccion_fila(self, widget):
        #print(widget)
        model, treeiter = widget.get_selection().get_selected()
        if treeiter is not None:
            self.comicbook.goto(model[treeiter][0])
            #print("You selected", model[treeiter][0])
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
                print("insertando registro {}".format(elemento))
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

        # cb.getImagePage().show()

    def click_derecho(self, widget, event):
        # click derecho
        if event.button == 3:
            # print(self.tree_left.get_allocation().width)
            # print('mostrando menu')
            # help(event)
            # self.menu_comic.set_relative_to(None)
            rect = Gdk.Rectangle()
            rect.height=10
            rect.width= 10
            # print(event.x_root, event.y_root)
            # print(event.x,event.y)
            rect.x= int(event.x)
            rect.y = int(event.y)
            #rect.y = int(event.y + (event.y_root-event.y)-80)
            # print(self.iconview.get_item_at_pos(event.x_root, event.y_root))
            # print(self.iconview.get_item_at_pos(event.x, event.y)[1])
            # print(event.x_root,event.y_root)
            self.menu_comic.set_pointing_to(rect)
            self.menu_comic.set_position(3)
            self.menu_comic.set_relative_to(widget)
            # self.menu_comic.show_all()
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
            self.textbuffer.set_text(BeautifulSoup(comicbook_info.resumen).get_text("\n"))
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
    id = "6645"

    cbi = Comicbook_Detail_Gtk()
    cbi.window.connect("destroy", Gtk.main_quit)
    cbi.set_comicbook(id)
    cbi.window.show()

    Gtk.main()