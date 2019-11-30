import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk





class Acerca_de_gtk():
    # todo arreglar boton de acpetar o grilla de directorios de comics

    def __init__(self, session=None):

        # self.handlers = {"click_guardar":self.click_guardar,
        #                  'click_boton_borrar_directorio_comic':self.click_boton_borrar_directorio_comic,
        #                  'click_boton_agregar_directorio_comic':self.click_boton_agregar_directorio_comic,
        #                  'click_boton_directorio_base':self.click_boton_directorio_base}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Acercade.glade")
        #self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Acerca_de")
        self.window.set_icon_from_file('../iconos/BabelComic.png')

    def click_boton_agregar_directorio_comic(self, widget):
        dialogo = Gtk.FileChooserDialog(title='Selección de Directorios de Comics', parent= self.window,  action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialogo.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        response = dialogo.run()
        if response == Gtk.ResponseType.OK:
            # print("Open clicked")
            # print("File selected: " + salida.get_filename())
            self.liststore_directorios_comics.append([dialogo.get_filename()])
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialogo.destroy()




if (__name__ == '__main__'):
    test = Acerca_de_gtk()
    test.window.connect("destroy", Gtk.main_quit)
    test.window.show()
    Gtk.main()

