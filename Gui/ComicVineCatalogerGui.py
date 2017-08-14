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

        self.comicbooks[0].openCbFile()
        self.comicbooks[0].goto(0)
        self.size = (160, 248)
        self.panelSourceComic = self.__createPanelComic__(self, comicbooks[0],
                                                          self.comicbooks[0].getImagePage().resize(self.size,resample=Image.BICUBIC),
                                                          'Comic info')


        self.panelSourceComic.grid(sticky=(N, W, S, E))
        self.listViewComics = ttk.Treeview(self)

        self.listViewComics['columns'] = ['Nombre_Archivo']
        #, 'Total_Paginas', 'Porcentaje_Descargado']
        self.listViewComics.heading('#0', text='Nro')
        self.listViewComics.column('#0', width=3)
        self.listViewComics.heading('Nombre_Archivo', text='Nombre Archivo')
        self.listViewComics.column('Nombre_Archivo', width=230)
        self.listViewComics.grid(row=1, column=0, sticky=(N, W, S, E),columnspan=4)
        ##Panel opciones busqueda

        self.panelBusqueda = LabelFrame(self)
        self.panelBusqueda.grid(column=1, row=0, sticky=(N, W, S, E))
        #self.entryTitulo = StringVar()
        self.entrySerie = StringVar()
        self.spinNumero = IntVar()
        self.spinAnio = IntVar()

        self.seriesLookupFrame = ttk.Frame(self.panelBusqueda)
        self.seriesLookupFrame.grid(column=1, row=0, sticky=(W,E), pady=5)

        panelVolumenLookup=ttk.Frame(self.seriesLookupFrame)
        panelVolumenLookup.grid(column=1, row=0,sticky=(W,E))
        ttk.Label(self.seriesLookupFrame, text='Volumen:').grid(column=0, row=0, sticky=(W), pady=5)
        self.pilImagenLookup = Iconos.pilImagenLookup
        self.lookupImage = ImageTk.PhotoImage(self.pilImagenLookup)
        ttk.Button(panelVolumenLookup, image=self.lookupImage, command=self.openSerieLookup).grid(column=2, row=0, sticky=(E), pady=5)

        ttk.Entry(panelVolumenLookup, textvariable=self.entrySerie).grid(column=1, row=0, sticky=(W), pady=5)
        ttk.Label(self.seriesLookupFrame, text='Número:').grid(column=0, row=1, sticky=(W), pady=5)
        Spinbox(self.seriesLookupFrame, textvariable=self.spinNumero, from_=0, to=9999).grid(column=1, row=1, sticky=(W),
                                                                                         pady=5)

        botonBuscar = ttk.Button(self.seriesLookupFrame, text='Buscar', command=self.buscarSerie)
        botonBuscar.grid(column=2, row=0, pady=5)

        ##config grilla comics
        self.grillaComics = ttk.Treeview(self.seriesLookupFrame,
                                         columns=('fecha', 'titulo', 'descripcion', 'idExterno', 'numero',
                                                  'api_detail_url', 'thumb_url', 'volumeName', 'volumeId'),
                                         displaycolumns=('titulo', 'numero', 'volumeName'))

        self.grillaComics.heading('titulo', text='Título')
        self.grillaComics.heading('fecha', text='Fecha Cover')
        self.grillaComics.heading('descripcion', text='Descripcion')
        self.grillaComics.heading('idExterno', text='Id Vine')
        self.grillaComics.heading('numero', text='Número')
        self.grillaComics.heading('api_detail_url', text='api_detail_url')
        self.grillaComics.heading('thumb_url', text='thumb_url')
        self.grillaComics.heading('volumeName', text='Serie')
        self.grillaComics.heading('volumeId', text='SserieID')

        self.grillaComics.config(show='headings')  # tree, headings
        self.grillaComics.grid(column=0, row=2, columnspan=10, sticky=(N, E, S, W))
        self.grillaComics.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()
        self.grillaComics.column('numero',width=65)
        # boton copiar datos
        ttk.Button(self.seriesLookupFrame, text='copiar info', command=self.copiarInfo).grid(column=2, row=1)
        print('--------------------------------------')
        '''
        cargamos los datos que se guardaron de la ultima vez
        '''
        setup = self.session.query(Setup).first()
        self.spinNumero.set(setup.ultimoNumeroConsultado)
        self.entrySerie.set(setup.ultimoVolumeIdUtilizado)

    def copiarInfo(self):
        cnf = Config(self.session)
        print('clave: ' + cnf.getClave('issue'))
        cv = ComicVineSearcher(cnf.getClave('issue'))
        cv.setEntidad('issue')
        completComicInfo = cv.getVineEntity(self.comicBookVine.idExterno)
        self.comicbook = self.session.query(ComicBook).filter(ComicBook.path==self.comicbook.path).first()
        catalogador = Catalogador(self.session)
        catalogador.copyFromComicToComic(completComicInfo,self.comicbook)
        setup = self.session.query(Setup).first()
        setup.ultimoNumeroConsultado = self.spinNumero.get()
        setup.ultimoVolumeIdUtilizado = self.entrySerie.get()
        self.session.commit()
        self.parent.destroy()

    def itemClicked(self, event):
        if (self.grillaComics.selection):

            item = self.grillaComics.item(self.grillaComics.selection())
            webImage = item['values'][6]
            nombreImagen = item['values'][6][item['values'][6].rindex('/') + 1:]
            setup = self.session.query(Setup).first()
            path = setup.directorioBase + os.sep + "images" + os.sep + "searchCache" + os.sep

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
        buscador = ComicVineSearcher(config.getClave("issues"))

        buscador.setEntidad('issues')
        if (self.entrySerie.get()):
            buscador.addFilter('volume:' + self.entrySerie.get())
        if (str(self.spinNumero.get()) != '0'):
            buscador.addFilter('issue_number:' + str(self.spinNumero.get()))

        buscador.vineSearch()
        for item in self.grillaComics.get_children():
            self.grillaComics.delete(item)
        for issue in buscador.listaBusquedaVine:
            self.grillaComics.insert('', 0, '', values=(issue['fecha'],
                                                        issue['titulo'],
                                                        issue['descripcion'],
                                                        issue['idExterno'],
                                                        issue['numero'],
                                                        issue['api_detail_url'],
                                                        issue['thumb_url'],
                                                        issue['volumeName'],
                                                        issue['volumeId']
                                                        ))


if __name__ == '__main__':
    root = Tk()
    session = Entidades.Init.Session()
    comics=[]
    comics.append(session.query(ComicBook).filter(ComicBook.path=='E:\\Comics\\DC\\DC Week+ (01-11-2017)\\Hal Jordan & the Green Lantern Corps 012 (2017) (2 covers) (digital) (Minutemen-Slayer).cbr') .order_by(ComicBook.path.asc()).first())
    comics.append(session.query(ComicBook).filter(
    ComicBook.path == 'E:\\Comics\\DC\\DC Week+ (07-13-2016)\\Hal Jordan and the Green Lantern Corps - Rebirth 01 (2016) (Webrip) (The Last Kryptonian-DCP).cbr').order_by(
        ComicBook.path.asc()).first())

    cvs = ComicCatalogerGui(root, comics)
    #cvs.entrySerie.set('4363')
    #cvs.spinNumero.set(80)
    cvs.grid(sticky=(N, W, S, E))
    cvs.grid()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()
