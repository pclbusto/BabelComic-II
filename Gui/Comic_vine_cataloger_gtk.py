import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Volumes.Volume import Volume
from datetime import date
from iconos.Iconos import Iconos
from Gui.Volumen_lookup_gtk import Volume_lookup_gtk
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
    def __init__(self,  comicbooks, session=None,):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.setup = self.session.query(Setup).first()
        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                            "coverIssuesThumbnails" + os.path.sep
        self.handlers = {'click_boton_lookup_serie':self.click_boton_lookup_serie,
                         'click_boton_calcular_numeracion':self.click_boton_calcular_numeracion,
                         'tree_view_archivos_para_catalogar_selection_change':self.tree_view_archivos_para_catalogar_selection_change,
                         'change_entry_id_volumen_catalogar':self.change_entry_id_volumen_catalogar,
                         'click_boton_traer_todo':self.click_boton_traer_todo,
                         'treeview_issues_in_volumen_selection_change':self.treeview_issues_in_volumen_selection_change}



        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Comic_vine_cataloger_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comic_vine_cataloger_gtk")
        self.image_cover_comic_local = self.builder.get_object("image_cover_comic_local")
        self.entry_serie_local = self.builder.get_object("entry_serie_local")
        self.entry_nombre_archivo_local = self.builder.get_object("entry_nombre_archivo_local")
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



        self.listore_comics_para_catalogar.clear()
        self.comicbooks = comicbooks
        for index,comic in enumerate(comicbooks):
            self.listore_comics_para_catalogar.append([int(comic.numero), comic.path, index, False])

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
        print("dsadsa")
        desde = 0
        hasta = 0
        if self.entry_expresion_regular_numeracion.get_text() != '':
            expresion = self.entry_expresion_regular_numeracion.get_text()
            for comic in self.listore_comics_para_catalogar:
                match = re.search(expresion, comic[1])
                if match is not None:
                    if match.group(1).isdigit():
                        comic[0] = int(match.group(1))
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

    def listViewComicsClicked(self, args):

        print(self.listViewComics.item(self.listViewComics.selection(), "values")[0])
        index = int(self.listViewComics.item(self.listViewComics.selection(), "values")[0])

        self.panelSourceComic.destroy()
        self.comicbook = self.comicbooks[index]
        self.comicbook.openCbFile()
        self.comicbook.goto(0)

        self.panelSourceComic = self.__createPanelComic__(self, self.comicbook,
                                                          self.comicbook.getImagePage().resize(self.size,
                                                                                                   resample=Image.BICUBIC),
                                                          'Comic info')

        self.panelSourceComic.grid(column=0, row=0, sticky=(N, W, S, E))

    def copiarInfoGrupoBtn(self):
        t = threading.Thread(target=self.copiarInfoGrupo)
        t.start()

    def copiarInfoGrupo(self):

        cantidadZeros=0
        for comic in self.comicbooks:
            if comic.numero == 0:
                cantidadZeros+=1
        if cantidadZeros>1:
            print("hay mas de un cero en la lista a catalogar. Se anula el proceso")
            return

        cnf = Config(self.session)
        print('clave: ' + cnf.getClave('issue'))
        cv = ComicVineSearcher(cnf.getClave('issue'),session=self.session)
        cv.setEntidad('issue')
        catalogador = Catalogador(self.session)
        for comic in self.comicbooks:
            print("Vamos a ACTUALIZAR EL COMIC")
            print(comic)
            comicInfo=None
            '''Buscamos en la lista de Vine el numero de comic'''
            for comicVine in self.listaAMostrar:
                    if comicVine.numero==comic.numero:
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

                for item in self.listViewComics.get_children():
                    if completComicInfo.numero == self.listViewComics.item(item, 'text'):
                        print("ACTUALIZANDO GUI")
                        t = threading.Thread(target=self.updateGui, args=[item])
                        t.start()

        self.setup.ultimoNumeroConsultadoHasta = self.entryNumeroHasta.get()
        self.setup.ultimoNumeroConsultadoDesde = self.entryNumeroDesde.get()
        self.setup.ultimoVolumeIdUtilizado = self.entrySerie.get()
        self.setup.expresionRegularNumero = self.entryPathRe.get()
        print(self.setup)
        self.session.commit()

    def updateGui(self, item):
        print("Dentro del thead: {}:".format(item))
        self.listViewComics.item(item, image=self.iconoGreenOrb)

    def copiarInfo(self):
        cnf = Config(self.session)
        print('clave: ' + cnf.getClave('issue'))
        cv = ComicVineSearcher(cnf.getClave('issue'),session=self.session)
        cv.setEntidad('issue')
        completComicInfo = cv.getVineEntity(self.comicBookVine.idExterno)
        self.comicbook = self.session.query(ComicBook).filter(ComicBook.path==self.comicbook.path).first()
        catalogador = Catalogador(self.session)
        catalogador.copyFromComicToComic(completComicInfo,self.comicbook)
        self.setup.ultimoNumeroConsultadoHasta = self.entryNumeroHasta.get()
        self.setup.ultimoNumeroConsultadoDesde = self.entryNumeroDesde.get()
        self.setup.ultimoVolumeIdUtilizado = self.entrySerie.get()
        self.setup.expresionRegularNumero = self.entryPathRe.get()
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
            self.liststore_comics_in_volumen.append([int(comic.numero), comic.titulo, int(comic.comicVineId), index])

    def buscarSerie(self):
        listaNumeros = [comic.numero for comic in self.comicbooks]
        comicInVolumeList = self.session.query(ComicInVolumes).filter(
            ComicInVolumes.volumeId == self.entrySerie.get()).order_by(ComicInVolumes.numero).all()
        print(listaNumeros)
        listaNumeroComics = [comic.numero for comic in comicInVolumeList]
        self.listaAMostrar.clear()
        self.listaAMostrar = []

        print(listaNumeroComics)
        for comic in comicInVolumeList:
            if comic.numero in listaNumeros:
                self.listaAMostrar.append(comic)
        for item in self.grillaComics.get_children():
            self.grillaComics.delete(item)
        for comic in self.listaAMostrar:
            self.grillaComics.insert('', 0, '', values=(comic.numero,comic.titulo,comic.comicVineId))


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
    comics_query = session.query(ComicBook).filter(ComicBook.path.like('%batm%')).all()
    # for comic in comics_query:
    #     comics.append(comic)

    cvs = Comic_vine_cataloger_gtk(comics_query)
    cvs.window.show_all()
    cvs.window.connect("destroy", Gtk.main_quit)
    Gtk.main()