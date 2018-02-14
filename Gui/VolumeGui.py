from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos
from Entidades.Volumes.Volume import Volume
from Entidades.Publishers.Publisher import Publisher
from PIL import Image, ImageTk
from Gui.FrameMaestro import FrameMaestro
import Entidades.Init
from Gui.VolumeLookupGui import VolumesLookupGui
from Gui.VolumeVineGui import VolumeVineGui
from Extras.ComicVineSearcher import ComicVineSearcher
from Entidades.Volumes.ComicsInVolume import ComicInVolumes
from Extras.Config import Config
class VolumeGui(FrameMaestro):
    def __init__(self, parent, volume=None, session=None, cnf={}, **kw):
        FrameMaestro.__init__(self, parent, cnf, **kw)
        iconos = Iconos.Iconos()
        self.pilImagenLookup = iconos.pilImagenLookup
        self.imagenLookup = PIL.ImageTk.PhotoImage(self.pilImagenLookup)
        self.pilImageExpansion = iconos.pilImageExpansion
        self.imageExpansion = PIL.ImageTk.PhotoImage(self.pilImageExpansion)
        self.pilImageLogo = iconos.pilImageLogo
        self.imageLogo = PIL.ImageTk.PhotoImage(self.pilImageLogo)
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.size = (int(320 * 0.5), int(496 * 0.5))

        self.panelPrincipal = self.getPanelPrincipal()
        ttk.Label(self.panelPrincipal, text='ID').grid(column=0, row=0, sticky=W)
        self.panelId = Frame(self.panelPrincipal)
        self.panelId.grid(column=1, row=0, sticky=(W, E))
        self.entradaId = ttk.Entry(self.panelId)
        self.entradaId.grid(column=1, row=0, padx=5, pady=2, sticky=W)
        self.botonLookupVolume = ttk.Button(self.panelId, image=self.imagenLookup, command=self.openLookupVolume)
        self.botonLookupVolume.grid(column=2, row=0, padx=5, pady=2, sticky=W)

        ttk.Label(self.panelPrincipal, text='Nombre').grid(column=0, row=1, sticky=W)
        self.entradaNombre = ttk.Entry(self.panelPrincipal)
        self.entradaNombre.grid(column=1, row=1, padx=5, pady=2, columnspan=2, sticky=W)

        ttk.Label(self.panelPrincipal, text='Url').grid(column=0, row=2, sticky=W)
        self.entradaUrl = ttk.Entry(self.panelPrincipal, width=50)
        self.entradaUrl .grid(column=1, row=2, padx=5, pady=2, sticky=W)

        ttk.Label(self.panelPrincipal, text='Url Cover').grid(column=0, row=3, sticky=W)
        self.entradaUrlImagen = ttk.Entry(self.panelPrincipal, width=90)
        self.entradaUrlImagen.grid(column=1, row=3, padx=5, pady=2, sticky=W, columnspan=2)

        ttk.Label(self.panelPrincipal, text='Editorial').grid(column=0, row=4, sticky=W)
        self.panelEditorial = Frame(self.panelPrincipal)
        self.panelEditorial.grid(column=1, row=4, sticky=(W, E))

        self.entradaEditorial = ttk.Entry(self.panelEditorial)
        self.entradaEditorial.grid(column=1, row=4, padx=5, pady=2, sticky=W)
        self.botonLookupEditorial = ttk.Button(self.panelEditorial, image=self.imagenLookup)
        self.botonLookupEditorial.grid(column=2, row=4, padx=5, pady=2)

        ttk.Label(self.panelPrincipal, text='Año Inicio').grid(column=0, row=5, sticky=W)
        self.entradaAnioInicio = ttk.Entry(self.panelPrincipal, width=8)
        self.entradaAnioInicio.grid(column=1, row=5, padx=5, pady=2, sticky=W)

        ttk.Label(self.panelPrincipal, text='Resumen').grid(column=0, row=7, sticky=W)
        self.botonExpansionResumen = ttk.Button(self.panelPrincipal, image=self.imageExpansion)
        self.botonExpansionResumen.grid(column=1, row=7, sticky=W)

        ttk.Label(self.panelPrincipal, text='Cantidad Números').grid(column=0, row=6, sticky=W)
        self.entradaCantidadNumeros = ttk.Entry(self.panelPrincipal, width=10)
        self.entradaCantidadNumeros.grid(column=1, row=6, padx=5, pady=2, sticky=W)

        self.coverVolumen = Canvas(self.panelPrincipal)
        self.coverVolumen.create_image(180, 250, image=self.imageLogo)
        self.coverVolumen.grid(column=3, row=0, rowspan=9, columnspan=1)

        self.botonCargarWeb.config(command=self.openVolumeComicVine)
        self.offset = 0
        self.cantidadRegistros = self.session.query(Volume).count()
        self.botonActualizarVolumen = Button(self.frameBotonesAcciones, text='Actualizar desde web',command=self.updateVolume)
        self.botonActualizarVolumen.grid(row=0, column=4, sticky=E)


        if volume is not None:
            self.setVolume(volume)
            self.loadVolume()
        else:
            self.getFirst()

    def updateVolume(self):
        cnf = Config(self.session)
        cv = ComicVineSearcher(cnf.getClave('volume'),session=self.session)
        cv.entidad='volume'
        volumenAndComics = cv.getVineEntity(self.volume.id)

        volumeUpdated = volumenAndComics[0]

        self.volume.cantidadNumeros = volumeUpdated.cantidadNumeros
        self.volume.nombre = volumeUpdated.nombre
        print(volumeUpdated.image_url)
        self.volume.image_url = volumeUpdated.image_url
        self.volume.publisher_name = volumeUpdated.publisher_name
        self.volume.publisherId = volumeUpdated.publisherId
        self.setVolume(self.volume)
        self.loadVolume()
        self.numerosPorVolumen = volumenAndComics[1]
        self.guardar()

    def openLookupVolume(self):
        window = Toplevel()
        volumeRetorno = Volume()
        lk = VolumesLookupGui(window, volumeRetorno)
        lk.grid(sticky=(E, W, S, N))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.geometry("+0+0")
        window.wm_title(string="Series")
        lk.buscarVolume()
        lk.treeview_sort_column(lk.grillaVolumes, 'name', False)
        self.wait_window(window)
        serieRetorno = lk.getSerie()
        self.volume = serieRetorno
        self.loadVolume()

    def openVolumeComicVine(self):
        window = Toplevel()
        window.geometry("+0+0")
        window.wm_title(string="Editorial desde Comic Vine")
        volumenVineGui = VolumeVineGui(window, width=507, height=358)
        volumenVineGui.grid(sticky=(N, S, E, W))

    def setVolume(self, volume):
        self.volume = volume
        if (self.volume.publisherId != 0):
            print('recuperando editorioa')
            self.editorial = self.session.query(Publisher).get(self.volume.publisherId)
            print(self.editorial)
        else:
            self.editorial = None

    def loadVolume(self):
        self.clear()
        if self.volume is not None:
            #print("Volumen {}".format(self.volume))
            self.entradaId.insert(0,self.volume.id)
            self.entradaNombre.insert(0,self.volume.nombre)
            print(self.volume.image_url)
            self.entradaUrlImagen.insert(0, self.volume.image_url)
            if (self.volume.hasPublisher()):
                print("*******VOLUMEN***********{}".format(self.volume.publisherId))
                print("Nombre {}".format(self.editorial.name))
                self.entradaEditorial.insert(0, self.editorial.name)
            self.entradaAnioInicio.insert(0,self.volume.AnioInicio)
            self.entradaCantidadNumeros.insert(0,self.volume.cantidadNumeros)

            im = self.volume.getImageCover()
            self.fImage = ImageTk.PhotoImage(im.resize(self.size, Image.BICUBIC))
            self.coverVolumen.create_image((0, 0), image=self.fImage, anchor=NW)  # recordar que esto decide desde donde se muestra la imagen
        self.newRecord=False
    def getFirst(self):
        super().getNext()
        self.offset=0
        volume = self.session.query(Volume).order_by(Volume.nombre.asc()).offset(self.offset).first()
        if volume is not None:
            print(volume)
            self.setVolume(volume)
            self.loadVolume()

    def borrar(self):
        super().borrar()
        volume = Volume(publisherId='0')
        self.setVolume(volume)
        self.clear()

    def clear(self):
        self.entradaId.delete(0, END)
        self.entradaNombre.delete(0, END)
        self.entradaUrl.delete(0, END)
        self.entradaEditorial.delete(0, END)
        self.entradaAnioInicio.delete(0, END)
        self.entradaCantidadNumeros.delete(0, END)
        self.entradaUrlImagen.delete(0,END)
        self.coverVolumen.delete(ALL)
        self.newRecord=True

    def getNext(self):
        super().getNext()
        if self.offset < self.cantidadRegistros-1:
            self.offset += 1
        if self.volume is not None:
            volume = self.session.query(Volume).order_by(Volume.nombre.asc()).offset(self.offset).first()
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
        self.volume.image_url = self.entradaUrlImagen.get()
        if self.editorial is not None:
            self.volume.publisherId = self.editorial.id_publisher
        self.volume.AnioInicio = self.entradaAnioInicio.get()
        self.volume.cantidadNumeros = self.entradaCantidadNumeros.get()

    def keyOrd(self,t):
        return(int(t.comicOrder))

    def guardar(self):
        super().guardar()
        self.copyFromWindowsToEntity()
        if self.newRecord:
            self.session.add(self.volume)
        self.session.query(ComicInVolumes).filter(ComicInVolumes.volumeId==self.volume.id).delete()
        #self.numerosPorVolumen.sort(reverse=False, key=self.keyOrd)
        for index, numeroComic in enumerate(self.numerosPorVolumen, start=0):
            self.session.add(numeroComic)
        self.session.commit()

    def getPrev(self):
        super().getPrev()
        if self.offset >0:
            self.offset -= 1
        if self.volume is not None:
            volume = self.session.query(Volume).order_by(Volume.nombre.asc()).offset(self.offset).first()
            if volume is not None:
                self.setVolume(volume)
                self.loadVolume()
        else:
            self.getLast()
    def getLast(self):
        super().getNext()
        self.offset = self.cantidadRegistros -1
        volume = self.session.query(Volume).order_by(Volume.nombre.asc()).offset(self.offset).first()
        if volume is not None:
            print(volume)
            self.setVolume(volume)
            self.loadVolume()

if __name__ == '__main__':
    root = Tk()
    # root.title = "Volume"
    volumen = VolumeGui(root, width=307, height=358)
    volumen.pack()
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.mainloop()

