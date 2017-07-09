from tkinter import *
from tkinter import Tk, ttk
from Gui.FrameMaestro import FrameMaestro
from PIL import Image, ImageTk
from datetime import date
from Entidades.ComicBooks import ComicBook
from Entidades.Volumes.Volume import Volume
import Entidades.Init
from Gui.ComicVineCatalogerGui import ComicCatalogerGui
from Entidades.ArcosArgumentales.ArcoArgumental import ArcoArgumental
from Gui.ComicVisorGui import ComicVisorGui

class ComicBookGui(FrameMaestro):
    def __init__(self, parent, comicBook=None, cnf={}, **kw):
        FrameMaestro.__init__(self, parent, cnf, **kw)
        panelPrincipal = self.getPanelPrincipal()
        notebook = ttk.Notebook(panelPrincipal)
        resumen = ttk.Frame(notebook)  # first page, which would get widgets gridded into it
        detalle = ttk.Frame(notebook)  # second page
        resumen.grid()
        detalle.grid()
        notebook.add(resumen, text='Resumen')
        notebook.add(detalle, text='Detalle')
        self.grid()
        notebook.grid()
        self.size = (int(320 * 0.5), int(496 * 0.5))
        self.cover = Canvas(resumen, width=self.size[0], height=self.size[1])
        self.cover.create_rectangle((2, 2, 160, 248))
        self.cover.grid(column=0, row=0, rowspan=5)
        self.labelNombre = ttk.Label(resumen)
        self.labelNombre.grid(column=1, row=0, sticky=(W, N))
        resumen.columnconfigure(1,weight=1)
        resumen.rowconfigure(1, weight=1)
        #tienen 9 lineas de alto y 59 chars de largo el texto
        self.resumenText = Text(resumen, width=50, height=9)
        self.resumenText.grid(column=1, row=1, sticky=(N,S,W,S), columnspan = 4)
        self.labelTipoyTamanio =  ttk.Label(resumen)
        self.labelTipoyTamanio.grid(column=0, row=5, sticky=(N, W))
        self.labelPaginas =  ttk.Label(resumen)
        self.labelPaginas.grid(column=0, row=6, sticky=(N, W))
        self.labelMiValoracion =ttk.Label(resumen)
        self.labelMiValoracion.grid(column=1, row=5, sticky=(N, W))
        self.labelValorecionComunidad=ttk.Label(resumen)
        self.labelValorecionComunidad.grid(column=1, row=6, sticky=(N, W))
        self.labelDonde = ttk.Label(resumen)
        self.labelDonde.grid(column=0, row=7,columnspan=2, sticky=(N, W))
        self.labelDonde.bind("<Button-1>",self.click)

        self.labelVolume =  ttk.Label(detalle, text='Volumen:').grid(column=0, row=0, sticky=(N, W))
        # self.labelDonde.bind("<Button-1>",self.zoom)
        self.entradaVolume = ttk.Entry(detalle, width=50)
        self.entradaVolume.grid(column=0, row=1, padx=5, sticky=(N, W), columnspan=2)

        ttk.Label(detalle, text='Nro Volumen:').grid(column=2, row=0, sticky=(N, W))
        self.entradaNroVolume = ttk.Entry(detalle, width=10)
        self.entradaNroVolume.grid(column=2, row=1, padx=5, sticky=(N, W),columnspan=2)

        ttk.Label(detalle, text='Número:').grid(column=3, row=0, sticky=(N, W))
        self.entradaNumero = Spinbox(detalle, from_=0, to=10000, width=6)
        self.entradaNumero.grid(column=3, row=1, padx=5, sticky=(N, W))

        ttk.Label(detalle, text='de:').grid(column=4, row=0, sticky=(N, W))
        self.entradaDe = Spinbox(detalle, from_=0, to=10000, width=6)
        self.entradaDe.grid(column=4, row=1, padx=5, sticky=(N, W))

        ttk.Label(detalle, text='Título:').grid(column=0, row=2, sticky=(N, W))
        self.entradaTitulo = ttk.Entry(detalle, width=50)
        self.entradaTitulo.grid(column=0, row=3, padx=5, sticky=(N, W), columnspan=2)

        ttk.Label(detalle, text='Fecha:').grid(column=2, row=2, sticky=(N, W))
        self.entradaFecha= ttk.Entry(detalle, width=10)
        self.entradaFecha.grid(column=2, row=3, padx=5, sticky=(N, W), columnspan=2)

        ttk.Label(detalle, text='Arco Argumental:').grid(column=0, row=4, sticky=(N, W))
        self.entradaArco = ttk.Entry(detalle, text='', width=50)
        self.entradaArco.grid(column=0, row=5, padx=5, sticky=(N, W), columnspan=2)
        ttk.Label(detalle, text='Número:').grid(column=2, row=4, sticky=(N, W))
        self.entradaArcoArgumentalNumero = Spinbox(detalle, from_=0, to=10000, width=6)
        self.entradaArcoArgumentalNumero.grid(column=2, row=5, padx=5, sticky=(N, W))
        ttk.Label(detalle, text='de:').grid(column=3, row=4, sticky=(N, W))
        self.entradaArcoArgumentalDe = Spinbox(detalle, text='', from_=0, to=10000, width=6)
        self.entradaArcoArgumentalDe.grid(column=3, row=5, padx=5, sticky=(N, W))

        #agregamos otro boton mas
        self.botonComicVine = Button(self.frameBotonesAcciones, text="Comic Vine",command=self.abrirCatalogadorComicVine)
        self.botonComicVine.grid(row=0, column=4, sticky=E)
        self.botonVisorComic = Button(self.frameBotonesAcciones, text="Leer Comic",
                                     command=self.openVisorComic)
        self.botonVisorComic.grid(row=0, column=5, sticky=E)

        notebook.select(0)
        self.entries = {}
        self.variables = {}
        self.varaible = StringVar(self).trace(mode='w', callback=self.__Changed__)
        self.changed = False
        if comicBook is not None:
            self.setComic(comicBook)
            self.loadComic()
        else:
            self.getFirst()

    def openVisorComic(self):
        #ventana = Toplevel()
        ComicVisorGui(None, self.comic)

    def zoom(self,event):
        print("Zoooom")

    def abrirCatalogadorComicVine(self):
        window = Toplevel()
        cvc = ComicCatalogerGui(window,self.comic)
        cvc.grid(sticky=(E, W, S, N))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.geometry("+0+0")
        window.wm_title(string="Catalogador Comic Vine")
        self.wait_window(window)

    def getLast(self):
        super().getLast()
        session = Entidades.Init.Session()
        comic = session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.desc()).first()
        if comic is not None:
            self.setComic(comic)
            self.loadComic()

    def getPrev(self):
        super().getPrev()
        if self.comic is not None:
            session = Entidades.Init.Session()
            comic = session.query(ComicBook.ComicBook).filter(ComicBook.ComicBook.path<self.comic.path).order_by(ComicBook.ComicBook.path.desc()).first()
            if comic is not None:
                self.setComic(comic)
                self.loadComic()
        else:
            self.getFirst()

    def getNext(self):
        super().getNext()
        if self.comic is not None:
            session = Entidades.Init.Session()
            comic = session.query(ComicBook.ComicBook).filter(ComicBook.ComicBook.path>self.comic.path).order_by(ComicBook.ComicBook.path.asc()).first()
            if comic is not None:
                self.setComic(comic)
                self.loadComic()
        else:
            self.getLast()

    def setComic(self,comicBook):
        self.comic = comicBook

    def loadComic(self):
        self.comic.openCbFile()
        self.comic.goto(0)
        im = Image.open(self.comic.getPage())
        size = (int(320 * 0.5), int(496 * 0.5))
        self.fImage = ImageTk.PhotoImage(im.resize(self.size,Image.BICUBIC))
        self.cover.create_image((0, 0), image=self.fImage,
                                anchor=NW)  # recordar que esto decide desde donde se muestra la imagen
        self.labelNombre.configure(text=self.comic.getNombreArchivo(False))
        self.resumenText.delete(1.0,END)
        if (self.comic.resumen):
            self.resumenText.insert(END, self.comic.resumen)
        self.labelTipoyTamanio.configure(
            text="Tipo: " + self.comic.getTipo() + ' '  + str("%0.2f" % (self.comic.getSize() / (1024 * 1024))) + 'M')
        self.labelPaginas.configure(text="Páginas: " + str(self.comic.getCantidadPaginas()))
        self.labelMiValoracion.configure(text="Mi Valoración:")
        self.labelValorecionComunidad.configure(text="Valoración de la comunidad:")
        self.labelDonde.config(text="Dónde: {:.90s}".format(self.comic.path))
        #limpiamos los campos tenga o no volumen para no dejar el anterior
        self.entradaVolume.delete(0,END)
        self.entradaNroVolume.delete(0,END)
        self.entradaDe.delete(0,END)
        session = Entidades.Init.Session()
        if self.comic.volumeId != '':
            volume = session.query(Volume).filter(Volume.id==self.comic.volumeId).first()
            self.entradaVolume.insert(END, volume.nombre)
            self.entradaNroVolume.insert(END, volume.deck)
            self.entradaDe.insert(END, volume.cantidadNumeros)
        self.entradaNumero.delete(0,END)
        self.entradaNumero.insert(END, self.comic.numero)
        self.entradaTitulo.delete(0,END)
        self.entradaTitulo.insert(END, self.comic.titulo)
        self.entradaFecha.delete(0,END)
        self.entradaFecha.insert(END, date.fromordinal(self.comic.fechaTapa))
        self.entradaArco.delete(0, END)
        self.entradaArcoArgumentalNumero.delete(0,END)
        self.entradaArcoArgumentalDe.delete(0,END)

        if self.comic.tieneArcoAlterno():
            arco = session.query(ArcoArgumental).get(self.comic.arcoArgumentalId)
            self.entradaArco.insert(0, arco.nombre)
            self.entradaArcoArgumentalNumero.insert(0, self.comic.arcoArgumentalNumero)
            self.entradaArcoArgumentalDe.insert(0, arco.getIssuesCount())

    def click(self,event):
        help(Toplevel)
        window = Toplevel(self)
        window.columnconfigure(0, weight=1)

        window.wm_title(string='Path del comic')
        entry = ttk.Entry(window)
        entry.insert(0,self.comic.path)
        entry.grid(sticky=(W,E))
        print('{}x20+{}+{}'.format(len(self.comic.path)*6,event.x_root,event.y_root))
        window.geometry('{}x20+{}+{}'.format(len(self.comic.path)*6,event.x_root,event.y_root))


    def __Changed__(self, e, r, t):
        self.changed = True

    def getFirst(self):
        session = Entidades.Init.Session()
        comic = session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()).first()
        if comic is not None:
            print(comic)
            self.setComic(comic)
            self.loadComic()



    def guardar(self):
        if (self.changed):
            self.comic.path = self.entries['Path'].get()
            self.comic.titulo = self.entries['Título'].get()
            self.comic.volumen = self.entries['Volumen'].get()
            self.comic.numero = self.entries['Número'].get()
            self.comic.cantidadPaginas = self.entries['Cantidad de Paginas'].get()



if (__name__ == '__main__'):
    session = Entidades.Init.Session()
    comic =ComicBook.ComicBook()
    # path = 'E:\\Comics\\DC\\new 52\\DC New 52\\Aquaman\\Aquaman #011.cbr'
    # comic = session.query(ComicBook.ComicBook).filter(ComicBook.ComicBook.path == path).first()
    root = Tk()
    frameComic = ComicBookGui(root)
    frameComic.grid(padx=5, pady=5, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
