from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk



class PublisherGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self.frameInfoPrincipal=Frame(self)
        self.frameInfoPrincipal.grid(row=0, column=0, sticky=W + E + S + N)
        self.frameInfoPrincipal.columnconfigure(0, weight=1)
        self.frameInfoPrincipal.columnconfigure(1, weight=1)
        self.frameInfoPrincipal.columnconfigure(2, weight=1)

        self.labelId = Label(self.frameInfoPrincipal, text="ID")
        self.labelId.grid(row=0,column=0,sticky=W,padx=5,pady=5)
        self.entradaId = Entry(self.frameInfoPrincipal)
        self.entradaId.grid(row=0,column=1,padx=5,pady=5,sticky=W+E)
        self.botonLookupPublisher=Button(self.frameInfoPrincipal)
        self.botonLookupPublisher.grid(row=0,column=2,padx=5,pady=5,sticky=W)
        self.pilImagenLookup=PIL.Image.open("/home/pedro/Documentos/pycharmProjects/BabelComic-II/iconos/Magnifying-Glass-icon.png")
        self.imageLookup = PIL.ImageTk.PhotoImage(self.pilImagenLookup)
        self.botonLookupPublisher.config(image=self.imageLookup)
        self.labelNombre= Label(self.frameInfoPrincipal, text="Nombre")
        self.labelNombre.grid(row=1, column=0, sticky=W,padx=5,pady=5)
        self.entradaNombre = Entry(self.frameInfoPrincipal)
        self.entradaNombre.grid(row=1, column=1, sticky=W + E,padx=5,pady=5)
        self.labelUrl = Label(self.frameInfoPrincipal, text='Url')
        self.labelUrl.grid(row=2,sticky=W,padx=5,pady=5)
        self.entradaUrl = Entry(self.frameInfoPrincipal)
        self.entradaUrl.grid(row=2, column=1, sticky=W + E,padx=5,pady=5)

        self.imageLogoCanvas = Canvas(self, width=154, height=154)
        self.imageLogoCanvas.grid(row=0, column=1, rowspan=2,sticky=E)
        self.pilImageLogo = PIL.Image.open(
            "/home/pedro/Documentos/pycharmProjects/BabelComic-II/iconos/Logo-Editorial.png")
        self.imageLogo = PIL.ImageTk.PhotoImage(self.pilImageLogo)
        self.imageLogoCanvas.create_image(77, 77, image=self.imageLogo)


        self.labelDescripcion = Label(self, text="Descripción")
        self.labelDescripcion.grid(row=1,column=0,sticky=W,padx=5,pady=5)
        self.entradaDescripcion = Text(self)
        self.entradaDescripcion.grid(row=2, column=0, padx=5,columnspan=5,sticky=W+E)
        self.frameBotonesNavegacion = Frame(self)
        self.frameBotonesNavegacion.grid(row=3,column=0,sticky=W)
        self.botonFirst = Button(self.frameBotonesNavegacion,text="<<")
        self.botonFirst.grid(row=0, column=0)
        self.botonPrev = Button(self.frameBotonesNavegacion,text="<")
        self.botonPrev.grid(row=0, column=1)
        self.botonNext = Button(self.frameBotonesNavegacion,text=">")
        self.botonNext.grid(row=0, column=2)
        self.botonLast = Button(self.frameBotonesNavegacion,text=">>")
        self.botonLast.grid(row=0, column=3)

        self.frameBotonesAcciones = Frame(self)
        self.frameBotonesAcciones.grid(row=3,column=1)
        self.frameBotonesAcciones.grid(row=3, column=1, sticky=E)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Guardar")
        self.botonGuardar.grid(row=0, column=0)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Borrar")
        self.botonGuardar.grid(row=0, column=1)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Eliminar")
        self.botonGuardar.grid(row=0, column=2)
        self.botonGuardar = Button(self.frameBotonesAcciones, text="Cargar desde Web")
        self.botonGuardar.grid(row=0, column=3)

        self.columnconfigure(0,weight=4)
        self.width =500
        self.height = 500

if __name__ == '__main__':
    root = Tk()
    publisher = PublisherGui(root, width=768, height=576)
    publisher.pack()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
