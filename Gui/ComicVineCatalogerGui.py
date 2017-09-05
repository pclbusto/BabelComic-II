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
        lk =  VolumesLookupGui(window, volumeRetorno)
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

        for index,comic in enumerate(self.comicbooks):
            self.listViewComics.insert('', 'end', text=comic.numero,
                                    values=([index,comic.path]))


        ##Panel opciones busqueda
        self.panelBusqueda = LabelFrame(self)
        self.panelBusqueda.grid(column=1, row=0, sticky=(N, W, S, E))
        #self.entryTitulo = StringVar()
        self.entrySerie = StringVar()
        self.spinNumeroDesde = IntVar()
        self.spinNumeroHasta = IntVar()
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
        Spinbox(self.seriesLookupFrame, textvariable=self.spinNumeroDesde, from_=0, to=9999).grid(column=1, row=1, sticky=(W),
                                                                                         pady=5)

        Spinbox(self.seriesLookupFrame, textvariable=self.spinNumeroHasta, from_=0, to=9999).grid(column=2, row=1,
                                                                                             sticky=(W),
                                                                                             pady=5)

        self.botonCopiarGrupo = ttk.Button(self.seriesLookupFrame, text='Copiar Grupo', command=self.copiarInfoGrupo)
        self.botonCopiarGrupo.grid(column=2, row=2, pady=5)
        botonBuscar = ttk.Button(self.seriesLookupFrame, text='Buscar', command=self.buscarSerie)
        botonBuscar.grid(column=0, row=2, pady=5)

        ##config grilla comics
        self.grillaComics = ttk.Treeview(self.seriesLookupFrame,
                                         columns=('fecha', 'titulo', 'descripcion', 'idExterno', 'numero',
                                                  'api_detail_url', 'thumb_url', 'volumeName', 'volumeId'),
                                         displaycolumns=('titulo', 'numero', 'volumeName'))

        self.grillaComics.heading('titulo', text='Título', command=lambda: self.treeview_sort_column(self.grillaComics, 'titulo', False))
        self.grillaComics.heading('fecha', text='Fecha Cover')
        self.grillaComics.heading('descripcion', text='Descripcion')
        self.grillaComics.heading('idExterno', text='Id Vine')
        self.grillaComics.heading('numero', text='Número', command=lambda: self.treeview_sort_column(self.grillaComics, 'numero', False))
        self.grillaComics.heading('api_detail_url', text='api_detail_url')
        self.grillaComics.heading('thumb_url', text='thumb_url')
        self.grillaComics.heading('volumeName', text='Serie')
        self.grillaComics.heading('volumeId', text='SserieID')

        self.grillaComics.config(show='headings')  # tree, headings
        self.grillaComics.grid(column=0, row=3, columnspan=10, sticky=(N, E, S, W))
        self.grillaComics.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()
        self.grillaComics.column('numero',width=65)
        # boton copiar datos
        ttk.Button(self.seriesLookupFrame, text='copiar info', command=self.copiarInfo).grid(column=1, row=2)
        print('--------------------------------------')
        '''
        cargamos los datos que se guardaron de la ultima vez
        '''
        self.setup = self.session.query(Setup).first()
        self.spinNumeroDesde.set(self.setup.ultimoNumeroConsultadoDesde)
        self.spinNumeroHasta.set(self.setup.ultimoNumeroConsultadoHasta)
        self.entrySerie.set(self.setup.ultimoVolumeIdUtilizado)
        self.entryPathRe.insert(0, self.setup.expresionRegularNumero)

    def AutoAsignar(self):
        if self.entryPathRe.get() != '':
            expresion = self.entryPathRe.get()
            for comic in self.comicbooks:
                match = re.search(expresion, comic.path)
                numero = match.group(1)
                if numero.isdigit():
                    comic.numero=int(numero)

        comicNumeroMinimo = self.comicbooks[0]
        comicNumeroMaximo = self.comicbooks[0]

        for comic in self.comicbooks:
            if comicNumeroMinimo.numero>comic.numero:
                comicNumeroMinimo=comic
            if comicNumeroMaximo.numero<comic.numero:
                comicNumeroMaximo=comic
        self.spinNumeroDesde.set(comicNumeroMinimo.numero)
        self.spinNumeroHasta.set(comicNumeroMaximo.numero)

        for item in self.listViewComics.get_children():
            self.listViewComics.delete(item)

        for index,comic in enumerate(self.comicbooks):
            self.listViewComics.insert('', 'end', text=comic.numero,
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


        self.setup.ultimoNumeroConsultadoHasta = self.spinNumeroHasta.get()
        self.setup.ultimoNumeroConsultadoDesde = self.spinNumeroDesde.get()
        self.setup.ultimoVolumeIdUtilizado = self.entrySerie.get()
        self.setup.expresionRegularNumero = self.entryPathRe.get()
        print(self.setup)
        self.session.commit()

    def copiarInfo(self):
        cnf = Config(self.session)
        print('clave: ' + cnf.getClave('issue'))
        cv = ComicVineSearcher(cnf.getClave('issue'),session=self.session)
        cv.setEntidad('issue')
        completComicInfo = cv.getVineEntity(self.comicBookVine.idExterno)
        self.comicbook = self.session.query(ComicBook).filter(ComicBook.path==self.comicbook.path).first()
        catalogador = Catalogador(self.session)
        catalogador.copyFromComicToComic(completComicInfo,self.comicbook)
        self.setup.ultimoNumeroConsultadoHasta = self.spinNumeroHasta.get()
        self.setup.ultimoNumeroConsultadoDesde = self.spinNumeroDesde.get()
        self.setup.ultimoVolumeIdUtilizado = self.entrySerie.get()
        self.setup.expresionRegularNumero = self.entryPathRe.get()
        print(self.setup)
        self.session.commit()


    def itemClicked(self, event):
        if (self.grillaComics.selection):

            item = self.grillaComics.item(self.grillaComics.selection())
            webImage = item['values'][6]
            nombreImagen = item['values'][6][item['values'][6].rindex('/') + 1:]

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
        self.comicBookVine.volumeId = item['values'][8]
        self.comicBookVine.numero = item['values'][4]
        self.comicBookVine.fechaTapa = item['values'][0]
        self.comicBookVine.resumen = item['values'][2]
        self.comicBookVine.idExterno = item['values'][3]

        self.panelVineComic = self.__createPanelComic__(self, self.comicBookVine, im.resize(self.size),
                                                        'Vine Info')
        self.panelVineComic.grid(column=2, row=0, sticky=(N, S, E, W))

    def buscarSerie(self):
        # recuperarla de la configuracion
        config = Config()
        buscador = ComicVineSearcher(config.getClave("issues"),session=self.session)

        buscador.setEntidad('issues')
        if (self.entrySerie.get()):
            buscador.addFilter('volume:' + self.entrySerie.get())
        '''vamos a cambiar esto y vamos a retornar de a 100 registros. Calculamos el offset que contiene el rango y eso retornamos desde 
        comicvine despues filtramos para solo mostrar lo que se pidio.
        '''

        comicInVolume = self.session.query(ComicInVolumes).filter(ComicInVolumes.volumenId == self.entrySerie.get()).filter(ComicInVolumes.comicNumber==self.spinNumeroDesde.get()).first()

        print(comicInVolume)

        buscador.vineSearch(io_offset=comicInVolume.offset)
        for item in self.grillaComics.get_children():
            self.grillaComics.delete(item)

        self.listaAMostrar.clear()
        self.listaAMostrar = []
        for comic in buscador.listaBusquedaVine:
            if comic.numero>=self.spinNumeroDesde.get() and comic.numero<=self.spinNumeroHasta.get():
                self.listaAMostrar.append(comic)

        for issue in self.listaAMostrar:
            print(issue)
            self.grillaComics.insert('', 0, '', values=(issue.fechaTapa,
                                                        issue.titulo,
                                                        issue.resumen,
                                                        issue.comicVineId,
                                                        issue.numero,
                                                        issue.api_detail_url,
                                                        issue.thumb_url,
                                                        issue.volumeNombre,
                                                        issue.volumeId
                                                        ))


if __name__ == '__main__':
    root = Tk()
    session = Entidades.Init.Session()
    pathComics=[  "E:\\Comics\\Capcom\\Street Fighter II #00.cbr",
                    "E:\\Comics\\Capcom\\Street Fighter II #01.cbr",
                    "E:\\Comics\\Capcom\\Street Fighter II #02.cbr",
                    "E:\\Comics\\Capcom\\Street Fighter II #03.cbr",
                    "E:\\Comics\\Capcom\\Street Fighter II #04.cbr",
                    "E:\\Comics\\Capcom\\Street Fighter II #05.cbr",
                    "E:\\Comics\\Capcom\\Street Fighter II #06.cbr"]
    comics= []
    for pathComic in pathComics:
        comic = session.query(ComicBook).filter(ComicBook.path ==pathComic).first()
        print(comic)
        comics.append(comic)

    cvs = ComicCatalogerGui(root, comics)
    #cvs.entrySerie.set('4363')
    #cvs.spinNumero.set(80)
    cvs.grid(sticky=(N, W, S, E))
    cvs.grid()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()
