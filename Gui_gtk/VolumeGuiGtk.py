import Entidades.Init
from Entidades.Publishers import Publishers
from Entidades.Setups. Setup import  Setup
from Entidades.Volumens.Volumens import Volumens
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


from Entidades.Volumens.Volume import Volume
from Entidades.Publishers.Publisher import Publisher
import Entidades.Init
from Gui_gtk.Volumen_lookup_gtk import Volume_lookup_gtk

from Gui_gtk.Volumen_vine_search_gtk import Volumen_vine_search_Gtk
from Extras.ComicVineSearcher import ComicVineSearcher
from Entidades.Volumens.ComicsInVolume import ComicInVolumes
from Extras.Config import Config

class VolumeGuiGtk():
    # todo implementar los botones de limpiar, guardar y borrar
    # todo clase que administre el comportamiento completo de alta, baja mdoficacion navegacion y borrado
    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'getFirst': self.getFirst, 'getPrev': self.getPrev, 'getNext': self.getNext,
                         'getLast': self.getLast, 'boton_cargar_desde_web_click':self.boton_cargar_desde_web_click,
                         'click_lookup_volume':self.click_lookup_volume,'change_id_volumen':self.change_id_volumen}

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
        self.liststore_combobox = self.builder.get_object("liststore_combobox")
        self.volumens_manager = Volumens(session=self.session)
        self.combobox_orden = self.builder.get_object("combobox_orden")
        self.offset = 0
        self.cantidadRegistros = self.volumens_manager.get_count()

        # inicializamos el modelo con rotulos del manager
        self.liststore_combobox.clear()
        for clave in self.volumens_manager.lista_opciones.keys():
            self.liststore_combobox.append([clave])
        self.combobox_orden.set_active(0)
        self.getFirst("")


    def boton_cargar_desde_web_click(self,widget):
        volumen_vine_search = Volumen_vine_search_Gtk(self.session)
        volumen_vine_search.window.show()

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

    def click_lookup_volume(self,widget):
        print('dasds')
        lookup = Volume_lookup_gtk(self.session, self.entry_id)
        lookup.window.show()

    def change_id_volumen(self,widget):
        self.editorial = None
        if (self.entry_id.get_text() != ''):
            self.volume = self.session.query(Volume).get(self.entry_id.get_text())
        self.loadVolume()

    def loadVolume(self, volumen):
        self.clear()
        if self.volumens_manager.entidad is not None:
            #print("Volumen {}".format(self.volume))
            self.entry_id.set_text(str(volumen.id_volumen))
            self.entry_nombre.set_text(volumen.nombre)
            self.entry_url.set_text(volumen.get_url())
            self.entry_url_cover.set_text(volumen.image_url)
            self.entry_id_editorial.set_text(volumen.publisherId)
            self.label_nombre_editorial.set_text(volumen.publisher_name)
            self.entry_anio_inicio.set_text(str(volumen.AnioInicio))
            self.entry_cantidad_numeros.set_text(str(volumen.cantidadNumeros))
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=volumen.getImagePath(),
                width=250,
                height=250,
                preserve_aspect_ratio=True)

            # print(self.volumen_logo_image)
            self.volumen_logo_image.set_from_pixbuf(pixbuf)

    def getFirst(self,widget):
        volume = self.volumens_manager.getFirst()
        print(volume)
        if volume is not None:
            self.loadVolume(volume)

    def borrar(self):
        super().borrar()
        volume = Volume(publisherId='0')
        self.setVolume(volume)
        self.clear()

    def clear(self):
        self.entry_nombre.set_text('')
        self.entry_url.set_text('')
        self.entry_url_cover.set_text('')
        self.entry_id_editorial.set_text('')
        self.label_nombre_editorial.set_text('')
        self.entry_anio_inicio.set_text('')
        self.entry_cantidad_numeros.set_text('')

    def getNext(self,widget):
        if self.offset < self.cantidadRegistros-1:
            self.offset += 1
        if self.volume is not None:
            volume = self.session.query(Volume).order_by(Volume.nombre.asc()).offset(self.offset).first()
            if volume is not None:
                self.volume = volume
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
                self.volume = volume
                self.loadVolume()
        else:
            self.getLast()
    def getLast(self,widget):
        self.offset = self.cantidadRegistros -1
        volume = self.session.query(Volume).order_by(Volume.nombre.asc()).offset(self.offset).first()
        if volume is not None:
            print(volume)
            self.volume = volume
            self.loadVolume()

if __name__ == '__main__':

    if __name__ == "__main__":
        pub = VolumeGuiGtk()
        pub.window.show_all()
        pub.window.connect("destroy", Gtk.main_quit)
        Gtk.main()

