from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos
from Entidades.Publishers import Publishers
#import Entidades.Publishers.Publishers



class PublisherGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self.height=358
        self.width = 507
        self.labelId = Label(self, text="ID")
        self.labelId.grid(row=0,column=0, sticky=W ,padx=5,pady=5)
        self.entradaId = Entry(self)
        self.varID=StringVar()
        self.entradaId.grid(row=0,column=1, sticky=W + E,padx=5,pady=5, )
        self.botonLookupPublisher=Button(self)
        self.botonLookupPublisher.grid(row=0,column=3)
        self.pilImagenLookup=Iconos.Iconos.pilImagenLookup
        self.imageLookup = PIL.ImageTk.PhotoImage(self.pilImagenLookup)
        self.botonLookupPublisher.config(image=self.imageLookup)
        self.labelNombre= Label(self, text="Nombre")
        self.labelNombre.grid(row=1,column=0,sticky=W)
        self.entradaNombre = Entry(self)
        self.entradaNombre.grid(row=1, column=1, sticky=W + E,padx=5,pady=5)
        self.labelUrl = Label(self, text='Url')
        self.labelUrl.grid(row=2,sticky=W,padx=5,pady=5)
        self.entradaUrl = Entry(self)
        self.entradaUrl.grid(row=2, column=1, sticky=W+E ,padx=5,pady=5,columnspan=5)
        self.imageLogoCanvas = Canvas(self, width=154, height=154)
        self.imageLogoCanvas.grid(row=0, column=4, rowspan=4,sticky=E)

        self.pilImageLogo = Iconos.Iconos.pilImageLogo
        self.imageLogo = PIL.ImageTk.PhotoImage(self.pilImageLogo)
        self.imageLogoCanvas.create_image(77, 77, image=self.imageLogo)
        self.labelResumen = Label(self, text="Resumen")
        self.labelResumen.grid(row=5,column=0,sticky=W,padx=5,pady=5)
        self.pilImageExpansion = Iconos.Iconos.pilImageExpansion
        self.imageExpansion = PIL.ImageTk.PhotoImage(self.pilImageExpansion)

        self.botonExpansionResumen = Button(self,text="->",image=self.imageExpansion)
        self.botonExpansionResumen.grid(row=5,column=1,sticky=W)
        self.textoDescripcion = Label(self,wraplength=560,justify=LEFT,anchor=N)
        self.textoDescripcion.config(
            text='Descripcion')
        self.textoDescripcion.grid(row=6, column=0, padx=5,columnspan=5,sticky=W+E)

        self.frameBotonesNavegacion = Frame(self)
        self.frameBotonesNavegacion.grid(row=7,column=0,sticky=W)
        self.pilImageFirst=Iconos.Iconos.pilImageFirst
        self.imageFirst = PIL.ImageTk.PhotoImage(self.pilImageFirst)
        self.botonFirst = Button(self.frameBotonesNavegacion,image=self.imageFirst, command=self.getFirst)
        self.botonFirst.grid(row=0, column=0)
        self.pilImagePrev = Iconos.Iconos.pilImagePrev
        self.imagePrev = PIL.ImageTk.PhotoImage(self.pilImagePrev)
        self.botonPrev = Button(self.frameBotonesNavegacion,image=self.imagePrev, command=self.getPrev)
        self.botonPrev.grid(row=0, column=1)
        self.pilImageNext = Iconos.Iconos.pilImageNext
        self.imageNext = PIL.ImageTk.PhotoImage(self.pilImageNext)
        self.botonNext = Button(self.frameBotonesNavegacion,image=self.imageNext, command=self.getNext)
        self.botonNext.grid(row=0, column=2)
        self.pilImageLast = Iconos.Iconos.pilImageLast
        self.imageLast = PIL.ImageTk.PhotoImage(self.pilImageLast)
        self.botonLast = Button(self.frameBotonesNavegacion,image=self.imageLast, command=self.getLast)
        self.botonLast.grid(row=0, column=3)
        #
        self.frameBotonesAcciones = Frame(self)

        self.frameBotonesAcciones.grid(row=7, column=4, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Guardar")
        self.botonGuardar.grid(row=0, column=0, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Borrar", command=self.clearWindow)
        self.botonGuardar.grid(row=0, column=1, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Eliminar")
        self.botonGuardar.grid(row=0, column=2, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Cargar desde Web")
        self.botonGuardar.grid(row=0, column=3, sticky=E)
        self.publishersManager= Publishers.Publishers()

    def getFirst(self):
        publisher = self.publishersManager.getFirst()
        self._copyToWindow(publisher)

    def getLast(self):
        publisher = self.publishersManager.getLast()
        self._copyToWindow(publisher)

    def getNext(self):
        publisher = self.publishersManager.getNext()
        self._copyToWindow(publisher)

    def getPrev(self):
        publisher = self.publishersManager.getPrev()
        self._copyToWindow(publisher)

    def clearWindow(self):
        self.entradaId.delete(0, END)
        self.entradaNombre.delete(0, END)
        self.entradaUrl.delete(0, END)
        self.textoDescripcion.config(text='')

    def _copyToWindow(self,publisher):
        self.clearWindow()
        self.entradaId.insert(0, publisher.id_publisher)
        self.entradaNombre.insert(0, publisher.name)
        self.entradaUrl.insert(0, publisher.siteDetailUrl)
        self.textoDescripcion.config(text=publisher.deck)
if __name__ == '__main__':
    root = Tk()
    publisher = PublisherGui(root, width=507, height=358)
    publisher.pack()
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.mainloop()

