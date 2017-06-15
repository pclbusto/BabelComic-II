from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos


class PublisherGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self.height=358
        self.width = 507
        self.labelId = Label(self, text="ID")
        self.labelId.grid(row=0,column=0, sticky=W ,padx=5,pady=5)
        self.entradaId = Entry(self)
        self.entradaId.grid(row=0,column=1, sticky=W + E,padx=5,pady=5)
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
        self.entradaUrl.grid(row=2, column=1, sticky=W ,padx=5,pady=5)
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
        self.textoDescripcion = Label(self,wraplength=500,justify=LEFT)
        self.textoDescripcion.config(
            text='Originally known as "National Publications", DC is a publisher of comic books featuring iconic '
                 'characters and teams such as Superman, Batman, Wonder Woman, Green Lantern, the Justice League of '
                 'America, and the Teen Titans, and is considered the originator of the American superhero genre. DC, '
                 'along with rival Marvel Comics, is one of the "big two" American comic book publishers. DC '
                 'Entertainment is a subsidiary of Warner Brothers and its parent company Time Warner.'
                 'Originally known as "National Publications", DC is a publisher of comic books featuring iconic '
                 'characters and teams such as Superman, Batman, Wonder Woman, Green Lantern, the Justice League of '
                 'America, and the Teen Titans, and is considered the originator of the American superhero genre. DC, '
                 'along with rival Marvel Comics, is one of the "big two" American comic book publishers. DC '
                 'Entertainment is a subsidiary of Warner Brothers and its parent company Time Warner.')
        self.textoDescripcion.grid(row=6, column=0, padx=5,columnspan=5,sticky=W+E)

        self.frameBotonesNavegacion = Frame(self)
        self.frameBotonesNavegacion.grid(row=7,column=0,sticky=W)
        self.pilImageFirst=Iconos.Iconos.pilImageFirst
        self.imageFirst = PIL.ImageTk.PhotoImage(self.pilImageFirst)
        self.botonFirst = Button(self.frameBotonesNavegacion,image=self.imageFirst)
        self.botonFirst.grid(row=0, column=0)
        self.pilImagePrev = Iconos.Iconos.pilImagePrev
        self.imagePrev = PIL.ImageTk.PhotoImage(self.pilImagePrev)
        self.botonPrev = Button(self.frameBotonesNavegacion,image=self.imagePrev)
        self.botonPrev.grid(row=0, column=1)
        self.pilImageNext = Iconos.Iconos.pilImageNext
        self.imageNext = PIL.ImageTk.PhotoImage(self.pilImageNext)
        self.botonNext = Button(self.frameBotonesNavegacion,image=self.imageNext)
        self.botonNext.grid(row=0, column=2)
        self.pilImageLast = Iconos.Iconos.pilImageLast
        self.imageLast = PIL.ImageTk.PhotoImage(self.pilImageLast)
        self.botonLast = Button(self.frameBotonesNavegacion,image=self.imageLast)
        self.botonLast.grid(row=0, column=3)
        #
        self.frameBotonesAcciones = Frame(self)

        self.frameBotonesAcciones.grid(row=7, column=4, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Guardar")
        self.botonGuardar.grid(row=0, column=0, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Borrar")
        self.botonGuardar.grid(row=0, column=1, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Eliminar")
        self.botonGuardar.grid(row=0, column=2, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Cargar desde Web")
        self.botonGuardar.grid(row=0, column=3, sticky=E)

if __name__ == '__main__':
    root = Tk()
    publisher = PublisherGui(root, width=507, height=358)
    publisher.pack()
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.mainloop()

