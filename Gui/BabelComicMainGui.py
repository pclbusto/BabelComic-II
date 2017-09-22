from Gui.ComicBookGui import ComicBookGui
from Gui.ComicVineCatalogerGui import ComicCatalogerGui
from Gui.ConfigGui import ConfigGui
from Gui.ComicVisorGui import ComicVisorGui
from Gui.VolumeGui import VolumeGui
from Extras.WindowManager import *
from Gui.PublisherGui import PublisherGui
from Gui.ScannerGui import BabelComicScannerGui

from PIL import Image, ImageTk
from iconos.Iconos import Iconos
from Gui.PanelThumbnailComics import PanelThumbnailComics

import threading
from tkinter import Tk, ttk
from tkinter import *
import Entidades.Init

from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Setups.Setup import Setup
from Entidades.Publishers.Publisher import Publisher
from Entidades.Volumes.Volume import Volume
import Extras.ComicCataloger
from sqlalchemy import or_

class BabelComicMainGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self.barraHerramientas = Frame(parent)
        self.barraHerramientas.grid(column=0, row=0, sticky=(E, W))
        self.barraHerramientas.config()
        self.barraHerramientas.columnconfigure(0, weight=1)
        self.barraHerramientas.rowconfigure(1, weight=1)
        self.session = Entidades.Init.Session()
        self.setup = self.session.query(Setup).first()
        self.root = parent

        pilImagenLookup = Iconos().pilImagenLookup
        self.imagenLookup = ImageTk.PhotoImage(pilImagenLookup)

        self.pilImageFirst = Iconos().pilImageFirst
        self.imageFirst = ImageTk.PhotoImage(self.pilImageFirst)
        self.pilImagePrev = Iconos().pilImagePrev
        self.imagePrev = ImageTk.PhotoImage(self.pilImagePrev)
        self.pilImageNext = Iconos().pilImageNext
        self.imageNext = ImageTk.PhotoImage(self.pilImageNext)
        self.pilImageLast = Iconos().pilImageLast
        self.imageLast = ImageTk.PhotoImage(self.pilImageLast)


        '''Aca vamos a guardar las consulta para cada nodo del arbol de biblioteca'''
        self.listaConsultas=[]
        self.consultaActual = None
        self.listaComics = []
        self.consulta = ComicBook.path.like("%%")

        # opciones de barra de tareas
        self.buscarEntry = ttk.Entry(self.barraHerramientas)

        image = self.imagenLookup
        self.buscarBoton = ttk.Button(self.barraHerramientas, width=1, compound=CENTER, image=image,
                                 command=lambda: self.buscar(self.statusBar))
        self.buscarEntry.grid(column=6, row=0, sticky=E)
        self.buscarBoton.grid(column=7, row=0, sticky=E)
        self.buscarEntry.bind('<Return>', self.enterEventEntryBuscar)

        ttk.Button(self.barraHerramientas, text='refrescar', command=self.refrescar).grid(column=5, row=0, sticky=E)
        ttk.Button(self.barraHerramientas, image=self.imageFirst, command=self.primero).grid(column=1, row=0, sticky=E)
        ttk.Button(self.barraHerramientas, image=self.imagePrev, command=self.anterior).grid(column=2, row=0, sticky=E)
        ttk.Button(self.barraHerramientas, image=self.imageNext, command=self.siguiente).grid(column=3, row=0, sticky=E)
        ttk.Button(self.barraHerramientas, image=self.imageLast, command=self.ultimo).grid(column=4, row=0, sticky=E)
        ttk.Button(self.barraHerramientas, text='Salir', command=self.salir).grid(column=0, row=0, sticky=W)

        self.panedWindow = ttk.Panedwindow(parent, orient=HORIZONTAL)

        self.panedWindow.grid(column=0, row=1, sticky=(E, W, S, N))

        # arbol donde tenenmos las listas de comics.
        self.treeListas = ttk.Treeview(self.panedWindow)
        print(self.setup.anchoArbol)
        self.treeListas.column("#0", minwidth=0, width=self.setup.anchoArbol)

        self.treeListas.grid()
        self.biblioteca = ''
        '''Tomamos el indice o Id del nodo como la longitud de la lista para identificar la consulta asociada al nodo.
        este nodo indica la raiz del arbol con el nodo Biblioteca este nodo hace una consulta por todo comic sin tener 
        en cuenta editorial, volumen o arco. Trae todo.'''
        self.biblioteca = self.treeListas.insert('', 'end', len(self.listaConsultas), text='Biblioteca')
        self.listaConsultas.append(self.session.query(ComicBook).filter(ComicBook.comicVineId==''))
        self.editoriales = self.treeListas.insert(self.biblioteca, 'end', len(self.listaConsultas), text='Editoriales')
        '''1 al igual que el 0 tienen la misma consulta Trae todo.'''
        self.listaConsultas.append(self.session.query(ComicBook))
        self.crearArbolBibiloteca()



        # creamos menu popup para agregar vistas
        self. popup = Menu(self.treeListas, tearoff=0)
        self.popup.add_command(label="Abrir Volumenes", command=self.openVolume)

        self.treeListas.bind("<Button-3>", self.popupListas)

        self.treeListas.bind("<<TreeviewSelect>>", self.selectVista)

        self.panelGrillaComics = Frame(self.panedWindow)
        self.panelGrillaComics.columnconfigure(0, weight=1)
        self.panelGrillaComics.rowconfigure(0, weight=1)
        self.panelGrillaComics.grid(sticky=(N, S, W, E))

        #self.scrollbar = ttk.Scrollbar(self.panelGrillaComics)
        #self.scrollbar.grid(column=1, row=0, sticky=(S, N))

        #self.panelComics = PanelThumbnailComics(self.panedWindow, yscrollcommand=self.scrollbar.set)
        self.panelComics = PanelThumbnailComics(self.panedWindow)
        self.panelComics.bind("<Configure>", self.on_resize)



        #self.scrollbar.config(command=self.panelComics.yview)
        #    treeComics.grid()
        #self.panelComics.bind('<MouseWheel>', self.scrollupMouse)
        #parent.bind('<Down>', self.scrollupKeyboard)
        #parent.bind('<Key>', self.scrollupKeyboard)

        # creamos menu popup para abrir el catalogador el visor el editor de info y calcular el thumnails de nuevo
        self.popupThumbnails = Menu(self.panelComics, tearoff=0)

        self.popupThumbnails.add_command(label="Info comic", command=self.openComicEditor)
        self.popupThumbnails.add_command(label="Leer comic", command=self.openBabelComicVisor)
        self.popupThumbnails.add_command(label="Catalogar comic", command=self.openComicVine)
        self.popupThumbnails.add_separator()
        self.popupThumbnails.add_command(label="Refresh Thumbnail",
                                    command=self.panelComics.recreateThumbnails)

        self.calidad = Menu(self.popupThumbnails,tearoff=0)
        self.calidad.add_command(label='Mala')
        self.calidad.add_command(label='Buena')
        self.calidad.add_command(label='Muy Buena')
        self.calidad.add_command(label='Digital')
        self.popupThumbnails.add_cascade(label = 'Calidad', menu=self.calidad)

        self.panelComics.bind("<Button-3>", self.popupPanelThumbnails)

        parent.bind('<Control-m>', lambda x: self.openComicEditor())
        parent.bind('<Control-r>', lambda x: self.openComicVine())
        parent.bind('<Control-b>', lambda x: self.openBabelComicVisor())
        parent.bind('<Control-l>', lambda x: self.openVolume())
        parent.bind('<Control-p>', lambda x: self.openPublisher())


        parent.bind('<Control-s>', self.openBabelComicConfig)
        parent.bind('<Control-x>', self.openBabelComicScanner)
        parent.bind('<Control-c>', self.copiarInfoComic)
        parent.bind('<Control-v>', self.pegarInfoComic)

        self.statusBar = StringVar()
        ttk.Label(parent, textvariable=self.statusBar, anchor="e", relief='groove').grid(column=0, row=3, sticky=(W, E))

        self.panelComics.grid(column=0, row=0, sticky=(N, S, W, E))
        self.panedWindow.add(self.treeListas)
        self.panedWindow.add(self.panelComics)
        self.paginaActual=0
        # menu
        # comics = ComicBooks() m,
        self.buscar(self.statusBar)
        cantidadColumnas = 4
        # variables globales
        desc = False
    def copiarInfoComic(self, event):
        if len(self.panelComics.comicsSelected) == 1:
            self.comicClipboard = self.panelComics.getComicAt( self.panelComics.comicsSelected[0])
            print(self.comicClipboard)

    def pegarInfoComic(self, event):
        if self.comicClipboard is None:
            print("no se copio porque el clipboard esta vacio")
            return
        listaComicsDestino = []
        for index in self.panelComics.comicsSelected:
            listaComicsDestino.append(self.panelComics.getComicAt(index))
        if self.comicClipboard in listaComicsDestino:
            print("no se copia porque la fuente esta entre los destinos")
            return
        if len(self.panelComics.comicsSelected)<1:
            print("No se copia porque no hay destino")
            return
        catalogador = Extras.ComicCataloger.Catalogador(self.session)
        for destino in listaComicsDestino:
            catalogador.copyFromComicToComic(self.comicClipboard,
                                             destino)


    def multipleSelection(self):
        print("algo va")

    def crearArbolBibiloteca(self):
        publishers = self.session.query(Publisher).all()
        for publisher in publishers:
            editorialNode = self.treeListas.insert(self.editoriales, 'end', len(self.listaConsultas), text=publisher.name)
            '''Craemos consulta para el nodo'''
            self.listaConsultas.append(self.session.query(ComicBook).filter(ComicBook.publisherId==publisher.id_publisher))
            '''le pones -01 para poder diferemciar el  nodo volumen de una editorial a otra. De no hacerlo asi da error
            de nodo duplicado'''
            editorialNode = self.treeListas.insert(editorialNode, 'end', str(len(self.listaConsultas))+"-01", text='Volumenes')
            self.listaConsultas.append(
                self.session.query(ComicBook).filter(ComicBook.publisherId == publisher.id_publisher))
            self.crearArbolVolume(publisher.id_publisher, editorialNode, len(self.listaConsultas)-1)
        self.consultaActual = self.listaConsultas[0]

    def crearArbolVolume(self, publisherID, editorialNode, indiceConsultaPadre):
        '''
        Aca tenemos que armar los nodos para la editoral. Estos nodos son los volumenes que pertenecen a esta
        editorial. Ahora cada nodo tiene una consulta que es filtrar todo comic que tenga cumpla la conslta del
        padre mas que sea de este volumen
        :param publisherID: identifica la editorial
        :param editorialNode: identifica el nodo que representa la editorial
        :param indiceConsultaPadre: es el indice de la consulta del padre en la lista de consultas
        :return:
        '''
        volumes = self.session.query(Volume).filter(Volume.publisherId==publisherID).distinct(Volume.nombre).group_by(Volume.nombre).order_by(Volume.nombre).all()
        for volume in volumes:
            #si hya mas de un volumen que se llama igual la cuenta por el nombre es mayor que 1 en ese caso
            #creamos un nodo con el nombre para podermeter dentro los distintos volumenes por version
            cantidadRepeticiones = self.session.query(Volume).filter(Volume.publisherId==publisherID).filter(Volume.nombre==volume.nombre).count()
            print("Cantidad de repeticiones para{} {}".format(volume.nombre, cantidadRepeticiones))
            if cantidadRepeticiones>1:
                volumenes = self.session.query(Volume).filter(Volume.publisherId==publisherID).filter(Volume.nombre==volume.nombre).all()
                OR = or_(ComicBook.volumeId==vi.id for vi in volumenes)

                nodoVolumen = self.treeListas.insert(editorialNode, 'end', str(len(self.listaConsultas)), text=volume.nombre)
                consultaPadre = self.listaConsultas[indiceConsultaPadre]
                self.listaConsultas.append(
                    consultaPadre.filter(OR).order_by(ComicBook.numero))
                print("NOMBRE VOLUMEN: {}".format(volume.nombre))
                self.crearSubArbolVolumenesVersion(volume.nombre, nodoVolumen, len(self.listaConsultas)-1)
            else:
                self.treeListas.insert(editorialNode,'end',str(len(self.listaConsultas)), text = volume.nombre)
                consultaPadre = self.listaConsultas[indiceConsultaPadre]
                self.listaConsultas.append(consultaPadre.filter(ComicBook.volumeId==volume.id).order_by(ComicBook.numero))

    def crearSubArbolVolumenesVersion(self, nombreVolumen, nodoVolumen, indiceConsultaPadre):
        print("NOMBRE VOLUMEN PARAMETRO: {}".format(nombreVolumen))
        volumes = self.session.query(Volume).filter(Volume.nombre == nombreVolumen).order_by(Volume.AnioInicio).all()
        consultaPadre = self.listaConsultas[indiceConsultaPadre]
        for index,volume in enumerate(volumes,start=1):
            print("Creando filtro para volumen {} - {} {}".format(volume.nombre,volume.AnioInicio, nombreVolumen))
            self.treeListas.insert(nodoVolumen, 'end', str(len(self.listaConsultas)),
                                                 text="{}- Ver. {}".format(volume.nombre,index))
            self.listaConsultas.append(
                consultaPadre.filter(ComicBook.volumeId == volume.id).order_by(ComicBook.numero))

    def openPublisher(self):
        window = Toplevel()
        window.geometry("+0+0")
        window.wm_title(string="Editorial")
        publisherGui = PublisherGui(window, width=507, height=358, session=self.session)
        publisherGui.grid(sticky=(N, S, E, W))

    def openVolume(self):
        openWindow(Titulo="Volumen", session=self.session)
        # window = Toplevel()
        # window.geometry("+0+0")
        # window.wm_title(string="Volumen")
        # volumenGui = VolumeGui(window, width=507, height=358, session=self.session)
        # volumenGui.grid(sticky=(N, S, E, W))

    def salir(self):
        self.setup = self.session.query(Setup).first()
        self.setup.anchoArbol = self.treeListas.column('#0',"width")
        self.session.add(self.setup)
        self.session.commit()

        self.root.destroy()

    def CheckThumbnailsGeneration(self):
        while self.panelComics.threadLoadAndCreateThumbnails.isAlive():
            if self.panelComics.cantidadThumnailsAGenerar>0:
                self.statusBar.set('Porcentaje de carga de thumnails: {1:.2f} Cantidad de Registros: {0:}'.format(len(self.listaComics),100*(self.panelComics.cantidadThumnailsGenerados/self.panelComics.cantidadThumnailsAGenerar)))

        #print('generados {} totales {} porcentaje: '.format(self.panelComics.cantidadThumnailsGenerados, self.panelComics.cantidadThumnailsAGenerar))
                                                                  #,100 * (panelComics.cantidadThumnailsGenerados / panelComics.cantidadThumnailsAGenerar)))
        '''if len(self.listaComics)>0:
            self.statusBar.set('Porcentaje de carga de thumnails: {1:.2f} Cantidad de Registros: {0:}'.format(
            len(self.listaComics),
            100 * (self.panelComics.cantidadThumnailsGenerados / self.panelComics.cantidadThumnailsAGenerar)))'''

    def statusThumbnails(self):
        threadCheckThumbnailsGeneration = threading.Thread(target=self.CheckThumbnailsGeneration)
        threadCheckThumbnailsGeneration.start()

    def buscar(self, statusBar):
        #listaAtributos = [ComicBook.path]
        #filter = (listaAtributos[0].like(("%%")))
        self.listaComics.clear()
        self.listaComics = self.consultaActual.filter(ComicBook.path.like("%"+self.buscarEntry.get()+"%")).order_by(ComicBook.path.asc()).all()
        self.paginaActual = 0
        self.panelComics.loadComics(self.listaComics[(self.paginaActual*self.setup.cantidadComicsPorPagina):((self.paginaActual+1)*self.setup.cantidadComicsPorPagina)])
        self.statusThumbnails()
        statusBar.set('Cantidad de Registros: {} / {}'.format(30,len(self.listaComics)))

    def enterEventEntryBuscar(self):
        self.buscar(self.statusBar)


    def openComicEditor(self):
        if (self.panelComics.comicActual):
            comic = self.session.query(ComicBook).filter(ComicBook.path==self.panelComics.getComicActual().path).first()
            #comic = comics.get(panelComics.getComicActual().path)
            ventana = Toplevel()
            frameComic = ComicBookGui(ventana, comic, session=self.session)
            frameComic.grid()
    ##        frameComic.grid(padx=5, pady=5, sticky=(N, W, E, S))
    ##        frameComic.columnconfigure(0, weight=1)
    ##        frameComic.rowconfigure(0, weight=1)


    def openBabelComicConfig(self, event):
        window = Toplevel(root)
        window.title('Babel Comics Configuración')
        config = ConfigGui(window)
        config.grid(sticky=(N, S, W, E))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.grid()

    def openBabelComicVisor(self):
        print("estamos pro abrir")
        #if (panelComics.comicActual):
        print("abriendo")
        comic = self.panelComics.getComicActual()
        visor = ComicVisorGui(root, comic, session=self.session,height = root.winfo_screenheight(),width = root.winfo_screenwidth())
        visor.title = ('Babel Comics Visor')
        visor.wm_state('zoomed')

    def openComicVine(self):
        if (self.panelComics.comicActual):
            window = Toplevel()
            window.title('Catalogador')
            window.geometry('+0+0')
            comics=[]
            for index in self.panelComics.comicsSelected:
                comics.append(self.panelComics.getComicAt(index))
            # comic = self.panelComics.getComicActual()
            cvs = ComicCatalogerGui(window, comics, self.session)
            cvs.grid()
            window.columnconfigure(0, weight=1)
            window.rowconfigure(0, weight=1)
            root.wait_window(window)

    def sortby(self):
        grillaSeries.heading('start_year', command=lambda col='AnioInicio': self.sortby(col))
        if desc:
            self.buscarSerie('order by ' + col + ' desc')

    def openBabelComicScanner(self, event):
        print("Abriendo scanner")
        BabelComicScannerGui(root)
        #scanner = BabelComicMainGui()

    def scrollupMouse(self, event):
        self.panelComics.yview_scroll(-1 * (int)(event.delta / 120), "units")

    def scrollupKeyboard(self, event):
        print(event.keycode)
        if (event.keycode == 116) | (event.keycode == 117) | (event.keycode == 34)| (event.keycode == 40):
            self.panelComics.yview_scroll(1, "units")
            print('para abajo')
        if (event.keycode == 112) | (event.keycode == 111) | (event.keycode == 33)| (event.keycode == 38):
            self.panelComics.yview_scroll(-1, "units")
            print('para abajo')
        #el 114 es en linux y el 39 en windows
        if (event.keycode==114)|(event.keycode==39):#derecha
            self.panelComics.nextComic()
        # el 113 es en linux y el 37 en windows
        if (event.keycode == 113)|(event.keycode==37):  # izquierda
            self.panelComics.prevComic()

    def on_resize(self,event):
        #pass
        #solo refrescar cuando el tamañio sume o reste columnas
        self.panelComics.cantidadColumnas = int(event.width/(self.panelComics.size[0] + self.panelComics.space))
        #self.panelComics.loadComics(self.listaComics[(self.paginaActual*self.setup.cantidadComicsPorPagina) :((self.paginaActual+1)*self.setup.cantidadComicsPorPagina)])
        self.loadPage()
        print(self.panelGrillaComics.configure)

    def refrescar(self):
        #solo refrescar cuando el tamañio sume o reste columnas
        #if cantidadColumnas!=int(event.width/(panelComics.size[0] + panelComics.space)):
        #self.panelComics.loadComics(self.listaComics)
        #self.treeListas.column("#0",width=100)
        print("dsadas")
        self.loadPage()

    def popupListas(self,event):
        # display the popup menu
        try:
            if self.treeListas.item(self.treeListas.selection())["text"]=='Volumenes':
                self.popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.popup.grab_release()

    def popupPanelThumbnails(self,event):
        try:
            self.popupThumbnails.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.popupThumbnails.grab_release()

    def selectVista(self,event):
        print(self.treeListas.selection()[0])
        print("SELECON: "+self.treeListas.selection()[0])
        print("Padre: "+ self.treeListas.parent(self.treeListas.selection()[0]))
        if (self.treeListas.parent(self.treeListas.selection()[0])==''):
            self.consultaActual = self.listaConsultas[0]
        else:
            self.consultaActual= self.listaConsultas[int(self.treeListas.selection()[0])]
        self.buscar(self.statusBar)
        #self.comics.vistaConsultas = self.treeListas.selection()[0]

    def loadPage(self):
        if len(self.listaComics)<(self.paginaActual + 1) * self.setup.cantidadComicsPorPagina:
            print("cantidad:"+str(len(self.listaComics)))
            print("indice menor:" + str(self.paginaActual * self.setup.cantidadComicsPorPagina))
            print("indice mayor:" + str(len(self.listaComics)-1))

            self.panelComics.loadComics(self.listaComics[(self.paginaActual * self.setup.cantidadComicsPorPagina):len(self.listaComics)])
        else:
            self.panelComics.loadComics(self.listaComics[(self.paginaActual * self.setup.cantidadComicsPorPagina):(
            (self.paginaActual + 1) * self.setup.cantidadComicsPorPagina)])
        self.statusThumbnails()
    def primero(self):
        self.paginaActual = 0
        self.loadPage()

    def siguiente(self):
        self.paginaActual+=1
        self.loadPage()

    def anterior(self):
        self.paginaActual -= 1
        self.loadPage()

    def ultimo(self):
        self.paginaActual = int((len(self.listaComics)/self.setup.cantidadComicsPorPagina))-1
        self.loadPage()

if __name__ == "__main__":
    ##    babel = BabelComicMainGui()
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    bc = BabelComicMainGui(root)
    bc.grid(sticky=(E,W,N,S))
    #root.wm_state('zoomed')
    root.title('Babel Comic Manager GitHub')
    root.attributes('-fullscreen', True)
    #bc.buscar(bc.statusBar)
    #w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    #root.geometry("%dx%d+0+0" % (w, h))
    #print(bc.panelComics.configure())
    bc.panelComics.configure(width=10)
    bc.update()
    root.mainloop()
