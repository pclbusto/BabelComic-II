from Gui.ComicBookGui import ComicBookGui
from Gui.ComicVineCatalogerGui import ComicCatalogerGui
from Gui.ConfigGui import ConfigGui
from Gui.ComicVisorGui import ComicVisorGui
from PIL import Image, ImageTk
from iconos.Iconos import Iconos
from Gui.PanelThumbnailComics import PanelThumbnailComics
import threading
from tkinter import Tk, ttk
from tkinter import *
import Entidades.Init

from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Setups.Setup import Setup

class BabelComicMainGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self.barraHerramientas = Frame(parent)
        self.barraHerramientas.grid(column=0, row=0, sticky=(E, W))
        self.barraHerramientas.config()
        self.barraHerramientas.columnconfigure(0, weight=1)
        self.barraHerramientas.rowconfigure(1, weight=1)
        self.setup = Entidades.Init.Session().query(Setup).first()
        self.root = parent
        pilImagenLookup = Iconos.pilImagenLookup
        imagenLookup = ImageTk.PhotoImage(pilImagenLookup)

        self.pilImageFirst = Iconos.pilImageFirst
        self.imageFirst = ImageTk.PhotoImage(self.pilImageFirst)
        self.pilImagePrev = Iconos.pilImagePrev
        self.imagePrev = ImageTk.PhotoImage(self.pilImagePrev)
        self.pilImageNext = Iconos.pilImageNext
        self.imageNext = ImageTk.PhotoImage(self.pilImageNext)
        self.pilImageLast = Iconos.pilImageLast
        self.imageLast = ImageTk.PhotoImage(self.pilImageLast)

        self.session = Entidades.Init.Session()
        self.listaComics = []
        self.consulta = ComicBook.path.like("%%")

        # opciones de barra de tareas
        self.buscarEntry = ttk.Entry(self.barraHerramientas)

        image = imagenLookup
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
        self.treeListas.grid()
        self.biblioteca = ''
        self.biblioteca = self.treeListas.insert('', 0, 'Biblioteca', text='Biblioteca')
        self.editoriales = self.treeListas.insert(self.biblioteca, 'end', 'Editoriales', text='Editoriales')
        self.treeListas.insert(self.editoriales, 'end', 'DC Comics', text='DC Comics')

        # creamos menu popup para agregar vistas
        self. popup = Menu(self.treeListas, tearoff=0)
        self.popup.add_command(label="Agregar Lista")  # , command=next) etc...
        self.treeListas.bind("<Button-3>", self.popupListas)

        self.treeListas.bind("<<TreeviewSelect>>", self.selectVista)

        self.panelGrillaComics = Frame(self.panedWindow)
        self.panelGrillaComics.columnconfigure(0, weight=1)
        self.panelGrillaComics.rowconfigure(0, weight=1)
        self.panelGrillaComics.grid(sticky=(N, S, W, E))

        self.scrollbar = ttk.Scrollbar(self.panelGrillaComics)
        self.scrollbar.grid(column=1, row=0, sticky=(S, N))

        self.panelComics = PanelThumbnailComics(self.panelGrillaComics, yscrollcommand=self.scrollbar.set)
        self.panelComics.bind("<Configure>", self.on_resize)

        self.scrollbar.config(command=self.panelComics.yview)
        #    treeComics.grid()
        self.panelComics.bind('<MouseWheel>', self.scrollupMouse)
        parent.bind('<Down>', self.scrollupKeyboard)
        parent.bind('<Key>', self.scrollupKeyboard)

        # creamos menu popup para abrir el catalogador el visor el editor de info y calcular el thumnails de nuevo
        self.popupThumbnails = Menu(self.panelComics, tearoff=0)
        self.popupThumbnails.add_command(label="Info comic", command=self.openComicEditor)  # , command=next) etc...
        self.popupThumbnails.add_command(label="Leer comic", command=self.openBabelComicVisor)  # , command=next) etc...
        self.popupThumbnails.add_command(label="Catalogar comic", command=self.openComicVine)  # , command=next) etc...
        self.popupThumbnails.add_separator()
        self.popupThumbnails.add_command(label="Refresh Thumbnail",
                                    command=self.panelComics.recreateThumbnails)  # , command=next) etc...
        self.panelComics.bind("<Button-3>", self.popupPanelThumbnails)
        # popup.add_separator()
        # popup.add_command(label="Home")



        # treeComics.heading('serie', text='Serie',command=lambda col='serie': sortby(col))
        # treeComics.heading('numero', text='Número',command=lambda col='numero': sortby(col))
        # treeComics.heading('archivo', text='Archivo',command=lambda col='archivo': sortby(col))
        # treeComics.heading('nombre', text='Nombre', command=lambda col='nombre': sortby(col))
        # treeComics.config(show='headings')  # tree, headings

        parent.bind('<Control-c>', lambda x: self.openComicEditor())
        parent.bind('<Control-v>', lambda x: self.openComicVine())
        parent.bind('<Control-b>', lambda x: self.openBabelComicVisor())

        parent.bind('<Control-s>', self.openBabelComicConfig)
        parent.bind('<Control-x>', self.openBabelComicScanner)

        self.statusBar = StringVar()
        ttk.Label(parent, textvariable=self.statusBar, anchor="e", relief='groove').grid(column=0, row=3, sticky=(W, E))

        self.panelComics.grid(column=0, row=0, sticky=(N, S, W, E))
        self.panedWindow.add(self.treeListas)
        self.panedWindow.add(self.panelGrillaComics)
        self.paginaActual=0
        # menu
        # comics = ComicBooks()
        self.buscar(self.statusBar)
        cantidadColumnas = 4
        # variables globales
        desc = False
    def salir(self):
        self.root.destroy()
    def CheckThumbnailsGeneration(self):
        while self.panelComics.threadLoadAndCreateThumbnails.isAlive():
            if self.panelComics.cantidadThumnailsAGenerar>0:
                self.statusBar.set('Porcentaje de carga de thumnails: {1:.2f} Cantidad de Registros: {0:}'.format(len(self.listaComics),100*(self.panelComics.cantidadThumnailsGenerados/self.panelComics.cantidadThumnailsAGenerar)))

        print('generados {} totales {} porcentaje: '.format(self.panelComics.cantidadThumnailsGenerados, self.panelComics.cantidadThumnailsAGenerar))
                                                                  #,100 * (panelComics.cantidadThumnailsGenerados / panelComics.cantidadThumnailsAGenerar)))
        self.statusBar.set('Porcentaje de carga de thumnails: {1:.2f} Cantidad de Registros: {0:}'.format(
            len(self.listaComics),
            100 * (self.panelComics.cantidadThumnailsGenerados / self.panelComics.cantidadThumnailsAGenerar)))

    def statusThumbnails(self):
        threadCheckThumbnailsGeneration = threading.Thread(target=self.CheckThumbnailsGeneration)
        threadCheckThumbnailsGeneration.start()

    def buscar(self, statusBar):
        listaAtributos = [ComicBook.path]
        filter = (listaAtributos[0].like(("%%")))
        self.listaComics = self.session.query(ComicBook).filter(filter).filter(ComicBook.path.like("%legends%")).order_by(ComicBook.path.asc()).all()
        self.paginaActual = 0
        busqueda = self.buscarEntry.get()
        if not busqueda:
            busqueda='%%'
            #self.buscarEntry.insert(0,busqueda)
            self.panelComics.loadComics(self.listaComics[(self.paginaActual*self.setup.cantidadComicsPorPagina) :((self.paginaActual+1)*self.setup.cantidadComicsPorPagina)])
        self.statusThumbnails()
        statusBar.set('Cantidad de Registros: {} / {}'.format(30,len(self.listaComics)))



    def enterEventEntryBuscar(self):
        self.buscar(self.statusBar)


    def openComicEditor(self):
        if (self.panelComics.comicActual):
            comic = self.session.query(ComicBook).filter(ComicBook.path==self.panelComics.getComicActual().path).first()
            #comic = comics.get(panelComics.getComicActual().path)
            ventana = Toplevel()
            frameComic = ComicBookGui(ventana, comic)
            frameComic.grid()
    ##        frameComic.grid(padx=5, pady=5, sticky=(N, W, E, S))
    ##        frameComic.columnconfigure(0, weight=1)
    ##        frameComic.rowconfigure(0, weight=1)


    def openBabelComicConfig(self, event):
        window = Toplevel(root)
        window.title('Babel Comics Configuración')
        config = BabelComicConfigGui(window)
        config.grid(sticky=(N, S, W, E))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.grid()

    def openBabelComicVisor(self):
        print("estamos pro abrir")
        #if (panelComics.comicActual):
        print("abriendo")
        comic = self.panelComics.getComicActual()
        visor = ComicVisorGui(root, comic,height = root.winfo_screenheight(),width = root.winfo_screenwidth())
        visor.title = ('Babel Comics Visor')
        visor.wm_state('zoomed')

    def openComicVine(self):
        if (panelComics.comicActual):
            window = Toplevel()
            window.title('Catalogador')
            window.geometry('+0+0')
            comics = ComicBooks()
            comic = panelComics.getComicActual()

            cvs = ComicCatalogerGui(window, comic)
            #cvs.grid(sticky=(N, W, S, E))
            cvs.grid()
            window.columnconfigure(0, weight=1)
            window.rowconfigure(0, weight=1)
            root.wait_window(window)

    def sortby(self):
        grillaSeries.heading('start_year', command=lambda col='AnioInicio': self.sortby(col))
        if desc:
            self.buscarSerie('order by ' + col + ' desc')

    def openBabelComicScanner(event):
        scanner = BabelComicScannerGui(root)

    def scrollupMouse(self, event):
        self.panelComics.yview_scroll(-1 * (int)(event.delta / 120), "units")

    def scrollupKeyboard(self, event):
        print(event.keycode)
        if (event.keycode == 116) | (event.keycode == 117) | (event.keycode == 34)| (event.keycode == 40):
            panelComics.yview_scroll(1, "units")
            print('para abajo')
        if (event.keycode == 112) | (event.keycode == 111) | (event.keycode == 33)| (event.keycode == 38):
            panelComics.yview_scroll(-1, "units")
            print('para abajo')
        #el 114 es en linux y el 39 en windows
        if (event.keycode==114)|(event.keycode==39):#derecha
            panelComics.nextComic()
        # el 113 es en linux y el 37 en windows
        if (event.keycode == 113)|(event.keycode==37):  # izquierda
            panelComics.prevComic()

    def on_resize(self,event):
        #solo refrescar cuando el tamañio sume o reste columnas
        self.panelComics.cantidadColumnas = int(event.width/(self.panelComics.size[0] + self.panelComics.space))
        #self.panelComics.loadComics(self.listaComics[(self.paginaActual*self.setup.cantidadComicsPorPagina) :((self.paginaActual+1)*self.setup.cantidadComicsPorPagina)])
        self.loadPage()
        #print(event.width/(self.size[0] + self.panelComics.space))

    def refrescar(self):
        #solo refrescar cuando el tamañio sume o reste columnas
        #if cantidadColumnas!=int(event.width/(panelComics.size[0] + panelComics.space)):
        panelComics.loadComics(comics.listaConsulta)
        #print(event.width/(panelComics.size[0] + panelComics.space))

    def popupListas(self,event):
        # display the popup menu
        try:
            self.popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            popup.grab_release()

    def popupPanelThumbnails(self,event):
        try:
            self.popupThumbnails.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.popupThumbnails.grab_release()

    def selectVista(self,event):
        print("SELECON: "+self.treeListas.selection()[0])
        self.comics.vistaConsultas = self.treeListas.selection()[0]

    def loadPage(self):
        if len(self.listaComics)<(self.paginaActual + 1) * self.setup.cantidadComicsPorPagina:
            print("cantidad:"+str(len(self.listaComics)))
            print("indice menor:" + str(self.paginaActual * self.setup.cantidadComicsPorPagina))
            print("indice mayor:" + str(len(self.listaComics)-1))

            self.panelComics.loadComics(self.listaComics[(self.paginaActual * self.setup.cantidadComicsPorPagina):len(self.listaComics)-1])
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
    #w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    #root.geometry("%dx%d+0+0" % (w, h))
    root.mainloop()
