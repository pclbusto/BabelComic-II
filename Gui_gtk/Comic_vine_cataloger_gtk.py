import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Volumes.Volume import Volume


from Gui_gtk.Volumen_lookup_gtk import Volume_lookup_gtk
from Extras.ComicVineSearcher import ComicVineSearcher
from Entidades.Setups.Setup import Setup

from Extras.ComicCataloger import Catalogador
import urllib.request
import os
from  Extras.Config import Config
import Entidades.Init
from Entidades.Volumes.ComicsInVolume import ComicInVolumes
import re
import threading


class Comic_vine_cataloger_gtk():
    def __init__(self,  comicbooks=None, session=None):
        if session is not None:
            self.session = session
            print("usnado session existente")
        else:
            self.session = Entidades.Init.Session()
            print("SESSION NEW")
        self.setup = self.session.query(Setup).first()
        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                            "coverIssuesThumbnails" + os.path.sep
        self.handlers = {'click_boton_lookup_serie':self.click_boton_lookup_serie,
                         'click_boton_calcular_numeracion':self.click_boton_calcular_numeracion,
                         'tree_view_archivos_para_catalogar_selection_change':self.tree_view_archivos_para_catalogar_selection_change,
                         'change_entry_id_volumen_catalogar':self.change_entry_id_volumen_catalogar,
                         'click_boton_traer_todo':self.click_boton_traer_todo,
                         'treeview_issues_in_volumen_selection_change':self.treeview_issues_in_volumen_selection_change,
                         'click_boton_traer_solo_para_catalogar':self.click_boton_traer_solo_para_catalogar,
                         'boton_catalogar_simple':self.boton_catalogar_simple,
                         'boton_catalogar_grupo':self.boton_catalogar_grupo}



        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Comic_vine_cataloger_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comic_vine_cataloger_gtk")
        self.image_cover_comic_local = self.builder.get_object("image_cover_comic_local")
        self.entry_serie_local = self.builder.get_object("entry_serie_local")
        self.entry_nombre_archivo_local = self.builder.get_object("entry_nombre_archivo_local")
        self.treeview_comics_para_catalogar = self.builder.get_object("treeview_comics_para_catalogar")
        self.listore_comics_para_catalogar = self.builder.get_object("listore_comics_para_catalogar")
        self.liststore_comics_in_volumen = self.builder.get_object("liststore_comics_in_volumen")
        self.entry_expresion_regular_numeracion = self.builder.get_object("entry_expresion_regular_numeracion")
        self.entry_id_volumen_catalogar = self.builder.get_object("entry_id_volumen_catalogar")
        self.entry_descripcion_volumen_catalogar = self.builder.get_object("entry_descripcion_volumen_catalogar")
        self.entry_desde = self.builder.get_object("entry_desde")
        self.entry_hasta = self.builder.get_object("entry_hasta")
        self.entry_serie_vine = self.builder.get_object("entry_serie_vine")
        self.entry_titulo_vine = self.builder.get_object("entry_titulo_vine")
        self.entry_numero_vine = self.builder.get_object("entry_numero_vine")
        self.entry_fecha_vine = self.builder.get_object("entry_fecha_vine")
        self.image_cover_comic_vine = self.builder.get_object("image_cover_comic_vine")

        self.listaAMostrar =[]
        self.listore_comics_para_catalogar.clear()
        self.comicbooks = comicbooks
        for index,comic in enumerate(comicbooks):
            self.listore_comics_para_catalogar.append([int(comic.numero), comic.path, index, 0])

        self._load_comic(comicbooks[0])
        self.entry_expresion_regular_numeracion.set_text(".*\#(\d*)")


    def tree_view_archivos_para_catalogar_selection_change(self,selection):
        (model, iter) = selection.get_selected()
        if iter:
            # comicbook = self.session.query(ComicBook).filter(
            #     Publisher.id_publisher == model[iter][0]).first()
            self._load_comic(self.comicbooks[model[iter][2]])
            # print(self.c model[iter][2])

    def click_boton_calcular_numeracion (self,widget):
        desde = 0
        hasta = 0
        if self.entry_expresion_regular_numeracion.get_text() != '':
            expresion = self.entry_expresion_regular_numeracion.get_text()
            for index, comic in enumerate(self.listore_comics_para_catalogar):
                match = re.search(expresion, comic[1])
                if match is not None:
                    if match.group(1).isdigit():
                        comic[0] = int(match.group(1))
                        self.comicbooks[index].numero = match.group(1)
                        if hasta == 0:
                            hasta = comic[0]
                        if desde == 0:
                            desde = comic[0]
                        if comic[0]>hasta :
                            hasta = comic[0]
                        if comic[0]<desde:
                            desde = comic[0]
        self.entry_desde.set_text(str(desde))
        self.entry_hasta.set_text(str(hasta))

        self._load_comic(self.comicbooks[0])

    def change_entry_id_volumen_catalogar(self,widget):
        self.editorial = None
        if (self.entry_id_volumen_catalogar.get_text() != ''):
            self.volume = None
            self.volume = self.session.query(Volume).get(self.entry_id_volumen_catalogar.get_text())
            if self.volume is not None:
                self.entry_descripcion_volumen_catalogar.set_text(self.volume.nombre)

    def click_boton_lookup_serie(self,widget):
        lookup = Volume_lookup_gtk(self.session, self.entry_id_volumen_catalogar)
        lookup.window.show()

    def _load_comic(self, comic):

        self.entry_serie_local.set_text(comic.volumeNombre)
        self.entry_nombre_archivo_local.set_text(comic.getNombreArchivo())
        comic.openCbFile()
        nombreThumnail = self.pahThumnails + str(comic.comicId) + comic.getPageExtension()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=nombreThumnail,
            width=150,
            height=250,
            preserve_aspect_ratio=True)
        self.image_cover_comic_local.set_from_pixbuf(pixbuf)
        self.comicbook = comic

    def _load_comic_vine(self, comic):

        self.entry_serie_vine.set_text(comic.volumeNombre)
        self.entry_fecha_vine.set_text(comic.fechaTapa)
        self.entry_titulo_vine.set_text(comic.titulo)
        self.entry_numero_vine.set_text(comic.numero)
        comic.openCbFile()
        nombreThumnail = comic.path
        print("PATH COVER {}".format(nombreThumnail))
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=nombreThumnail,
            width=150,
            height=250,
            preserve_aspect_ratio=True)
        self.image_cover_comic_vine.set_from_pixbuf(pixbuf)

    def AutoAsignar(self):
        if self.entryPathRe.get() != '':
            expresion = self.entryPathRe.get()
            for comic in self.comicbooks:
                match = re.search(expresion, comic.path)
                if match is not None:
                    if match.group(1).isdigit():
                        comic.numero = str(int(match.group(1)))
                    else:
                        comic.numero=match.group(1)

        for item in self.listViewComics.get_children():
            self.listViewComics.delete(item)

        '''cargamos los comics de nuevo con los numeros asignados.'''
        for index,comic in enumerate(self.comicbooks):
            self.listViewComics.insert('', 'end', text=comic.numero, image=self.iconoRedOrb,
                                    values=([index,comic.path]))
        for comic in self.comicbooks:
            print(comic)

    def boton_catalogar_grupo(self,widget):
        t = threading.Thread(target=self._catalogar_grupo)
        t.start()

    def _catalogar_grupo(self):
        cantidadZeros=0
        for comic in self.comicbooks:
            if comic.numero == 0:
                cantidadZeros+=1
        if cantidadZeros>1:
            print("hay mas de un cero en la lista a catalogar. Se anula el proceso")
            return

        cnf = Config(self.session)
        print('clave: ' + cnf.getClave('issue'))
        cv = ComicVineSearcher(cnf.getClave('issue'), session=self.session)
        cv.setEntidad('issue')
        catalogador = Catalogador(self.session)
        for index, comic in enumerate(self.comicbooks):
            print("Vamos a ACTUALIZAR EL COMIC:{}".format(comic.path))
            comicInfo=None
            '''Buscamos en la lista de Vine el numero de comic'''
            for comicVine in self.comicInVolumeList:
                    print("Numero Vine:{} numero comic:{}".format(comicVine.numero, comic.numero))
                    if comicVine.numero == comic.numero:
                        comicInfo = comicVine
                        break
            print("Encontramos el comic:")
            print(comicInfo)
            '''Si existe lo catalogamos'''
            if comicInfo is not None:
                print("LA INFO COMPLETA")
                print(comicInfo)
                cv.setEntidad('issue')
                completComicInfo = cv.getVineEntity(comicInfo.comicVineId)
                comicbook = self.session.query(ComicBook).filter(ComicBook.path==comic.path).first()
                catalogador.copyFromComicToComic(completComicInfo,comicbook)
                GLib.idle_add(self.check_fila_treeview_comics_para_catalogar, index)
        self.save_estado_catalogo()


    def check_fila_treeview_comics_para_catalogar(self, index):
        self.treeview_comics_para_catalogar.get_model()[index][3] = True

    def boton_catalogar_simple(self, widget):
        cnf = Config(self.session)
        print('clave: ' + cnf.getClave('issue'))
        cv = ComicVineSearcher(cnf.getClave('issue'),session=self.session)
        cv.setEntidad('issue')
        completComicInfo = cv.getVineEntity(self.comicBookVine.comicVineId)
        self.comicbook = self.session.query(ComicBook).filter(ComicBook.path==self.comicbook.path).first()
        catalogador = Catalogador(self.session)
        catalogador.copyFromComicToComic(completComicInfo,self.comicbook)
        self.save_estado_catalogo()
        (modelo, iter) = self.treeview_comics_para_catalogar.get_selection().get_selected()
        modelo[iter][3]=True

    def save_estado_catalogo(self):
        self.setup.ultimoNumeroConsultadoHasta = self.entry_desde.get_text()
        self.setup.ultimoNumeroConsultadoDesde = self.entry_hasta.get_text()
        self.setup.ultimoVolumeIdUtilizado = self.entry_id_volumen_catalogar.get_text()
        self.setup.expresionRegularNumero = self.entry_expresion_regular_numeracion.get_text()
        print(self.setup)
        self.session.commit()

    def treeview_issues_in_volumen_selection_change(self, selection):
        (model, iter) = selection.get_selected()
        if iter:
            comic_in_volumen = self.comicInVolumeList[model[iter][3]]
            cnf = Config(self.session)
            cv = ComicVineSearcher(cnf.getClave('issues'), session=self.session)
            cv.setEntidad('issues')
            # print(item['values'][2])
            cv.addFilter("id:" + str(comic_in_volumen.comicVineId))
            cv.vineSearch()
            webImage = cv.listaBusquedaVine[0].thumb_url
            nombreImagen = webImage[webImage.rindex('/') + 1:]
            print(webImage)
            print(nombreImagen)

            path = self.setup.directorioBase + os.sep + "images" + os.sep + "searchCache" + os.sep

            if not (os.path.isfile(path + nombreImagen)):
                print('no existe')
                print(nombreImagen)
                # path = setup.directorioBase + os.sep + "images"+ os.sep+"searchCache" + os.sep
                jpg = urllib.request.urlopen(webImage)
                jpgImage = jpg.read()
                fImage = open(path + nombreImagen, 'wb')
                fImage.write(jpgImage)
                fImage.close()
            self.comicBookVine = cv.listaBusquedaVine[0]
            self.comicBookVine.path = path + nombreImagen
            self._load_comic_vine(self.comicBookVine)


    def click_boton_traer_todo(self,widget):

        self.comicInVolumeList = self.session.query(ComicInVolumes).filter(
            ComicInVolumes.volumeId == self.volume.id).order_by(ComicInVolumes.numero).all()
        self.liststore_comics_in_volumen.clear()
        for index, comic in enumerate(self.comicInVolumeList):
            self.liststore_comics_in_volumen.append([comic.numero, comic.titulo, int(comic.comicVineId), index])

    def click_boton_traer_solo_para_catalogar(self, widget):
        lista_numeros = []
        for comic in self.listore_comics_para_catalogar:
            lista_numeros.append(str(comic[0]))
        print(lista_numeros)
        self.comicInVolumeList = self.session.query(ComicInVolumes).filter(
            ComicInVolumes.volumeId == self.volume.id).all()
        self.comicInVolumeList = [comic for comic in self.comicInVolumeList if comic.numero in lista_numeros ]
        print(self.comicInVolumeList)

        # .filter(ComicInVolumes.numero in lista_numeros).order_by(ComicInVolumes.numero).all()

        print(self.comicInVolumeList)
        # listaNumeroComics = [comic for comic in self.comicInVolumeList if comic.numero>=desde and comic.numero<=hasta]
        self.listaAMostrar.clear()
        self.listaAMostrar = []

        # print(listaNumeroComics)
        # for comic in self.comicbooks:
        #     if comic.numero in listaNumeroComics:
        #         self.listaAMostrar.append(comic)
        self.liststore_comics_in_volumen.clear()

        for index, comic in enumerate(self.comicInVolumeList):
            self.liststore_comics_in_volumen.append([comic.numero, comic.titulo, int(comic.comicVineId), index])


if __name__ == '__main__':

    session = Entidades.Init.Session()
    # pathComics=["/home/pedro/Imágenes/comics/Witchblade (2017) Issue #1.cbz"]
    # '''
    #             "E:\\Comics\\DC\\Action Comics\\Action Comics 442.cbr",
    #             "E:\\Comics\\DC\\Action Comics\\Action Comics 447.cbr",
    #             "E:\\Comics\\DC\\Action Comics\\Action Comics 470.cbr",
    #             "E:\\Comics\\DC\\Action Comics\\Action Comics 473.cbr"
    #  '''
    # comics= []
    comics_query = session.query(ComicBook).filter(ComicBook.path.like('%s/Batman (2016) Issue #3.%')).all()
    # for comic in comics_query:
    #     comics.append(comic)

    cvs = Comic_vine_cataloger_gtk(comics_query)
    cvs.window.show_all()
    cvs.window.connect("destroy", Gtk.main_quit)
    cvs.entry_id_volumen_catalogar.set_text('91273')
    Gtk.main()