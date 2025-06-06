import shutil

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GLib, GObject
from gi.repository import Gdk
import Entidades.Init
from Entidades.Agrupado_Entidades import Comicbook, Publisher, Volume, Comicbook_Info, Arcos_Argumentales_Comics_Reference, Comicbook_Detail
from Entidades.Agrupado_Entidades import Setup
from Gui_gtk.ScannerGtk import ScannerGtk
from Gui_gtk.PublisherGuiGtk import PublisherGtk
from Gui_gtk.VolumeGuiGtk import VolumeGuiGtk
from Gui_gtk.VolumensGuiGtk import Volumens_gtk
#lo usamos para reutilizar la generacion de thumnails
from Entidades.Entitiy_managers import Commicbooks_detail
from Entidades.Entitiy_managers import Volumens

from Gui_gtk.Comicbook_Detail_Gtk import Comicbook_Detail_Gtk
from Gui_gtk.Comic_vine_cataloger_gtk import Comic_vine_cataloger_gtk
from Gui_gtk.config_gtk import Config_gtk
from Gui_gtk.acerca_de_gtk import Acerca_de_gtk
from Gui_gtk.function_launcher_Gtk import Function_launcher_gtk
from Extras import BabelComics_Manager
import os.path
import math
from PIL import Image, ImageFile
from rarfile import NotRarFile, BadRarFile
import threading, subprocess
from Entidades.Entitiy_managers import Comicbooks


icons = ["edit-cut", "edit-paste", "edit-copy"]

class BabelComics_main_gtk():
    BASE_KEY = "github.com.BabelComics"
    # todo el panel izquiero que tiene el arbol. hay que implementarlo completo. No tiene ni eventos.
    # todo que tengan iconos las ventanas.
    # todo implementar ventana de datos comics
    def __init__(self):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        self.session = Entidades.Init.Session()
        self.settings = Gio.Settings.new(self.BASE_KEY)

        self.listaEditoriales = self.session.query(Publisher).all()

        self.load_setup()

        self.handlers = {'click_editorial': self.click_editorial, 'click_boton_serie': self.click_boton_serie,
                         'item_seleccionado': self.item_seleccionado, 'click_derecho': self.click_derecho,
                         'click_boton_refresh': self.click_boton_refresh, 'click_catalogar': self.click_catalogar,
                         'click_boton_open_scanear': self.click_boton_open_scanear,
                         'click_boton_catalogar': self.click_boton_catalogar,
                         'click_boton_configurar_comicbook': self.click_boton_configurar_comicbook,
                         'click_boton_config': self.click_boton_config,
                         'click_boton_buscar': self.click_boton_buscar,
                         'search_change': self.search_change,
                         'search_change_panel_filtro': self.search_change_panel_filtro,
                         'atajos_teclado': self.atajos_teclado,
                         'evento_cierre': self.evento_cierre,
                         'click_primero': self.click_primero,
                         'click_anterior': self.click_anterior,
                         'click_siguiente': self.click_siguiente,
                         'click_ultimo': self.click_ultimo,
                         'cambio_pagina': self.cambio_pagina,
                         'seleccion_item_view': self.seleccion_item_view,
                         'click_boton_comic_info': self.click_boton_comic_info,
                         'click_boton_acerca_de': self.click_boton_acerca_de,
                         'click_next_view': self.click_next_view,
                         'click_prev_view': self.click_prev_view,
                         'marca_filtro': self.marca_filtro,
                         'lanzador_funciones': self.lanzador_funciones,
                         'pop_up_menu': self.pop_up_menu,
                         'enviar_papelera': self.enviar_papelera,
                         'click_restaurar': self.click_restaurar,
                         'click_derecho_panel_izquierdo': self.click_derecho_panel_izquierdo,
                         'click_boton_abrir_menu_panel_izquierdo': self.click_boton_abrir_menu_panel_izquierdo,
                         'doble_click_panel_izquierdo': self.doble_click_panel_izquierdo,
                         'click_abrir_nautilus': self.click_abrir_nautilus,
                         'search_entry_change': self.search_entry_change,
                         'guardar_settings': self.guardar_settings,
                         'comic_iconview_keypress': self.comic_iconview_keypress,
                         'click_exportar_a': self.click_exportar_a,
                         'click_organizar_Volumen': self.click_organizar_Volumen,
                         'click_borrar_comics_de_papelera':self.click_borrar_comics_de_papelera
                         }

        self.cataloged_pix = Pixbuf.new_from_file_at_size('../iconos/Cataloged.png', 32, 32)
        #self.cataloged_pix = Pixbuf.new_from_file_at_size('/home/pclbusto/PycharmProjects/BabelComic-II/iconos/Cataloged.png', 32, 32)


        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/BabelComic_main_gtk-II.glade")
        self.builder.connect_signals(self.handlers)
        self.menu = self.builder.get_object("popovermenu")
        self.window = self.builder.get_object("BabelComics_main_gtk")
        self.app_icon = Pixbuf.new_from_file_at_size('../iconos/iconoBabelComics-buuf.png', 32, 32)
        #Gtk.Windowset_default_icon_list([self.app_icon])
        self.window.set_icon_from_file('../iconos/iconoBabelComics-buuf.png')
        #self.window.set_icon_from_file('/home/pclbusto/PycharmProjects/BabelComic-II/iconos/BabelComic.png')
        self.window.set_default_icon_list([self.app_icon])
        self.boton_refresh= self.builder.get_object('boton_refresh')
        self.iconview = self.builder.get_object('iconview')
        self.search_entry_filtro_comics = self.builder.get_object('search_entry_filtro_comics')
        self.tree_left = self.builder.get_object("tree_left")
        self.gtk_tree_view_publisher = self.builder.get_object('tree_general')
        self.menu_comic = self.builder.get_object("menu_comic")
        self.search_bar_general = self.builder.get_object("search_bar_general")
        self.search_entry_filtro_general = self.builder.get_object("search_entry_filtro_general")
        self.search_bar_comics = self.builder.get_object("search_bar_comics")
        self.search_entry_filtro_comics = self.builder.get_object("search_entry_filtro_comics")
        self.cbx_text_paginas = self.builder.get_object("cbx_text_paginas")
        self.none_radio = self.builder.get_object("none_radio")
        self.selected_radio = self.builder.get_object("selected_radio")
        self.all_radio = self.builder.get_object("all_radio")
        self.popovermenu = self.builder.get_object("popovermenu")
        self.label_contadores = self.builder.get_object("label_contadores")
        self.label_pagina_filtros = self.builder.get_object("label_pagina_filtros")
        self.list_navegacion = self.builder.get_object("list_navegacion")
        self.mostrar_papelera = self.builder.get_object("mostrar_papelera")
        self.menu_panel_izquierdo = self.builder.get_object("menu_panel_izquierdo")
        self.panel_izquierdo = self.builder.get_object("panel_izquierdo")

        self.thread_creacion_thumnails = None

        self.list_navegacion = self.builder.get_object('list_navegacion')
        self.list_navegacion.clear()
        self.lista_comics_esperando_por_thumnail=[]
        self.updating_gui = False
        self.salir_thread = False
        #for editorial in self.listaEditoriales:
         #   self.list_navegacion.append([editorial.name, 0])

        self.liststore = Gtk.ListStore(Pixbuf, str, int)
        self.lista_pendientes = []
        self.filtro =   ''
        self.limit = self.session.query(Setup).first().cantidadComicsPorPagina
        self.offset = 0
        self.query = None
        self.manager = BabelComics_Manager.BabelComics_Manager()

        self.cantidad_thumnails_pendiente=0
        self.do_search()

        self.iconview.set_column_spacing(-1)
        self.iconview.set_item_padding(10)
        self.iconview.set_item_width(1)
        self.iconview.set_spacing(30)
        self.update_panel_filtros()
        self.panel_izquierdo.set_position(self.settings.get_int("position-handle"))

        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-theme-name", "Adwaita")
        settings.set_property("gtk-application-prefer-dark-theme",
                              True)  # if you want use dark theme, set second arg to True
        # print(settings.get_property("gtk-theme-name"))
        # for i in settings.list_properties():
        #     print(i)
    def guardar_settings(self, widget):

        self.settings.set_int("position-handle", self.panel_izquierdo.get_position())

    def click_abrir_nautilus(self, widget):
        comic = self.get_id_comics_from_selection()[0]
        # comic_manager = Comicbooks(self.session)
        # comic_manager.get(comic_id)
        print(comic.path[:comic.path.rfind('/')])
        subprocess.Popen(['xdg-open', comic.path[:comic.path.rfind('/')]])
        self.popovermenu.popdown()
        self.menu_comic.popdown()

    def click_exportar_a(self, widget):
        comics = self.get_id_comics_from_selection()
        for comic in comics:
            shutil.copyfile(comic.path, "/home/pedro/test/"+comic.getNombreArchivo(conExtension=True))
        # self.manager.enviar_quitar_papelera(comics, True)
        self.menu_comic.popdown()
        self.update_imagen_papelera()
        self.click_boton_refresh(None)

    def click_borrar_comics_de_papelera(self,widget):
        lista_comics = self.get_id_comics_from_selection()
        # todo implementar dialogo que pregunte si esta seguro de borrar estos archivos de forma definitiva
        self.menu_comic.popdown()
        comics = Comicbooks()
        comics.borrar_comics_de_papelera(lista_comics=lista_comics)
        self.update_imagen_papelera()
        self.click_boton_refresh(None)

    def click_organizar_Volumen(self, widget):
        select = self.gtk_tree_view_publisher.get_selection()
        model, treeiter = select.get_selected()
        volumenes = Volumens(session=self.session)
        volumenes.get(model[treeiter][2])
        volumenes.normalizar_comics_vinculados()
        self.menu_comic.popdown()

    def load_setup(self):
        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                            "coverIssuesThumbnails" + os.path.sep
        self.ancho_thumnail = self.session.query(Setup).first().anchoThumnail

    def update_imagen_papelera(self):
        pass
        # if self.manager.hay_comics_en_papelera():
        #     self.imagen_papelera.set_from_file("../iconos/Trash-Full-icon.png")
        # else:
        #     self.imagen_papelera.set_from_file("../iconos/Trash-Empty-icon.png")

    def doble_click_panel_izquierdo(self, widget , event, doble):
        select = self.gtk_tree_view_publisher.get_selection()
        model, treeiter = select.get_selected()
        if treeiter is not None:
            if self.manager.seccion_activa == 0:
                editorial = PublisherGtk(self.session)
                editorial.window.show()
                editorial.goto(model[treeiter][2])

            if self.manager.seccion_activa == 1:
                serie = VolumeGuiGtk(self.session)
                serie.window.show()
                self.popovermenu.popdown()
                serie.goto(model[treeiter][2])

            if self.manager.seccion_activa == 2:
                print("Arco Argumental")


    def click_boton_abrir_menu_panel_izquierdo(self, widget):
        select = self.gtk_tree_view_publisher.get_selection()
        model, treeiter = select.get_selected()
        if treeiter is not None:
            if self.manager.seccion_activa == 0:
                editorial = PublisherGtk(self.session)
                editorial.window.show()
                editorial.goto(model[treeiter][2])

            if self.manager.seccion_activa == 1:
                serie = VolumeGuiGtk(self.session)
                serie.window.show()
                self.popovermenu.popdown()
                serie.goto(model[treeiter][2])

            if self.manager.seccion_activa == 2:
                print("Arco Argumental")

        self.menu_panel_izquierdo.popdown()
            #print("You selected", model[treeiter][2])

    def enviar_papelera(self, widget):
        comics = self.get_id_comics_from_selection()
        self.manager.enviar_quitar_papelera(comics, True)
        self.menu_comic.popdown()
        self.update_imagen_papelera()
        self.click_boton_refresh(None)

    def click_restaurar(self, widget):
        comics = self.get_id_comics_from_selection()
        self.manager.enviar_quitar_papelera(comics, False)
        self.menu_comic.popdown()
        self.update_imagen_papelera()
        self.click_boton_refresh(None)

    def pop_up_menu(self,widget):
        # self.popover.set_relative_to(button)
        self.menu.show_all()
        self.menu.popup()

    def lanzador_funciones(self, widget, args):
        print("lanzador de funciones")

    def marca_filtro(self, widget, args):
        self.manager.marcar_para_filtrar(self.list_navegacion[args][2])
        if self.list_navegacion[args][1] == 1:
            self.list_navegacion[args][1] = 0
        else:
            self.list_navegacion[args][1] = 1

        self.do_search()

    def click_next_view(self, widget):
        self.manager.next_seccion()
        self.label_pagina_filtros.set_text(self.manager.get_titulo_actual())
        self.update_panel_filtros()

    def click_prev_view(self, widget):
        self.manager.prev_seccion()
        self.label_pagina_filtros.set_text(self.manager.get_titulo_actual())
        self.update_panel_filtros()

    def click_boton_comic_info(self, widget):
        self.manager.prev_seccion()
        self.label_pagina_filtros.set_text(self.manager.get_titulo_actual())


    def update_panel_filtros(self):
        lista = self.manager.get_lista_actual()
        self.list_navegacion.clear()
        for entidad in lista:
            self.list_navegacion.append([entidad[0], entidad[1], entidad[2]])


    def seleccion_item_view(self, event):

        self.label_contadores.set_text("{}/{}".format(len(self.iconview.get_selected_items()), len(self.listaComics)))
    def cambio_pagina(self,event):
        index = self.cbx_text_paginas.get_active()
        self.offset = index*self.limit
        self.loadAndCreateThumbnails()

    def click_primero(self,event):
        self.cbx_text_paginas.set_active(0)
        # self.loadAndCreateThumbnails()

    def click_anterior(self,event):
        if self.cbx_text_paginas.get_active() > 0:
            self.cbx_text_paginas.set_active(self.cbx_text_paginas.get_active()-1)

    def click_siguiente(self, event):
        if self.cbx_text_paginas.get_active() < len(self.cbx_text_paginas.get_model())-1:
            self.cbx_text_paginas.set_active(self.cbx_text_paginas.get_active() + 1)

    def click_ultimo(self,event):
        self.cbx_text_paginas.set_active(len(self.cbx_text_paginas.get_model())-1)

    def evento_cierre(self,event):
        print("hola")


    def comic_iconview_keypress(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            print("ABRIR LECTOR")

    def atajos_teclado(self, widget, event):


        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        print(ctrl)
        print(event.state)
        # if ctrl and event.keyval == Gdk.KEY_f:
        if event.keyval == Gdk.KEY_f:
            print(self.search_bar_general.get_search_mode())
            self.search_bar_general.set_search_mode(not self.search_bar_general.get_search_mode())
            if self.search_bar_general.get_search_mode():
                self.search_entry_filtro_general.grab_focus()
        if ctrl and event.keyval == Gdk.KEY_g:
            self.search_bar_comics.set_search_mode(not self.search_bar_comics.get_search_mode())
            if self.search_bar_comics.get_search_mode():
                self.search_entry_filtro_comics.grab_focus()
        if ctrl and event.keyval == Gdk.KEY_q:
            self.click_editorial(None)
        if ctrl and event.keyval == Gdk.KEY_w:
            self.click_boton_serie(None)
        if ctrl and event.keyval == Gdk.KEY_e:
            self.click_boton_catalogar(None)
        if event.keyval == Gdk.KEY_F5:
            self.click_boton_refresh(None)
        if ctrl and event.keyval == Gdk.KEY_s:
            self.click_boton_open_scanear(None)
        if ctrl and event.keyval == Gdk.KEY_d:
            self.click_boton_config(None)
        if event.keyval == Gdk.KEY_F1:
            fl = Function_launcher_gtk(self)
            fl.window.show()
        if event.keyval == Gdk.KEY_F2:
            self.click_catalogar(None)
        if event.keyval == Gdk.KEY_Delete:
            self.enviar_papelera(None)

    def click_boton_buscar(self, event):
        self.search_bar.set_search_mode(not self.search_bar.get_search_mode())
        if self.search_bar.get_search_mode():
            self.search_entry_filtro_comics.grab_focus()

    def search_change_panel_filtro(self, widget):
        print("Cambiando filtro")
        self.manager.set_filtro(self.search_entry_filtro_general.get_text())
        self.update_panel_filtros()

    def search_entry_change(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self.do_search()

    def search_change(self, widget):
        self.do_search()

    def do_search(self):

        self.menu_comic = self.builder.get_object("menu_comic")
        self.filtro = self.search_entry_filtro_comics.get_text()

        lista_editoriales = [editorial[2] for editorial in self.manager.lista_editoriales if editorial[1] == 1]
        lista_volumen = [volumen[2] for volumen in self.manager.lista_volumenes if volumen[1] == 1]
        lista_arcos = [arcos[2] for arcos in self.manager.lista_arcos_argumentales if arcos[1] == 1]
        # print('AAARCCCOOOOSS')

        # print(lista_arcos)
        print("MOSTRAMOS: {}".format(self.mostrar_papelera.get_active()))
        check = 0
        if self.mostrar_papelera.get_active():
            check = 1
            self.menu_comic = self.builder.get_object("menu_comic_2")
        else:
            self.menu_comic = self.builder.get_object("menu_comic")

        if self.filtro != '':

            # self.query = self.session.query(Comicbook).filter(
            #     Comicbook.path.like("%{}%".format(self.filtro))).filter(Comicbook.en_papelera == check)
            self.query = self.session.query(Comicbook)
            for word in self.filtro.split():
                self.query = self.query.filter(Comicbook.path.like("%{}%".format(word)))

            self.query = self.query.filter(Comicbook.en_papelera == check)
        else:
            self.query = self.session.query(Comicbook).filter(Comicbook.en_papelera == check)

        if len(lista_editoriales) > 0 or len(lista_volumen) > 0 or len(lista_arcos) > 0:
            self.query = self.query.join(Comicbook_Info,
                                         Comicbook_Info.id_comicbook_info == Comicbook.id_comicbook_info)

            if len(lista_arcos) > 0:
                self.query = self.query.join(Arcos_Argumentales_Comics_Reference, Arcos_Argumentales_Comics_Reference.id_comicbook_info == Comicbook_Info.id_comicbook_info). \
                    filter(Arcos_Argumentales_Comics_Reference.id_arco_argumental.in_(lista_arcos))
            else:
                if len(lista_editoriales) > 0 and len(lista_volumen) == 0:
                    self.query = self.query.join(Volume, Volume.id_volume == Comicbook_Info.id_volume)
                    self.query = self.query.join(Publisher, Publisher.id_publisher == Volume.id_publisher)
                    self.query = self.query.filter(Publisher.id_publisher.in_(lista_editoriales))
                if len(lista_volumen) > 0 and len(lista_editoriales) == 0:
                    self.query = self.query.join(Volume, Volume.id_volume == Comicbook_Info.id_volume)
                    self.query = self.query.filter(Volume.id_volume.in_(lista_volumen))
                if len(lista_editoriales) > 0 and len(lista_volumen) > 0:
                    self.query = self.query.join(Volume, Volume.id_volume == Comicbook_Info.id_volume)
                    self.query = self.query.join(Publisher, Publisher.id_publisher == Volume.id_publisher)
                    self.query = self.query.filter(Publisher.id_publisher.in_(lista_editoriales))
                    self.query = self.query.filter(Volume.id_volume.in_(lista_volumen))

        if len(lista_editoriales) > 0 or len(lista_volumen) > 0 or len(lista_arcos) > 0:
            self.query = self.query.order_by(Comicbook_Info.orden)
        else:
            self.query = self.query.order_by(Comicbook.path)

        print(lista_editoriales)
        # chequamos si mostramos todos o solo los catalogado o los no catalogados
        if self.none_radio.get_active():
            self.query = self.query.filter(Comicbook.id_comicbook_info == '')
        if self.all_radio.get_active():
            pass
        if self.selected_radio.get_active():
            self.query = self.query.filter(Comicbook.id_comicbook_info != '')

        cantidad_total_registros = self.query.count()
        # self.update_imagen_papelera()
        self.updating_gui = True
        self.cbx_text_paginas.remove_all()
        # calculamos la cantidad de paginas para la consulta que tenemos
        cantidad_paginas = math.ceil(cantidad_total_registros / self.limit)
        print("CANTIDAD {}".format(cantidad_paginas))
        for i in range(0, cantidad_paginas):
            self.cbx_text_paginas.insert(i, str(i), "Página {} de {}".format(i + 1, cantidad_paginas))
        self.updating_gui = False
        self.cbx_text_paginas.set_active(0)

    def click_boton_config(self, widget):
        config = Config_gtk()
        config.window.show()
        self.popovermenu.popdown()

    def click_boton_acerca_de(self, widget):
        acerca_de = Acerca_de_gtk()
        acerca_de.window.show()

    def click_boton_open_scanear(self,widget):
        scanner = ScannerGtk(funcion_callback=self.loadAndCreateThumbnails)
        scanner.window.show()
        self.popovermenu.popdown()


    def get_id_comics_from_selection(self):
        comics = []
        for path in self.iconview.get_selected_items():
            indice = path
            comics.append(self.listaComics[indice[0]])
        return comics

    def click_catalogar(self,widget):
        comics = self.get_id_comics_from_selection()
        # for path in self.iconview.get_selected_items():
        #     indice = path
        #     comics.append(self.listaComics[indice[0]])
        cvs = Comic_vine_cataloger_gtk(comicbooks=comics, session=self.session)
        cvs.window.show()

    def click_boton_refresh(self,widget):
        self.loadAndCreateThumbnails()
        self.popovermenu.popdown()

    def click_boton_configurar_comicbook(self, widget):
        lista_comicbooks_id = []
        for path in self.iconview.get_selected_items():
            indice = path
            lista_comicbooks_id.append(self.listaComics[indice[0]].id_comicbook)
        print(lista_comicbooks_id)
        cbi = Comicbook_Detail_Gtk(session=self.session, lista_comics_id=lista_comicbooks_id)
        cbi.get_first(None)
        cbi.window.show()
        if self.popovermenu is not None:
            self.popovermenu.popdown()
        if self.menu_comic is not None:
            self.menu_comic.popdown()

    def click_boton_catalogar(self, widget):
        comics = []
        for path in self.iconview.get_selected_items():
            indice = path
            comics.append(self.listaComics[indice[0]])
        cvs = Comic_vine_cataloger_gtk(comicbooks=comics, session=self.session)
        cvs.window.show()
        if self.popovermenu is not None:
            self.popovermenu.popdown()
        if self.menu_comic is not None:
            self.menu_comic.popdown()

    def click_derecho_panel_izquierdo(self, widget, event):

        if event.button == 3:
            rect = Gdk.Rectangle()
            rect.x = event.x
            rect.y = event.y+70
            rect.width = rect.height = 1
            self.menu_panel_izquierdo.set_pointing_to(rect)
            self.menu_panel_izquierdo.show_all()

    def click_derecho(self, widget, event):
        # click derecho
        if event.button == 3:
            rect = Gdk.Rectangle()
            rect.height = 10
            rect.width = 10
            rect.x = int(event.x)
            rect.y = int(event.y + (event.y_root-event.y)-80)
            self.menu_comic.set_pointing_to(rect)
            self.menu_comic.set_position(3)
            self.menu_comic.set_relative_to(widget)
            # self.menu_comic.show_all()
            self.menu_comic.popup()



    def item_seleccionado(self,selected):
        for path in self.iconview.get_selected_items():
            indice  = path
            print(self.listaComics[indice[0]])




    def click_boton_serie(self, widget):
        serie = Volumens_gtk(self.session)
        serie.window.show()
        self.popovermenu.popdown()

    def click_editorial(self, widget):
        editorial = PublisherGtk(self.session)
        editorial.window.show()
        self.popovermenu.popdown()

    def on_click_scanner(self, button):
        # pub = ScannerGtk(self.loadAndCreateThumbnails)
        pub = ScannerGtk()
        pub.window.show()
        self.popovermenu.popdown()

    def on_click_me_clicked(self, button):
        self.popover.set_relative_to(self.opciones)
        self.popover.show_all()
        self.popover.popup()

    def crear_thumnail(self, comic, iter):
        '''Recibe el comic y el iter para poder refresacar el thumnail del cover'''
        comicbooks_detail_manager = Commicbooks_detail(self.session)
        comicbooks_detail_manager.set_comicbook(comic.id_comicbook)
        cover = comicbooks_detail_manager.crear_thumnail_cover()
        GLib.idle_add(self.liststore.set_value, iter, 0, cover)

    def crear_thumnails_de_pagina_background(self):
        # hilo que solo lanza la creacion individual de thumnails
        self.load_setup()
        self.cantidad_thumnails_pendiente = len(self.lista_pendientes)
        print(self.cantidad_thumnails_pendiente)
        self.salir_thread=False
        print("CARGANDO THUMNAIL {}".format(self.cantidad_thumnails_pendiente))
        for iter, comic in self.lista_pendientes:
            cover = None
            t = threading.Thread(target=self.crear_thumnail, args=(comic, iter,))
            t.start()

            self.cantidad_thumnails_pendiente -= 1
            self.cantidad_thumnails_pendiente -= 1
            if self.salir_thread:
                print("SALIENDO DEL THREAD")
                break

    def loadAndCreateThumbnails(self):
        if not self.updating_gui:
            # sacamo el hilo que puede estar creando los thumnails para la pagina anterior porque ahora la vamos a
            # recreear
            self.salir_thread = True
            self.liststore.clear()
            self.lista_pendientes.clear()
            self.listaComics = self.query.limit(self.limit).offset(self.offset).all()
            print("Cantidad de comics: {}".format(len(self.listaComics)))

            self.iconview.set_model(self.liststore)
            self.iconview.set_pixbuf_column(0)
            self.iconview.set_text_column(1)
            self.cantidadThumnailsAGenerar = len(self.listaComics)
            self.cantidadThumnailsGenerados = 0
            self.label_contadores.set_text("0/{}".format(len(self.listaComics)))
            for index, comic in enumerate(self.listaComics):
                self.cantidadThumnailsGenerados += 1
                try:
                    nombreThumnail = self.pahThumnails + str(comic.id_comicbook) + '.jpg'
                    cover = None
                    if os.path.isfile(nombreThumnail):
                        try:
                            cover = Pixbuf.new_from_file(nombreThumnail)
                        except:
                            cover = Pixbuf.new_from_file(self.pahThumnails + "error_caratula.png")

                        #cover = Pixbuf.new_from_file(self.pahThumnails + "sin_caratula.jpg")
                        if comic.id_comicbook_info != '':
                            self.cataloged_pix.composite(cover,
                                                         cover.props.width - self.cataloged_pix.props.width,

                                                         cover.props.height - self.cataloged_pix.props.height,
                                                         self.cataloged_pix.props.width,
                                                         self.cataloged_pix.props.height,
                                                         cover.props.width - self.cataloged_pix.props.width,
                                                         cover.props.height - self.cataloged_pix.props.height,
                                                         1, 1,
                                                         3, 200)
                            cover.scale_simple(50, 10, 3)
                        self.liststore.append([cover, comic.getNombreArchivo(), index])
                    else:
                        cover = Pixbuf.new_from_file(self.pahThumnails + "sin_caratula.jpg")
                        iter = self.liststore.append([cover, comic.getNombreArchivo(), index])
                        self.lista_pendientes.append((iter, comic))
                except NotRarFile:
                    print('error en el archivo ' + comic.path)
                except BadRarFile:
                    print('error en el archivo ' + comic.path)

            self.thread_creacion_thumnails = threading.Thread(target=self.crear_thumnails_de_pagina_background)
            self.thread_creacion_thumnails.start()
            self.update_imagen_papelera()

if __name__ == "__main__":
    GLib.set_prgname('Babelcomics')
    bc = BabelComics_main_gtk()
    bc.window.connect("destroy", Gtk.main_quit)
    bc.window.show()
    bc.window.maximize()
    Gtk.main()
