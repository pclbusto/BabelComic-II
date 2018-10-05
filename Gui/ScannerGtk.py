from Extras.Config import Config
from Extras.Scanner import BabelComicBookScanner
import Entidades.Init
from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Setups.Setup import Setup
import threading
import shutil,os


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject,GLib
# from gi.repository import Gdk

class ScannerGtk():

    def __init__(self,  session=None,):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'borrarComics': self.borrarComics,'scannearDirectorio':self.scannearDirectorio}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Scanner.glade")
        self.window = self.builder.get_object("ScannerGtk")
        self.builder.connect_signals(self.handlers)
        self.window.set_destroy_with_parent(True)
        self.progerss_bar = self.builder.get_object('progress_bar')

    def scannearDirectorio(self,widget):
        self.config = Config()
        self.manager = BabelComicBookScanner(self.config.listaDirectorios, self.config.listaTipos)

        self.manager.iniciarScaneo()
        t = threading.Thread(target=self.testScanning)
        t.start()

    def actualizar_scroll(self):
        self.progerss_bar.set_fraction(self.manager.porcentajeCompletado / 100.0)

    def testScanning(self):
        while (self.manager.scanerDir.isAlive()):
            print("PROCENTAJE COMPLETADO {}".format(self.manager.porcentajeCompletado/100.0))
            GLib.idle_add(self.actualizar_scroll)
        print("Finalizado")

    def borrarComics(self, widget):
        session = Entidades.Init.Session()
        session.query(ComicBook).delete()
        session.commit()
        setup = session.query(Setup).get(1)
        for nombre_archivo in os.listdir(os.path.join(os.path.join(setup.directorioBase,'images'),'coverIssuesThumbnails')):
            if nombre_archivo != 'sin_caratula.jpg':
                os.remove(os.path.join(os.path.join(os.path.join(setup.directorioBase,'images'),
                                                    'coverIssuesThumbnails'),nombre_archivo))

    def salir(self,arg1,arg2):
        return True

    def _copy_to_window(self,publisher):
        # self.clearWindow()
        if publisher is not None:
            print("cargan valores")
            self.entry_id.set_text(publisher.id_publisher)
            self.entry_nombre.set_text( publisher.name)
            self.entry_url.set_text(publisher.siteDetailUrl)
            # if publisher.localLogoImagePath

            if publisher.localLogoImagePath:
                if publisher.localLogoImagePath[-3].lower()=='gif':
                    gif = GdkPixbuf.PixbufAnimation.new_from_file(publisher.localLogoImagePath).get_static_image()
                    self.publisher_logo_image.set_from_pixbuf(gif.scale_simple(250, 250, 3))
                else:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        filename=self.path_publisher_logo+publisher.localLogoImagePath,
                        width=250,
                        height=250,
                        preserve_aspect_ratio=True)
                    self.publisher_logo_image.set_from_pixbuf(pixbuf)

            self.label_resumen.set_text(publisher.deck)

    def clearWindow(self):
        # self.entradaId.delete(0, END)
        # self.entradaNombre.delete(0, END)
        # self.entradaUrl.delete(0, END)
        # self.textoDescripcion.config(text='')
        pass


if __name__ == "__main__":
    pub = ScannerGtk()
    pub.window.connect("destroy", Gtk.main_quit)

    pub.window.show_all()
    Gtk.main()