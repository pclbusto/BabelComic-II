import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from Gui_gtk.Volumen_vine_search_gtk import Volumen_vine_search_Gtk




class Function_launcher_gtk():
    # todo arreglar boton de acpetar o grilla de directorios de comics

    def __init__(self, babel_comic_window):

        self.handlers = {
                         "enter_configuracion": self.enter_configuracion,
                         "enter_acerca_de": self.enter_acerca_de,
                         "enter_comic_info": self.enter_comic_info,
                         "enter_serie": self.enter_serie,
                         "enter_editorial": self.enter_editorial,
                         "enter_refrescar": self.enter_refrescar,
                         "enter_catalogar": self.enter_catalogar,
                         "enter_escanear_dir": self.enter_escanear_dir,
                         "enter_serie_vine_search": self.enter_serie_vine_search,
                         "evento": self.evento,
                         "search_changed": self.search_changed}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Funtion_launcher.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Function_launcher")
        self.function_list = self.builder.get_object("function_list")
        self.function_searcher = self.builder.get_object("function_searcher")
        self.babel_comic_window = babel_comic_window
        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.lista_botones = self.function_list.get_children()
        self.lista_botones_visibles = self.function_list.get_children()
        self.function_searcher.grab_focus()

        for item in self.lista_botones:
            print(item.get_label())

    def enter_serie_vine_search(self, widget):
        volumen_vine_search = Volumen_vine_search_Gtk()
        volumen_vine_search.window.show()
        self.window.close()

    def enter_configuracion(self, widget):
        self.babel_comic_window.click_boton_config(None)
        self.window.close()
    def enter_serie(self, widget):
        self.babel_comic_window.click_boton_serie(None)
        self.window.close()
    def enter_acerca_de(self, widget):
        self.babel_comic_window.click_boton_acerca_de(None)
        self.window.close()
    def enter_comic_info(self, widget):
        self.babel_comic_window.click_boton_comic_info(None)
        self.window.close()
    def enter_editorial(self, widget):
        self.babel_comic_window.click_editorial(None)
        self.window.close()
    def enter_refrescar(self, widget):
        self.babel_comic_window.click_boton_refresh(None)
        self.window.close()
    def enter_catalogar(self, widget):
        self.babel_comic_window.click_catalogar(None)
        self.window.close()
    def enter_escanear_dir(self, widget):
        self.babel_comic_window.click_boton_open_scanear(None)
        self.window.close()

    def evento(self, widget, args):
        print(args.keyval)
        if args.keyval == Gdk.KEY_Escape:
            self.window.close()
        if args.keyval == Gdk.KEY_Return:
            if len(self.lista_botones_visibles) > 0:
                self.lista_botones_visibles[0].clicked()
                self.window.close()

    def search_changed(self, widget):
        x = 0
        y = 0
        for item in self.lista_botones_visibles:
            self.function_list.remove(item)
        self.lista_botones_visibles.clear()
        for item in self.lista_botones:
            if self.function_searcher.get_text().lower() in item.get_label().lower():
                self.lista_botones_visibles.append(item)
        for item in self.lista_botones_visibles:
            self.function_list.attach(item, x, y, 1, 1)
            x += 1
            if x == 3:
                y += 1
                y %= 3
            x %= 3

