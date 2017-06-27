from tkinter import *
from tkinter import Tk, ttk
from Gui.FrameMaestro import FrameMaestro
from PIL import Image, ImageTk

from Entidades.ComicBooks import ComicBook
from Entidades.Volumes import Volume
import Entidades.Init


class ComicBookGui(FrameMaestro):
    def __init__(self, parent, comicBook, cnf={}, **kw):
        FrameMaestro.__init__(self, parent, cnf, **kw)
        comic = self.comic = comicBook
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


        ttk.Label(resumen, text="Páginas: "+str(self.comic.getCantidadPaginas())).grid(column=0, row=6, sticky=(N, W))
        ttk.Label(resumen, text="Mi Valoración:").grid(column=1, row=5, sticky=(N, W))

        ttk.Label(resumen, text="Valoración de la comunidad:").grid(column=1, row=6, sticky=(N, W))
        donde = ttk.Label(resumen)
        donde.config(text="Dónde: {:.90s}".format(self.comic.path))
        donde.grid(column=0, row=7,columnspan=2, sticky=(N, W))
        donde.bind("<Button-1>",self.click)
        ttk.Label(detalle, text='Serie:').grid(column=0, row=0, sticky=(N, W))
        self.entradaSerie = ttk.Entry(detalle, width=50)
        self.entradaSerie.grid(column=0, row=1, padx=5, sticky=(N, W), columnspan=2)
        #entrada.insert(END, self.serie.nombre)

        ttk.Label(detalle, text='Volumen:').grid(column=2, row=0, sticky=(N, W))
        self.entradaVolume = ttk.Entry(detalle, width=6)
        self.entradaVolume.grid(column=2, row=1, padx=5, sticky=(N, W))
#        entrada.insert(END, self.comic.volumen)

        ttk.Label(detalle, text='Número:').grid(column=3, row=0, sticky=(N, W))
        self.entradaNumero = Spinbox(detalle, from_=0, to=10000, width=6)
        self.entradaNumero.grid(column=3, row=1, padx=5, sticky=(N, W))
        self.entradaNumero.delete(0)
        self.entradaNumero.insert(END, self.comic.numero)

        ttk.Label(detalle, text='de:').grid(column=4, row=0, sticky=(N, W))
        self.entradaDe = Spinbox(detalle, from_=0, to=10000, width=6)
        self.entradaDe.grid(column=4, row=1, padx=5, sticky=(N, W))
        self.entradaDe.delete(0)

        ttk.Label(detalle, text='Título:').grid(column=0, row=2, sticky=(N, W))
        self.entradaTitulo = ttk.Entry(detalle, text='Título', width=50)
        self.entradaTitulo.grid(column=0, row=3, padx=5, sticky=(N, W), columnspan=2)
        self.entradaTitulo.insert(END, self.comic.titulo)

        ttk.Label(detalle, text='Fecha:').grid(column=2, row=2, sticky=(N, W))
        entrada = ttk.Entry(detalle, width=10)
        entrada.grid(column=2, row=3, padx=5, sticky=(N, W), columnspan=2)
        entrada.insert(END, self.comic.fechaTapa)

        ttk.Label(detalle, text='Arco Argumental:').grid(column=0, row=4, sticky=(N, W))
        self.entradaArco = ttk.Entry(detalle, text='', width=50)
        self.entradaArco.grid(column=0, row=5, padx=5, sticky=(N, W), columnspan=2)
        ttk.Label(detalle, text='Número:').grid(column=2, row=4, sticky=(N, W))
        self.entradaArcoArgumentalNumero = Spinbox(detalle, from_=0, to=10000, width=6)
        self.entradaArcoArgumentalNumero.grid(column=2, row=5, padx=5, sticky=(N, W))
        ttk.Label(detalle, text='de:').grid(column=3, row=4, sticky=(N, W))
        self.entradaArcoArgumentalDe = Spinbox(detalle, text='', from_=0, to=10000, width=6)
        self.entradaArcoArgumentalDe.grid(column=3, row=5, padx=5, sticky=(N, W))

        # if comic.tieneArcoAlterno():
        #     entradaArco.insert(END, ArcosArgumentales().get(comic.seriesAlternasNumero[0][0]).nombre)
        #     entradaNumero.delete(0)
        #     entradaNumero.insert(END, comic.seriesAlternasNumero[0][1])
        #     arco = ArcosArgumentales().get(comic.seriesAlternasNumero[0][0])
        #     entradaDe.delete(0)
        #     entradaDe.insert(END, arco.getCantidadTitulos())

        notebook.select(0)
        self.entries = {}
        self.variables = {}
        self.varaible = StringVar(self).trace(mode='w', callback=self.__Changed__)
        self.changed = False
        self.loadComic()
    def loadComic(self):
        self.comic.openCbFile()
        self.comic.goto(0)
        im = Image.open(self.comic.getPage())
        size = (int(320 * 0.5), int(496 * 0.5))
        self.fImage = ImageTk.PhotoImage(im.resize(self.size))
        self.cover.create_image((0, 0), image=self.fImage,
                                anchor=NW)  # recordar que esto decide desde donde se muestra la imagen
        self.labelNombre.configure(text=self.comic.getNombreArchivo(False))
        if (self.comic.resumen):
            self.resumenText.insert(END, self.comic.resumen)
        self.labelTipoyTamanio.configure(
            text="Tipo: " + self.comic.getTipo() + ' '  + str("%0.2f" % (self.comic.getSize() / (1024 * 1024))) + 'M')
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
        session.query(ComicBook).first()
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

    comic = session.query(ComicBook.ComicBook).filter(ComicBook.ComicBook.path == 'E:\\Comics\\DC\\new 52\\DC New 52\\Aquaman\\Aquaman #018.cbr').first()
    comic.create('E:\\Comics\\DC\\new 52\\DC New 52\\Aquaman\\Aquaman #018.cbr')
    print(comic)
    root = Tk()
    frameComic = ComicBookGui(root, comic)
    frameComic.grid(padx=5, pady=5, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
