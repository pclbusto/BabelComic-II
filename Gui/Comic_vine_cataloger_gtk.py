import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Volumes.Volume import Volume
from datetime import date
from iconos.Iconos import Iconos
from Gui.VolumeLookupGui import VolumesLookupGui
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

        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                            "coverIssuesThumbnails" + os.path.sep
        self.handlers = {'click_boton_lookup_serie':self.click_boton_lookup_serie}


        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Comic_vine_cataloger_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Comic_vine_cataloger_gtk")
        self.image_cover_comic_local = self.builder.get_object("image_cover_comic_local")
        self.entry_serie_local = self.builder.get_object("entry_serie_local")
        self.entry_nombre_archivo_local = self.builder.get_object("entry_nombre_archivo_local")
        self.listore_comics_para_catalogar = self.builder.get_object("listore_comics_para_catalogar")

        self.listore_comics_para_catalogar.clear()
        for index,comic in enumerate(comicbooks):
            self.listore_comics_para_catalogar.append([comic.comicId, comic.path, index, False])

        self._load_comic(comicbooks[0])

    def click_boton_lookup_serie(self,widget):
        lookup = Publisher_lookup_gtk.Publisher_lookup_gtk(self.session, self.entry_id)
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

    def int(self,t):
        return(int(t[0]))

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        if col in['numero']:
            l.sort(reverse=reverse,key=self.int)
        else:
            l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        # reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

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


    def itemClicked(self, event):
        if (self.grillaComics.selection):

            item = self.grillaComics.item(self.grillaComics.selection())

            cnf = Config(self.session)
            cv = ComicVineSearcher(cnf.getClave('issues'), session=self.session)
            cv.setEntidad('issues')
            print(item['values'][2])
            cv.addFilter("id:"+str(item['values'][2]))
            cv.vineSearch()
            webImage = cv.listaBusquedaVine[0].thumb_url
            nombreImagen = webImage[webImage.rindex('/') + 1:]
            print(webImage)
            print(nombreImagen)

            path = self.setup.directorioBase + os.sep + "images" + os.sep + "searchCache" + os.sep

            if not (os.path.isfile(path  + nombreImagen)):
                print('no existe')
                print(nombreImagen)
                # path = setup.directorioBase + os.sep + "images"+ os.sep+"searchCache" + os.sep
                jpg = urllib.request.urlopen(webImage)
                jpgImage = jpg.read()
                fImage = open(path  + nombreImagen, 'wb')
                fImage.write(jpgImage)
                fImage.close()
            fImage = open(path  + nombreImagen, 'rb')
            im = Image.open(fImage)

        # print(item['values'][8],item['values'][4])
        self.comicBookVine = ComicBook()
        self.comicBookVine.path = 'Path'
        self.comicBookVine.titulo = str(item['values'][1])
        self.comicBookVine.volumeId = self.entrySerie.get()
        self.comicBookVine.numero = item['values'][0]
        #self.comicBookVine.fechaTapa = item['values'][0]
        #self.comicBookVine.resumen = item['values'][2]
        self.comicBookVine.idExterno = item['values'][2]

        self.panelVineComic = self.__createPanelComic__(self, self.comicBookVine, im.resize(self.size),
                                                        'Vine Info')
        self.panelVineComic.grid(column=2, row=0, sticky=(N, S, E, W))

    def traerTodos(self):

        comicInVolumeList = self.session.query(ComicInVolumes).filter(
            ComicInVolumes.volumeId == self.entrySerie.get()).order_by(ComicInVolumes.numero).all()
        self.listaAMostrar.clear()
        self.listaAMostrar = []
        for item in self.grillaComics.get_children():
            self.grillaComics.delete(item)
        for comic in comicInVolumeList:
            self.listaAMostrar.append(comic)
            self.grillaComics.insert('', 0, '', values=(comic.numero, comic.titulo, comic.comicVineId))

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
    pathComics=["/home/pedro/Imágenes/comics/Witchblade (2017) Issue #1.cbz"]
    '''
                "E:\\Comics\\DC\\Action Comics\\Action Comics 442.cbr",
                "E:\\Comics\\DC\\Action Comics\\Action Comics 447.cbr",
                "E:\\Comics\\DC\\Action Comics\\Action Comics 470.cbr",
                "E:\\Comics\\DC\\Action Comics\\Action Comics 473.cbr"
     '''
    comics= []
    for pathComic in pathComics:
        comic = session.query(ComicBook).filter(ComicBook.path ==pathComic).first()
        print(comic)
        comics.append(comic)

    cvs = Comic_vine_cataloger_gtk( comics)
    cvs.window.show_all()
    cvs.window.connect("destroy", Gtk.main_quit)
    Gtk.main()