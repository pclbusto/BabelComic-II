from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos
from Entidades.Volumes.Volume import Volume
from Entidades.Publishers.Publisher import Publisher
from PIL import Image, ImageTk


from Gui.FrameMaestro import FrameMaestro
import Entidades.Init

class VolumeGui(FrameMaestro):
    def __init__(self, parent, volume=None, cnf={}, **kw):
        FrameMaestro.__init__(self, parent, cnf, **kw)
        self.pilImagenLookup = Iconos.Iconos.pilImagenLookup
        self.imagenLookup = PIL.ImageTk.PhotoImage(self.pilImagenLookup)
        self.pilImageExpansion = Iconos.Iconos.pilImageExpansion
        self.imageExpansion = PIL.ImageTk.PhotoImage(self.pilImageExpansion)
        self.pilImageLogo = Iconos.Iconos.pilImageLogo
        self.imageLogo = PIL.ImageTk.PhotoImage(self.pilImageLogo)
        self.session = Entidades.Init.Session()
        self.size = (int(320 * 0.5), int(496 * 0.5))

        self.panelPrincipal = self.getPanelPrincipal()
        ttk.Label(self.panelPrincipal, text='ID').grid(column=0,row=0, sticky=W)
        self.entradaId = ttk.Entry(self.panelPrincipal)
        self.entradaId.grid(column=1, row=0, padx=5, pady=2, sticky=W)
        self.botonLookupVolume = ttk.Button(self.panelPrincipal, image=self.imagenLookup)
        self.botonLookupVolume.grid(column=2, row = 0, padx=5, pady=2, sticky=W)

        ttk.Label(self.panelPrincipal, text='Nombre').grid(column=0,row=1, sticky=W)
        self.entradaNombre = ttk.Entry(self.panelPrincipal)
        self.entradaNombre.grid(column=1, row=1, padx=5, pady=2, columnspan=2, sticky=W)

        ttk.Label(self.panelPrincipal, text='Url').grid(column=0, row=2, sticky=W)
        self.entradaUrl = ttk.Entry(self.panelPrincipal)
        self.entradaUrl .grid(column=1, row=2, padx=5, pady=2, sticky=W)

        ttk.Label(self.panelPrincipal, text='Editorial').grid(column=0, row=3, sticky=W)
        self.entradaEditorial = ttk.Entry(self.panelPrincipal)
        self.entradaEditorial.grid(column=1, row=3, padx=5, pady=2, sticky=W)
        self.botonLookupEditorial = ttk.Button(self.panelPrincipal, image=self.imagenLookup)
        self.botonLookupEditorial.grid(column=2, row=3, padx=5, pady=2)

        ttk.Label(self.panelPrincipal, text='Año Inicio').grid(column=0, row=4, sticky=W)
        self.entradaAnioInicio = ttk.Entry(self.panelPrincipal, width=8)
        self.entradaAnioInicio.grid(column=1, row=4, padx=5, pady=2, sticky=W)

        ttk.Label(self.panelPrincipal, text='Resumen').grid(column=0, row=6, sticky=W)
        self.botonExpansionResumen = ttk.Button(self.panelPrincipal, image=self.imageExpansion)
        self.botonExpansionResumen.grid(column=1, row=6, sticky=W)

        ttk.Label(self.panelPrincipal, text='Cantidad Números').grid(column=0, row=5, sticky=W)
        self.entradaCantidadNumeros = ttk.Entry(self.panelPrincipal, width=10)
        self.entradaCantidadNumeros.grid(column=1, row=5, padx=5, pady=2, sticky=W)

        self.coverVolumen = Canvas(self.panelPrincipal)
        self.coverVolumen.create_image(180,250, image=self.imageLogo)
        self.coverVolumen.grid(column=3, row=0, rowspan=7, columnspan=2)

        if volume is not None:
            self.setVolume(volume)
            self.loadVolume()
        else:
            self.getFirst()

    def setVolume(self, volume):
        self.volume = volume
        if (self.volume.publisherId != 0):
            self.editorial = self.session.query(Publisher).get(self.volume.publisherId)
        else:
            self.editorial = None

    def loadVolume(self):
        self.clear()

        self.entradaId.insert(0,self.volume.id)
        self.entradaNombre.insert(0,self.volume.nombre)
        self.entradaUrl.insert(0,"falta implementar")
        print(self.volume)
        if (self.volume.hasPublisher()):
            self.entradaEditorial.insert(0,self.editorial.name)
        self.entradaAnioInicio.insert(0,self.volume.AnioInicio)
        self.entradaCantidadNumeros.insert(0,self.volume.cantidadNumeros)

        self.coverVolumen.delete(ALL)
        im = self.volume.getImageCover()
        self.fImage = ImageTk.PhotoImage(im.resize(self.size, Image.BICUBIC))
        self.coverVolumen.create_image((0, 0), image=self.fImage, anchor=NW)  # recordar que esto decide desde donde se muestra la imagen

    def getFirst(self):
        super().getNext()
        volume = self.session.query(Volume).order_by(Volume.nombre.asc()).first()
        if volume is not None:
            print(volume)
            self.setVolume(volume)
            self.loadVolume()

    def borrar(self):
        super().borrar()
        volume = Volume(publisherId='0')
        print("volumen: "+volume.publisherId)
        self.setVolume(volume)
        self.clear()

    def clear(self):
        self.entradaId.delete(0, END)
        self.entradaNombre.delete(0, END)
        self.entradaUrl.delete(0, END)
        self.entradaEditorial.delete(0, END)
        self.entradaAnioInicio.delete(0, END)
        self.entradaCantidadNumeros.delete(0, END)

    def getNext(self):
        super().getNext()
        if self.volume is not None:
            volume = self.session.query(Volume).filter(Volume.nombre > self.volume.nombre).order_by(
                Volume.nombre.asc()).first()
            if volume is not None:

                self.setVolume(volume)
                self.loadVolume()
        else:
            self.getLast()

    def copyFromWindowsToEntity(self):
        self.volume.id = self.entradaId.get()
        self.volume.nombre = self.entradaNombre.get()
        # self.volume.deck = self..get()
        # self.volume.descripcion = self.entradaId.get()
        # self.volume.image_url = self.entradaUrl.get()
        if self.editorial is not None:
            self.volume.publisherId = self.editorial.id_publisher
        self.volume.AnioInicio = self.entradaAnioInicio.get()
        self.volume.cantidadNumeros = self.entradaCantidadNumeros.get()

    def guardar(self):
        super().guardar()
        self.copyFromWindowsToEntity()
        self.session.add(self.volume)
        self.session.commit()

    def getPrev(self):
        super().getPrev()
        if self.volume is not None:
            volume = self.session.query(Volume).filter(Volume.nombre < self.volume.nombre).order_by(
                Volume.nombre.desc()).first()
            if volume is not None:
                self.setVolume(volume)
                self.loadVolume()
        else:
            self.getLast()
    def getLast(self):
        super().getNext()
        volume = self.session.query(Volume).order_by(Volume.nombre.desc()).first()
        if volume is not None:
            print(volume)
            self.setVolume(volume)
            self.loadVolume()

if __name__ == '__main__':
    root = Tk()
    # root.title = "Volume"
    volumen = VolumeGui(root, width=507, height=358)
    volumen.pack()
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.mainloop()

