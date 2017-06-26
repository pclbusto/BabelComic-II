from tkinter import *
from tkinter import Tk, ttk
from tkinter import filedialog
import datetime
import _tkinter
from PIL import Image, ImageTk

from Entidades.ComicBooks import ComicBook
from Entidades.Volumes import Volume
import Entidades.Init


class ComicBookGui(Frame):
    def __init__(self, parent, comicBook, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        comic = self.comic = comicBook
        #self.serie = V().get(comicBook.serieId)
        notebook = ttk.Notebook(self)
        resumen = ttk.Frame(notebook)  # first page, which would get widgets gridded into it
        detalle = ttk.Frame(notebook)  # second page
        resumen.grid()
        detalle.grid()
        notebook.add(resumen, text='Resumen')
        notebook.add(detalle, text='Detalle')
        self.grid()
        notebook.grid()
        self.comic.openCbFile()
        comicBook.goto(0)
        im = Image.open(comicBook.getPage())
        size = (int(320 * 0.5), int(496 * 0.5))
        self.fImage = ImageTk.PhotoImage(im.resize(size))
        # self.cover = ttk.Label(resumen, image=self.fImage, anc1hor=CENTER, compound='top', text='No anda')
        # self.cover.grid(column=0, row=4, columnspan=2, rowspan=2, sticky=(N, W, E, S))
        self.cover = Canvas(resumen, width=size[0], height=size[1])
        self.cover.create_image((0, 0), image=self.fImage,anchor=NW)  # recordar que esto decide desde donde se muestra la imagen
        self.cover.create_rectangle((2, 2, 160, 248))
        self.cover.grid(column=0, row=0, rowspan=5)

        ttk.Label(resumen, text=comic.getNombreArchivo(False)).grid(column=1, row=0, sticky=(W, N))
        resumen.columnconfigure(1,weight=1)
        resumen.rowconfigure(1, weight=1)
        #tienen 9 lineas de alto y 59 chars de largo el texto
        resumenText = Text(resumen, width=50, height=9)
        if(comic.resumen):
            resumenText.insert(END, comic.resumen)
        resumenText.grid(column=1, row=1, sticky=(N,S,W,S), columnspan = 4)

        size = self.comic.getSize()/(1024*1024)

        ttk.Label(resumen, text="Tipo: "+self.comic.getTipo()+' '+str("%0.2f"%size)+'M' ).grid(column=0, row=5, sticky=(N, W))
        ttk.Label(resumen, text="Páginas: "+str(self.comic.getCantidadPaginas())).grid(column=0, row=6, sticky=(N, W))
        ttk.Label(resumen, text="Mi Valoración:").grid(column=1, row=5, sticky=(N, W))

        ttk.Label(resumen, text="Valoración de la comunidad:").grid(column=1, row=6, sticky=(N, W))
        donde = ttk.Label(resumen)
        donde.config(text="Dónde: {:.90s}".format(self.comic.path))
        donde.grid(column=0, row=7,columnspan=2, sticky=(N, W))
        donde.bind("<Button-1>",self.click)
        # los ttk no usans el text=''
        ttk.Label(detalle, text='Serie:').grid(column=0, row=0, sticky=(N, W))
        entrada = ttk.Entry(detalle, width=50)
        entrada.grid(column=0, row=1, padx=5, sticky=(N, W), columnspan=2)
        #entrada.insert(END, self.serie.nombre)

        ttk.Label(detalle, text='Volumen:').grid(column=2, row=0, sticky=(N, W))
        entrada = ttk.Entry(detalle, width=6)
        entrada.grid(column=2, row=1, padx=5, sticky=(N, W))
#        entrada.insert(END, self.comic.volumen)

        ttk.Label(detalle, text='Número:').grid(column=3, row=0, sticky=(N, W))
        entrada = Spinbox(detalle, from_=0, to=10000, width=6)
        entrada.grid(column=3, row=1, padx=5, sticky=(N, W))
        entrada.delete(0)
        entrada.insert(END, self.comic.numero)

        ttk.Label(detalle, text='de:').grid(column=4, row=0, sticky=(N, W))
        entrada = Spinbox(detalle, from_=0, to=10000, width=6)
        entrada.grid(column=4, row=1, padx=5, sticky=(N, W))
        entrada.delete(0)
        entrada.insert(END, self.serie.cantidadNumeros)

        ttk.Label(detalle, text='Título:').grid(column=0, row=2, sticky=(N, W))
        entrada = ttk.Entry(detalle, text='Título', width=50)
        entrada.grid(column=0, row=3, padx=5, sticky=(N, W), columnspan=2)
        entrada.insert(END, self.comic.titulo)

        ttk.Label(detalle, text='Fecha:').grid(column=2, row=2, sticky=(N, W))
        entrada = ttk.Entry(detalle, width=10)
        entrada.grid(column=2, row=3, padx=5, sticky=(N, W), columnspan=2)
        entrada.insert(END, self.comic.fechaTapa)

        ttk.Label(detalle, text='Arco Argumental:').grid(column=0, row=4, sticky=(N, W))
        entradaArco = ttk.Entry(detalle, text='', width=50)
        entradaArco.grid(column=0, row=5, padx=5, sticky=(N, W), columnspan=2)
        ttk.Label(detalle, text='Número:').grid(column=2, row=4, sticky=(N, W))
        entradaNumero = Spinbox(detalle, from_=0, to=10000, width=6)
        entradaNumero.grid(column=2, row=5, padx=5, sticky=(N, W))
        ttk.Label(detalle, text='de:').grid(column=3, row=4, sticky=(N, W))
        entradaDe = Spinbox(detalle, text='', from_=0, to=10000, width=6)
        entradaDe.grid(column=3, row=5, padx=5, sticky=(N, W))
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
        self.botonGuardar = ttk.Button(self, text='Guardar', command=self.guardar)
        self.botonGuardar.grid(column=0, sticky=(E))
        self.changed = False

    def click(self,event):
        window = Toplevel(self)
        window.columnconfigure(0, weight=1)

        window.wm_title(string='Path del comic')
        entry = ttk.Entry(window)
        entry.insert(0,self.comic.path)
        entry.grid(sticky=(W,E))
        help(event)
        print('{}x20+{}+{}'.format(len(self.comic.path)*6,event.x_root,event.y_root))
        window.geometry('{}x20+{}+{}'.format(len(self.comic.path)*6,event.x_root,event.y_root))

        print('Hola')
    def __Changed__(self, e, r, t):
        self.changed = True

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
