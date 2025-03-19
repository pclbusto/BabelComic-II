import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

from Entidades.Agrupado_Entidades import Volume, Comicbook_Info_Cover_Url, Setup, Comicbook_Info
from Entidades.Entitiy_managers import Comicbooks_Info
from Gui_gtk.Volumen_lookup_gtk import Volume_lookup_gtk
from Gui_gtk.VolumeGuiGtk import VolumeGuiGtk
import urllib.request
import os
from gi.repository import Gdk
import Entidades.Init
import re
import threading
from datetime import datetime

class Comic_vine_cataloger_gtk():
    def __init__(self,  comicbooks=None, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.setup = self.session.query(Setup).first()
        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                            "coverIssuesThumbnails" + os.path.sep
        self.handlers = {'click_boton_lookup_serie':self.click_boton_lookup_serie,
                         'tree_view_archivos_para_catalogar_selection_change':self.tree_view_archivos_para_catalogar_selection_change,
                         'change_entry_id_volumen_catalogar':self.change_entry_id_volumen_catalogar,
                         'treeview_issues_in_volumen_selection_change': self.treeview_issues_in_volumen_selection_change,
                         'click_boton_traer_solo_para_catalogar': self.click_boton_traer_solo_para_catalogar,
                         'boton_catalogar_grupo': self.boton_catalogar_grupo,
                         'text_edited': self.text_edited,
                         'calcular_numeracion': self.calcular_numeracion,
                         'borrar_linea': self.borrar_linea,
                         'siguiente_cover': self.siguiente_cover,
                         'anterior_cover':self.anterior_cover,
                         'cerrar_ventana':self.cerrar_ventana,
                         'click_boton_label_volumen_id': self.click_boton_label_volumen_id,
                         'tecla_presionada': self.tecla_presionada}



        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Comic_vine_cataloger_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comic_vine_cataloger_gtk")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.image_cover_comic_local = self.builder.get_object("image_cover_comic_local")
        self.entry_serie_local = self.builder.get_object("entry_serie_local")
        self.entry_nombre_archivo_local = self.builder.get_object("entry_nombre_archivo_local")
        self.treeview_comics_para_catalogar = self.builder.get_object("treeview_comics_para_catalogar")
        self.treeview_comics_in_volumen = self.builder.get_object("treeview_comics_in_volumen")
        self.listore_comics_para_catalogar = self.builder.get_object("listore_comics_para_catalogar")
        self.liststore_comics_in_volumen = self.builder.get_object("liststore_comics_in_volumen")
        self.entry_expresion_regular_numeracion = self.builder.get_object("entry_expresion_regular_numeracion")
        self.entry_id_volumen_catalogar = self.builder.get_object("entry_id_volumen_catalogar")
        self.entry_descripcion_volumen_catalogar = self.builder.get_object("entry_descripcion_volumen_catalogar")
        self.entry_serie_vine = self.builder.get_object("entry_serie_vine")
        self.entry_titulo_vine = self.builder.get_object("entry_titulo_vine")
        self.entry_numero_vine = self.builder.get_object("entry_numero_vine")
        self.entry_fecha_vine = self.builder.get_object("entry_fecha_vine")
        self.image_cover_comic_vine = self.builder.get_object("image_cover_comic_vine")
        self.boton_cantidad_covers = self.builder.get_object("boton_cantidad_covers")
        self.box_cover_vine = self.builder.get_object("box_cover_vine")
        self.spinner = Gtk.Spinner()
        self.comicbooks_info_manager = Comicbooks_Info()
        self.lista_covers = []
        self.index_lista_covers = 0
        self.listaAMostrar = []
        self.lista_covers_downloading = []
        self.lock = threading.Lock()
        self.listore_comics_para_catalogar.clear()
        # contine la lista de comics que vamos a catalogar
        self.comicbooks = comicbooks
        for index, comic in enumerate(comicbooks):
            self.listore_comics_para_catalogar.append(['', comic.path, index, 0, 0])

        self._load_comic(comicbooks[0])
        self.entry_expresion_regular_numeracion.set_text(self.setup.expresionRegularNumero)
        self.entry_id_volumen_catalogar.set_text(self.setup.ultimoVolumeIdUtilizado)

        self.gui_updating = False
        screen = Gdk.Screen.get_default()
        self.window.set_default_size(screen.width(), self.window.get_size()[1]*(1.5))

    def tecla_presionada(self, widget, args):
        print(args.keyval)
        if args.keyval == Gdk.KEY_Escape:
            self.window.close()
        if args.keyval == Gdk.KEY_Return:
            if len(self.lista_botones_visibles) > 0:
                self.lista_botones_visibles[0].clicked()
                self.window.close()

    def click_boton_label_volumen_id(self,widget):
        serie = VolumeGuiGtk(self.session)
        serie.set_volumen_id(self.entry_id_volumen_catalogar.get_text())
        serie.window.show()

    def siguiente_cover(self, widget):
        self.comicbooks_info_manager.get_next_cover_complete_path()
        self.load_cover_comic_info()

    def anterior_cover(self, widget):
        self.comicbooks_info_manager.get_prev_cover_complete_path()
        self.load_cover_comic_info()

    def borrar_linea(self,widget, event):
        if event.keyval == Gdk.KEY_Delete:
            (model, iter) = self.treeview_comics_para_catalogar.get_selection().get_selected()
            if iter:
                # no borramos la lista de comics porque sino tenemos que recalcular el indice que tenemos en la col 2
                del(model[iter])


    def text_edited(self, widget, path, text):
        self.listore_comics_para_catalogar[path][0] = text

        self.listore_comics_para_catalogar[path][4] = float(text)
        self.click_boton_traer_solo_para_catalogar(None)


    def return_lookup(self,id_volume):
        if id_volume != '':
            self.entry_id_volumen_catalogar.set_text(str(id_volume))
        self.calcular_numeracion(None)

    def tree_view_archivos_para_catalogar_selection_change(self,selection):
        (model, iter) = selection.get_selected()
        if iter:
            self._load_comic(self.comicbooks[model[iter][2]])
            if model[iter][0] != '':
                print("nro comicbook: {}".format(model[iter][0]))
                nro_comic = model[iter][0]
                index = 0
                for row in  self.liststore_comics_in_volumen:
                    if nro_comic == row[0]:
                        break
                    index += 1
                c = self.treeview_comics_in_volumen.get_column(0)
                self.treeview_comics_in_volumen.set_cursor(index, c, True)
            else:
                print("Nada")


    def is_number(self, s):
        try:
            float(s)  # for int, long and float
        except ValueError:
            try:
                complex(s)  # for complex
            except ValueError:
                return False

        return True

    def calcular_numeracion(self, widget):

        if self.entry_expresion_regular_numeracion.get_text() != '':
            expresion = self.entry_expresion_regular_numeracion.get_text()
            for index, comic in enumerate(self.listore_comics_para_catalogar):
                match = re.search(expresion, comic[1])

                if match is not None:

                    if self.is_number(match.group(1)):
                        comic[0] = str(int(match.group(1)))
                        comic[4] = float(match.group(1))
                    else:
                        comic[4] = 0
                        comic[0] = match.group(1)
        self.click_boton_traer_solo_para_catalogar(None)
        self._load_comic(self.comicbooks[0])

    def change_entry_id_volumen_catalogar(self,widget):
        self.editorial = None
        if (self.entry_id_volumen_catalogar.get_text() != ''):
            self.volume = None
            self.volume = self.session.query(Volume).get(self.entry_id_volumen_catalogar.get_text())
            if self.volume is not None:
                self.entry_descripcion_volumen_catalogar.set_text(self.volume.nombre)
                self.click_boton_traer_solo_para_catalogar(None)

    def click_boton_lookup_serie(self,widget):
        lookup = Volume_lookup_gtk(self.session, self.return_lookup)
        lookup.window.show()

    def _load_comic(self, comic):
        if comic.id_comicbook_info != '':
            comic_info = self.session.query(Comicbook_Info).get(comic.id_comicbook_info)
            self.entry_serie_local.set_text(comic_info.nombre_volumen)
        self.entry_nombre_archivo_local.set_text(comic.getNombreArchivo())
        comic.openCbFile()

        nombreThumnail = self.pahThumnails + str(comic.id_comicbook) + '.jpg'

        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=nombreThumnail,
                width=150,
                height=250,
                preserve_aspect_ratio=True)
        except:
            nombreThumnail = self.pahThumnails + "error_caratula.png"
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=nombreThumnail,
                width=150,
                height=250,
                preserve_aspect_ratio=True)
        self.image_cover_comic_local.set_from_pixbuf(pixbuf)
        self.comicbook = comic

    def _load_comic_vine(self):

        self.entry_serie_vine.set_text(self.comicbooks_info_manager.entidad.nombre_volumen)
        if self.comicbooks_info_manager.entidad.fecha_tapa == 0:
            dt = datetime.fromordinal(1)
        else:
            dt = datetime.fromordinal(self.comicbooks_info_manager.entidad.fecha_tapa)
        self.entry_fecha_vine.set_text("{}/{}/{}".format(dt.year, dt.month, dt.day))
        self.entry_titulo_vine.set_text(self.comicbooks_info_manager.entidad.titulo)
        self.entry_numero_vine.set_text(self.comicbooks_info_manager.entidad.numero)
        # comic.openCbFile()

        nombreThumnail = self.comicbooks_info_manager.get_cover_complete_path()

        if (os.path.isfile(nombreThumnail)):
            self.mostrar_cover(nombreThumnail)
        else:
            print("Elimiando compoennte en spinner")
            self.box_cover_vine.remove(self.image_cover_comic_vine)
            self.box_cover_vine.remove(self.spinner)
            self.box_cover_vine.add(self.spinner)#, 1, 0, 1, 1)
            self.window.show_all()
            self.spinner.start()

    def mostrar_cover(self, nombreThumnail):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=nombreThumnail,
            width=150,
            height=250,
            preserve_aspect_ratio=True)
        print("Elimiando compoennte en imagen")
        self.box_cover_vine.remove(self.spinner)
        self.box_cover_vine.remove(self.image_cover_comic_vine)
        self.box_cover_vine.add(self.image_cover_comic_vine)  # , 1, 0, 1, 1)
        self.window.show_all()
        self.image_cover_comic_vine.set_from_pixbuf(pixbuf)

    def boton_catalogar_grupo(self,widget):
        t = threading.Thread(target=self._catalogar_grupo)
        t.start()

    def _catalogar_grupo(self):
        cantidadZeros=0

        for index, comic in enumerate(self.listore_comics_para_catalogar):
            if comic[0] == '':
                cantidadZeros+=1
        if cantidadZeros>1:
            print("hay mas de un cero en la lista a catalogar. Se anula el proceso")
            return
        for numero in self.listore_comics_para_catalogar:
            nro = numero[0]
            comicbook = self.comicbooks[numero[2]]
            for comicbook_info in self.lista_comicbook_info_por_volumen:
                print(nro, type(nro), comicbook_info.numero, type(comicbook_info.numero))
                if nro==comicbook_info.numero:
                    comicbook.id_comicbook_info = comicbook_info.id_comicbook_info
                    numero[3]=True
                    break

        self.session.commit()


    def check_fila_treeview_comics_para_catalogar(self, index):
        self.treeview_comics_para_catalogar.get_model()[index][3] = True

    def cerrar_ventana(self, widget, args):
        self.setup.ultimoVolumeIdUtilizado = self.entry_id_volumen_catalogar.get_text()
        self.setup.expresionRegularNumero = self.entry_expresion_regular_numeracion.get_text()
        print(self.setup)
        self.session.commit()

    def treeview_issues_in_volumen_selection_change(self, selection):
        (model, iter) = selection.get_selected()
        if iter:
            self.comicbooks_info_manager.get(model[iter][2])
            self.load_cover_comic_info()

    def load_cover_comic_info(self):
        self.boton_cantidad_covers.set_label("{}/{}".format(self.comicbooks_info_manager.index_lista_covers + 1, len(self.comicbooks_info_manager.lista_covers)))

        if not self.gui_updating:
            self._load_comic_vine()


    def descargar_imagen(self, web_image, path, nombre_imagen):
        threading.Thread(target=self.descargar_imagen_thread, args=[web_image, path, nombre_imagen]).start()


    def descargar_imagen_thread(self, web_image, path, nombre_imagen):
        if (path + nombre_imagen) not in self.lista_covers_downloading:
            self.lock.acquire(True)
            self.lista_covers_downloading.append(path + nombre_imagen)
            self.lock.release()
            print('bajando imagen')
            jpg = urllib.request.urlopen(web_image)
            jpg_image = jpg.read()
            print('imagen bajada')

            f_image = open(path + nombre_imagen, 'wb')
            f_image.write(jpg_image)
            f_image.close()
            self.lock.acquire(True)
            self.lista_covers_downloading.remove(path + nombre_imagen)
            self.lock.release()
            self.mostrar_cover(path + nombre_imagen)


    def click_boton_traer_solo_para_catalogar(self, widget):
        self.gui_updating = True
        lista_numeros = []
        # print(self.listore_comics_para_catalogar)
        for comic in self.listore_comics_para_catalogar:
            lista_numeros.append(str(comic[0]))
        # print(lista_numeros)
        if hasattr(self, "volume"):
            self.lista_comicbook_info_por_volumen = self.session.query(Comicbook_Info).filter(
                Comicbook_Info.id_volume == self.volume.id_volume).all()
            self.lista_comicbook_info_por_volumen = [comicbook_info for comicbook_info in self.lista_comicbook_info_por_volumen if comicbook_info.numero in lista_numeros ]
            # print(self.lista_comicbook_info_por_volumen)
            self.listaAMostrar.clear()
            self.liststore_comics_in_volumen.clear()
            for index, comicbook_info in enumerate(self.lista_comicbook_info_por_volumen):
                self.liststore_comics_in_volumen.append([comicbook_info.numero, comicbook_info.titulo, int(comicbook_info.id_comicbook_info), index, comicbook_info.orden])
            self.gui_updating = False

if __name__ == '__main__':

    #session = Entidades.Init.Session()
    # # pathComics=["/home/pedro/Imágenes/comics/Witchblade (2017) Issue #1.cbz"]
    # # '''
    # #             "E:\\Comics\\DC\\Action Comics\\Action Comics 442.cbr",
    # #             "E:\\Comics\\DC\\Action Comics\\Action Comics 447.cbr",
    # #             "E:\\Comics\\DC\\Action Comics\\Action Comics 470.cbr",
    # #             "E:\\Comics\\DC\\Action Comics\\Action Comics 473.cbr"
    # #  '''
    # # comics= []
    # comics_query = session.query(Comicbook).filter(Comicbook.path.like('%Batman%')).all()
    # print(comics_query)
    # # for comic in comics_query:
    # #     comics.append(comic)
    #
    # cvs = Comic_vine_cataloger_gtk(comics_query)
    # cvs.window.show_all()
    # cvs.window.connect("destroy", Gtk.main_quit)
    # cvs.entry_id_volumen_catalogar.set_text('91273')
    # Gtk.main()
    web_image = 'https://comicvine1.cbsistatic.com/uploads/scale_large/0/9241/2203280-batman_001__2011___3rd_printing_variant_cover___digital___golgoth_empire_.jpg'
    nombre_imagen = web_image[web_image.rindex('/') + 1:]
    print(web_image)
    print(nombre_imagen)
    dir_base = '/home/pedro/PycharmProjects/BabelComic-II'
    path = dir_base + os.sep + "images" + os.sep + "searchCache" + os.sep

    jpg = urllib.request.urlopen(web_image)
    jpg_image = jpg.read()
    print('imagen bajada')

    f_image = open(path + nombre_imagen, 'wb')
    f_image.write(jpg_image)
    f_image.close()