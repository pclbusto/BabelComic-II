from Extras.Config import Config
from Extras.Scanner import BabelComicBookScanner
import Entidades.Init
from Entidades.Agrupado_Entidades import Comicbook, Setup
import threading
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject,GLib

class ScannerGtk():

    def __init__(self,  session=None, funcion_callback=None):
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.handlers = {'borrarComics': self.borrarComics,'scannearDirectorio':self.scannearDirectorio}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Scanner.glade")
        self.window = self.builder.get_object("ScannerGtk")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
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

        if hasattr(self,'funcion_callback'):
            self.funcion_callback()

        # self.window.close()

    def borrarComics(self, widget):
        session = Entidades.Init.Session()
        session.query(Comicbook).delete()
        session.commit()
        setup = session.query(Setup).get(1)
        for nombre_archivo in os.listdir(os.path.join(os.path.join(setup.directorioBase,'images'),'coverIssuesThumbnails')):
            if nombre_archivo != 'sin_caratula.jpg':
                os.remove(os.path.join(os.path.join(os.path.join(setup.directorioBase,'images'),
                                                    'coverIssuesThumbnails'),nombre_archivo))

        if hasattr(self,'funcion_callback'):
            self.funcion_callback()


if __name__ == "__main__":
    pub = ScannerGtk()
    pub.window.connect("destroy", Gtk.main_quit)

    pub.window.show_all()
    Gtk.main()