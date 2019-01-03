
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

import Entidades.Init
from Entidades.Entitiy_managers import Volumens

from Entidades.Agrupado_Entidades import Volume , Publisher
import Entidades.Init
from Gui_gtk.Volumen_lookup_gtk import Volume_lookup_gtk

from Gui_gtk.Volumen_vine_search_gtk import Volumen_vine_search_Gtk
from Extras.ComicVineSearcher import ComicVineSearcher

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
                         'getLast': self.getLast, 'boton_cargar_desde_web_click': self.boton_cargar_desde_web_click,
                         'click_lookup_volume': self.click_lookup_volume,'change_id_volume': self.change_id_volume,
                         'click_limpiar': self.click_limpiar, 'combobox_change': self.combobox_change,
                         'selecion_pagina': self.selecion_pagina}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Volumen.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Volume_gtk")
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
        self.resumen_volumen = self.builder.get_object("resumen_volumen")
        self.liststore_comics_in_volume = self.builder.get_object("liststore_comics_in_volume")


        self.volumens_manager = Volumens(session=self.session)
        self.combobox_orden = self.builder.get_object("combobox_orden")
        self.offset = 0
        self.cantidadRegistros = self.volumens_manager.get_count()
        self.pagina_actual = 0
        # inicializamos el modelo con rotulos del manager
        self.liststore_combobox.clear()
        for clave in self.volumens_manager.lista_opciones.keys():
            self.liststore_combobox.append([clave])
        self.combobox_orden.set_active(0)
        self.getFirst("")

    def selecion_pagina(self, widget, page, page_num):
        self.pagina_actual = page_num
        if page_num == 1:
            comicbooks_in_volumen = self.volumens_manager.get_comicbook_info_by_volume()
            self.liststore_comics_in_volume.clear()
            for comicbook in comicbooks_in_volumen:
                # cantidad = self.volumens_manager.get_comicbook_info_status(comicbook.id_comicbook_info)
                self.liststore_comics_in_volume.append([comicbook.numero, comicbook.titulo, comicbook.cantidad, comicbook.cantidad])


    def combobox_change(self, widget):
        if widget.get_active_iter() is not None:
            self.volumens_manager.set_order(
                self.volumens_manager.lista_opciones[widget.get_model()[widget.get_active_iter()][0]])

    def boton_cargar_desde_web_click(self,widget):
        volumen_vine_search = Volumen_vine_search_Gtk(self.session)
        volumen_vine_search.window.show()

    def updateVolume(self):
         
        cnf = Config(self.session)
        cv = ComicVineSearcher(cnf.getClave('volume'),session=self.session)
        cv.entidad='volume'
        volumenAndComics = cv.getVineEntity(self.volume.id)

        volumeUpdated = volumenAndComics[0]

        self.volume.cantidad_numeros = volumeUpdated.cantidad_numeros
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
        lookup = Volume_lookup_gtk(self.session, self.return_lookup)
        lookup.window.show()

    def change_id_volume(self,widget,event):
        self.editorial = None
        if (self.entry_id.get_text() != ''):
            volume = self.volumens_manager.get(self.entry_id.get_text())
            self.loadVolume(volume)

    def return_lookup(self,id_volume):
        if id_volume!='':
            self.entry_id.set_text(str(id_volume))
            volume = self.volumens_manager.get(self.entry_id.get_text())
            self.loadVolume(volume)

    def loadVolume(self, volumen):
        self.clear()
        if self.volumens_manager.entidad is not None:
            #print("Volumen {}".format(self.volume))
            self.entry_id.set_text(str(volumen.id_volume))
            self.entry_nombre.set_text(volumen.nombre)
            self.entry_url.set_text(volumen.get_url())
            self.entry_url_cover.set_text(volumen.image_url)
            self.entry_id_editorial.set_text(volumen.id_publisher)
            self.label_nombre_editorial.set_text(volumen.publisher_name)
            self.entry_anio_inicio.set_text(str(volumen.anio_inicio))
            self.entry_cantidad_numeros.set_text(str(volumen.cantidad_numeros))
            self.resumen_volumen.set_text(volumen.descripcion)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=volumen.getImagePath(),
                width=250,
                height=250,
                preserve_aspect_ratio=True)

            # print(self.volumen_logo_image)
            self.volumen_logo_image.set_from_pixbuf(pixbuf)
            if self.pagina_actual == 1:
                self.selecion_pagina(None, None, 1)

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
        volume = self.volumens_manager.getNext()
        print('volume')
        print(volume)
        self.loadVolume(volume)

    def copyFromWindowsToEntity(self):
        self.volume.id = self.entradaId.get()
        self.volume.nombre = self.entradaNombre.get()
        # self.volume.deck = self..get()
        # self.volume.descripcion = self.entradaId.get()
        self.volume.image_url = self.entradaUrlImagen.get()
        if self.editorial is not None:
            self.volume.publisherId = self.editorial.id_publisher
        self.volume.anio_inicio = self.entradaAnioInicio.get()
        self.volume.cantidad_numeros = self.entradaCantidadNumeros.get()

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
        volume = self.volumens_manager.getPrev()
        self.loadVolume(volume)

    def getLast(self,widget):
        volume = self.volumens_manager.getLast()
        self.loadVolume(volume)

    def click_limpiar(self, widget):
        self.entry_url.set_text("")
        self.entry_id_editorial.set_text("")
        self.entry_id.set_text("")
        self.entry_cantidad_numeros.set_text("")
        self.entry_nombre.set_text("")
        self.entry_anio_inicio.set_text("")
        self.entry_url_cover.set_text("")
        self.label_nombre_editorial.set_text("")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='../images/coverIssuesThumbnails/sin_caratula.jpg',
            width=250,
            height=250,
            preserve_aspect_ratio=True)
        self.volumen_logo_image.set_from_pixbuf(pixbuf)

if __name__ == '__main__':

    if __name__ == "__main__":
        pub = VolumeGuiGtk()
        pub.window.show_all()
        pub.window.connect("destroy", Gtk.main_quit)
        Gtk.main()

