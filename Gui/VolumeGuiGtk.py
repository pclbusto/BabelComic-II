import os
import Entidades.Init
from Entidades.Publishers import Publishers
from Entidades.Setups. Setup import  Setup

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


from Entidades.Volumes.Volume import Volume
from Entidades.Publishers.Publisher import Publisher
import Entidades.Init
from Gui.VolumeLookupGui import VolumesLookupGui
from Gui.VolumeVineGui import VolumeVineGui
from Extras.ComicVineSearcher import ComicVineSearcher
from Entidades.Volumes.ComicsInVolume import ComicInVolumes
from Extras.Config import Config

class VolumeGuiGtk():

    def __init__(self, volume=None, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext,'getLast': self.getLast}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Volumen.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("VolumeGtk")
        self.entry_id = self.builder.get_object("entry_id")
        self.entry_nombre = self.builder.get_object("entry_nombre")
        self.entry_url = self.builder.get_object("entry_url")
        self.entry_url_cover = self.builder.get_object("entry_url_cover")
        self.entry_id_editorial = self.builder.get_object("entry_id_editorial")
        self.label_nombre_editorial = self.builder.get_object("label_nombre_editorial")
        self.entry_anio_inicio = self.builder.get_object("entry_anio_inicio")
        self.entry_cantidad_numeros = self.builder.get_object("entry_cantidad_numeros")
        self.volumen_logo_image = self.builder.get_object("volumen_logo_image")
        self.window.connect("destroy", Gtk.main_quit)

        self.offset = 0
        self.cantidadRegistros = self.session.query(Volume).count()

        if volume is not None:
            self.setVolume(volume)
            self.loadVolume()
        else:
            self.getFirst("")

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
        # self.clear()
        if self.volume is not None:
            #print("Volumen {}".format(self.volume))
            self.entry_id.set_text(self.volume.id)
            self.entry_nombre.set_text(self.volume.nombre)
            self.entry_url.set_text("http://comicvine/"+self.volume.id)
            self.entry_url_cover.set_text(self.volume.image_url)
            self.entry_id_editorial.set_text(self.volume.publisherId)
            self.label_nombre_editorial.set_text(self.volume.publisher_name)
            self.entry_anio_inicio.set_text(str(self.volume.AnioInicio))
            self.entry_cantidad_numeros.set_text(str(self.volume.cantidadNumeros))
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=self.volume.getImagePath(),
                width=250,
                height=250,
                preserve_aspect_ratio=True)
            print("dasdas")
            print(self.volumen_logo_image)
            self.volumen_logo_image.set_from_pixbuf(pixbuf)


            # print(self.volume.image_url)
            # self.entradaUrlImagen.insert(0, self.volume.image_url)
            # if (self.volume.hasPublisher()):
            #     print("*******VOLUMEN***********{}".format(self.volume.publisherId))
            #     print("Nombre {}".format(self.editorial.name))
            #     self.entradaEditorial.insert(0, self.editorial.name)
            # self.entradaAnioInicio.insert(0,self.volume.AnioInicio)
            # self.entradaCantidadNumeros.insert(0,self.volume.cantidadNumeros)
            #
            # im = self.volume.getImageCover()
            # self.fImage = ImageTk.PhotoImage(im.resize(self.size, Image.BICUBIC))
            # self.coverVolumen.create_image((0, 0), image=self.fImage, anchor=NW)  # recordar que esto decide desde donde se muestra la imagen
        # self.newRecord=False

    def getFirst(self,widget):
        print("get first")
        # super().getNext()
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

    def getNext(self,widget):
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

    def getPrev(self,widget):
        if self.offset >0:
            self.offset -= 1
        if self.volume is not None:
            volume = self.session.query(Volume).order_by(Volume.nombre.asc()).offset(self.offset).first()
            if volume is not None:
                self.setVolume(volume)
                self.loadVolume()
        else:
            self.getLast()
    def getLast(self,widget):
        self.offset = self.cantidadRegistros -1
        volume = self.session.query(Volume).order_by(Volume.nombre.asc()).offset(self.offset).first()
        if volume is not None:
            print(volume)
            self.setVolume(volume)
            self.loadVolume()

if __name__ == '__main__':

    if __name__ == "__main__":
        pub = VolumeGuiGtk()
        pub.window.show_all()
        Gtk.main()

