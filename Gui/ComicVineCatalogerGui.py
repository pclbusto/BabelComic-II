from tkinter import *
from tkinter import *
from tkinter import Tk, ttk
from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Volumes.Volume import Volume
from datetime import date
from iconos.Iconos import Iconos
from Gui.VolumeLookupGui import VolumesLookupGui
from Extras.ComicVineSearcher import ComicVineSearcher
from Entidades.Setups.Setup import Setup

from Extras.ComicCataloger import Catalogador
from PIL import Image, ImageTk
import urllib.request
import os
from  Extras.Config import Config
import Entidades.Init
from Entidades.Volumes.ComicsInVolume import ComicInVolumes
import re
import threading

class ComicCatalogerGui(Frame):
    '''muestra un panel con una info de comic resumida
    |------| serie nº /de
    |      | titulo
    |      | arco
    |      | nº arco / de
    |------|
    '''

    def __createPanelComic__(self, parent, comicbook, comicCoverImage, titulo):
        panelComic = ttk.LabelFrame(parent,text = titulo)
        self.comicCovers.append(ImageTk.PhotoImage(comicCoverImage))
        comicCoverLabel = ttk.Label(panelComic, image=self.comicCovers[len(self.comicCovers) - 1], compound='top')
        comicCoverLabel.grid(column=0, row=0, sticky=(W))
        panelInfo = ttk.LabelFrame(panelComic, text='info')
        panelInfo.grid(column=1, row=0, sticky=(W, E, N))
        if comicbook.volumeId!=0:
            volume = self.session.query(Volume).filter(Volume.id==comicbook.volumeId).first()
            if volume is None:
                print('No se pudo recueperar la serie')
                nombreSerie = ttk.Label(panelInfo, text='Volume: ' + "")
                numerode = ttk.Label(panelInfo, text='Número: ' + str(comicbook.numero) + ' de ' + str(0))
            else:
                nombreSerie = ttk.Label(panelInfo, text='Volume: ' + volume.nombre)
                numerode = ttk.Label(panelInfo,text='Número: ' + str(comicbook.numero) + ' de ' + str(volume.cantidadNumeros))

        archivo = ttk.Label(panelInfo, text='Archivo: ' + comicbook.getNombreArchivo(), anchor=W, wraplength=270)
        tituloEjemplar = ttk.Label(panelInfo, text='Título: ' + comicbook.titulo)
        arcoAlternativo = ttk.Label(panelInfo, text='Fecha Tapa: ' + str(comicbook.fechaTapa))

        nombreSerie.grid(sticky=(W), padx=5)
        tituloEjemplar.grid(sticky=(W), padx=5)
        numerode.grid(sticky=(W), padx=5)
        arcoAlternativo.grid(sticky=(W), padx=5)
        archivo.grid(sticky=(W), padx=5)
        return panelComic

    def openSerieLookup(self):
        window = Toplevel()
        volumeRetorno = Volume()
        lk =  VolumesLookupGui(window, volumeRetorno, session=self.session)
        lk.grid(sticky=(E, W, S, N))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.geometry("+0+0")
        window.wm_title(string="Series")
        lk.buscarVolume()
        lk.treeview_sort_column(lk.grillaVolumes, 'name', False)
        self.wait_window(window)
        serieRetorno = lk.getSerie()
        self.entrySerie.set(serieRetorno.id)

    def __init__(self, parent, comicbooks,session =None, *cnf, **kw):
        Frame.__init__(self, parent, *cnf, **kw)
        self.rowconfigure(0, weight=1)
        self.parent = parent
        self.rowconfigure(1, weight=1)
        self.comicCovers = []
        # representa lo que vamos a catalogar. tomando como fuente de datos ComicVine
        self.comicbooks = comicbooks
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.listaAMostrar =[]
        self.comicbook = self.comicbooks[0]
        self.comicbooks[0].openCbFile()
        self.comicbooks[0].goto(0)
        self.size = (160, 248)
        self.panelSourceComic = self.__createPanelComic__(self, comicbooks[0],
                                                          self.comicbooks[0].getImagePage().resize(self.size,resample=Image.BICUBIC),
                                                          'Comic info')


        self.panelSourceComic.grid(column=0,row=0, sticky=(N, W, S, E))

        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background="green")


        self.panelListView=ttk.Frame(self)
        self.panelListView.grid(row=1, column=0, sticky=(N, W, S, E),columnspan=6)
        self.panelListView.grid_columnconfigure(0,weight=1)
    #dsadsadsa
        #dsdasda

        self.listViewComics = ttk.Treeview(self.panelListView)

        self.listViewComics['columns'] = ['Nro','Nombre_Archivo']
        self.listViewComics['displaycolumns']=['Nombre_Archivo']
        #, 'Total_Paginas', 'Porcentaje_Descargado']
        self.listViewComics.heading('#0', text='Nro Comic')
        self.listViewComics.column('#0',  width=100,stretch=True)
        self.listViewComics.heading('Nombre_Archivo', text='Nombre Archivo')
        self.listViewComics.column('Nombre_Archivo', width=1000)
        self.listViewComics.grid(row=0, column=0, sticky=(N, W, S, E),columnspan=2)
        self.listViewComics.bind("<<TreeviewSelect>>",self.listViewComicsClicked)
        self.entryPathRe = Entry(self.panelListView)
        self.entryPathRe.grid(column=0, row=1, sticky=(N, W, S, E), padx=5)
        self.botonAutoasignar = Button(self.panelListView,text='Auto asignar',command=self.AutoAsignar)
        self.botonAutoasignar.grid(column=1, row=1, sticky=(N, W, S, E))
        self.iconoRedOrb = ImageTk.PhotoImage(Iconos().pilRedOrb)
        self.iconoGreenOrb = ImageTk.PhotoImage(Iconos().pilGreenOrb)

        for index,comic in enumerate(self.comicbooks):
            self.listViewComics.insert('', 'end', image = self.iconoRedOrb, text=comic.numero,
                                    values=([index,comic.path]))


        ##Panel opciones busqueda
        self.panelBusqueda = LabelFrame(self)
        self.panelBusqueda.grid(column=1, row=0, sticky=(N, W, S, E))
        #self.entryTitulo = StringVar()
        self.entrySerie = StringVar()
        self.entryNumeroDesde = IntVar()
        self.entryNumeroHasta = IntVar()
        self.spinAnio = IntVar()

        self.seriesLookupFrame = ttk.Frame(self.panelBusqueda)
        self.seriesLookupFrame.grid(column=1, row=0, sticky=(W,E), pady=5)

        panelVolumenLookup=ttk.Frame(self.seriesLookupFrame)
        panelVolumenLookup.grid(column=1, row=0,sticky=(W,E))
        ttk.Label(self.seriesLookupFrame, text='Volumen:').grid(column=0, row=0, sticky=(W), pady=5)
        self.pilImagenLookup = Iconos().pilImagenLookup
        self.lookupImage = ImageTk.PhotoImage(self.pilImagenLookup)
        ttk.Button(panelVolumenLookup, image=self.lookupImage, command=self.openSerieLookup).grid(column=2, row=0, sticky=(E), pady=5)

        ttk.Entry(panelVolumenLookup, textvariable=self.entrySerie).grid(column=1, row=0, sticky=(W), pady=5)
        ttk.Label(self.seriesLookupFrame, text='Número Desde/Hasta:').grid(column=0, row=1, sticky=(W), pady=5)
        Entry(self.seriesLookupFrame, textvariable=self.entryNumeroDesde).grid(column=1, row=1, sticky=(W),
                                                                                         pady=5)

        Entry(self.seriesLookupFrame, textvariable=self.entryNumeroHasta).grid(column=2, row=1,
                                                                                             sticky=(W),
                                                                                             pady=5)

        self.botonCopiarGrupo = ttk.Button(self.seriesLookupFrame, text='Copiar Grupo', command=self.copiarInfoGrupoBtn)
        self.botonCopiarGrupo.grid(column=3, row=2, pady=5)
        botonBuscar = ttk.Button(self.seriesLookupFrame, text='Traer Todo', command=self.traerTodos)
        botonBuscar.grid(column=0, row=2, pady=5)
        botonBuscar = ttk.Button(self.seriesLookupFrame, text='Buscar', command=self.buscarSerie)
        botonBuscar.grid(column=1, row=2, pady=5)

        ##config grilla comics
        self.grillaComics = ttk.Treeview(self.seriesLookupFrame,
                                         columns=('numero','titulo','idComic'),
                                         displaycolumns=('numero','titulo'))

        self.grillaComics.heading('titulo', text='Título', command=lambda: self.treeview_sort_column(self.grillaComics, 'titulo', False))
        self.grillaComics.heading('numero', text='Número', command=lambda: self.treeview_sort_column(self.grillaComics, 'numero', False))


        self.grillaComics.config(show='headings')  # tree, headings
        self.grillaComics.grid(column=0, row=3, columnspan=10, sticky=(N, E, S, W))
        self.grillaComics.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()
        self.grillaComics.column('numero',width=65)
        self.grillaComics.column('titulo', width=400)
        # boton copiar datos
        ttk.Button(self.seriesLookupFrame, text='copiar info', command=self.copiarInfo).grid(column=2, row=2)
        print('--------------------------------------')
        '''
        cargamos los datos que se guardaron de la ultima vez
        '''
        self.setup = self.session.query(Setup).first()
        self.entryNumeroDesde.set(self.setup.ultimoNumeroConsultadoDesde)
        self.entryNumeroHasta.set(self.setup.ultimoNumeroConsultadoHasta)
        self.entrySerie.set(self.setup.ultimoVolumeIdUtilizado)
        self.entryPathRe.insert(0, self.setup.expresionRegularNumero)

    def AutoAsignar(self):
        '''Toma los comics en la lista y trata mediante el RE calcular los numeros para cada comic. Ademas de esto de todo los numeros que tiene el volumen solo
        trae aquellos que esten dentro de la lista de nuemeros que se pudieron recuperar'''


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
    root = Tk()
    session = Entidades.Init.Session()
    pathComics=["E:\\Comics\\DC\\Action Comics\\Action Comics 420.cbr",
                "E:\\Comics\\DC\\Action Comics\\Action Comics 422.cbr",
                "E:\\Comics\\DC\\Action Comics\\Action Comics 423.cbr"
               ]
    '''
     ,
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

    comics_query = session.query(ComicBook).filter(ComicBook.path.like('%batm%')).all()
    cvs = ComicCatalogerGui(root, comics_query)
    #cvs.entrySerie.set('4363')
    #cvs.spinNumero.set(80)
    cvs.grid(sticky=(N, W, S, E))
    cvs.grid()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()
