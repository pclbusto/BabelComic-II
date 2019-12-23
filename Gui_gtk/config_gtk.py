import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import Extras.Config
import Entidades.Init



class Config_gtk():
    # todo arreglar boton de acpetar o grilla de directorios de comics

    def __init__(self, session=None):

        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

        self.babelComicConfig = Extras.Config.Config(self.session)

        self.handlers = {"click_guardar":self.click_guardar,
                         'click_boton_borrar_directorio_comic':self.click_boton_borrar_directorio_comic,
                         'click_boton_agregar_directorio_comic':self.click_boton_agregar_directorio_comic,
                         'click_boton_directorio_base':self.click_boton_directorio_base}

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Config_gtk.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("Config_gtk")
        self.window.set_icon_from_file('../iconos/BabelComic.png')
        self.liststore_directorios_comics = self.builder.get_object("liststore_directorios_comics")
        self.liststore_directorios_comics.clear()
        self.entry_clave_servico_comicvine = self.builder.get_object("entry_clave_servico_comicvine")
        self.entry_lista_extensiones_soportadas = self.builder.get_object("entry_lista_extensiones_soportadas")
        self.entry_directorio_base = self.builder.get_object("entry_directorio_base")
        self.entry_spinner_cantidad_por_pagina = self.builder.get_object("entry_spinner_cantidad_por_pagina")
        self.label_status = self.builder.get_object("label_status")
        self.treeview_directorios_comics = self.builder.get_object("treeview_directorios_comics")

        self._copy_to_window()


    def _copy_to_window(self):
        # self.clearWindow()
        if self.babelComicConfig is not None:
            for directorio in self.babelComicConfig.listaDirectorios:
                self.liststore_directorios_comics.append([directorio])
            if len(self.babelComicConfig.listaClaves)>0:
                self.entry_clave_servico_comicvine.set_text(self.babelComicConfig.listaClaves[0])

            lista_extenesiones = ''
            for extension in self.babelComicConfig.listaTipos:
                lista_extenesiones += extension+","

            if len(lista_extenesiones)>0 and lista_extenesiones[-1] ==',':
                lista_extenesiones=  lista_extenesiones[:-1]
                self.entry_lista_extensiones_soportadas.set_text(lista_extenesiones)

            self.entry_directorio_base.set_text(self.babelComicConfig.setup.directorioBase)
            self.entry_spinner_cantidad_por_pagina.set_value(self.babelComicConfig.setup.cantidadComicsPorPagina)

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

    def click_boton_directorio_base(self,widget):
        dialogo = Gtk.FileChooserDialog(title='Selección de Directorios Base de BabelComic', parent=self.window,
                                        action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialogo.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        response = dialogo.run()
        if response == Gtk.ResponseType.OK:
            # print("Open clicked")
            # print("File selected: " + salida.get_filename())
            self.entry_directorio_base.set_text(dialogo.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialogo.destroy()

    def click_boton_borrar_directorio_comic(self, widget):
        (model, iter) = self.treeview_directorios_comics.get_selection().get_selected()
        if iter:
            model.remove(iter)

    def click_guardar(self, widget):
        directorios = [item[0] for item in self.liststore_directorios_comics]
        clave = self.entry_clave_servico_comicvine.get_text()
        self.babelComicConfig.setListaDirectorios(directorios)
        self.babelComicConfig.setListaTipos(self.entry_lista_extensiones_soportadas.get_text().split(','))
        self.babelComicConfig.setListaClaves([clave])
        print(int(self.entry_spinner_cantidad_por_pagina.get_value()))
        self.babelComicConfig.setConfig(self.entry_directorio_base.get_text(), int(self.entry_spinner_cantidad_por_pagina.get_value()))
        self.label_status.set_text('Status: Gurdado exitosamente')



if (__name__ == '__main__'):
    config = Config_gtk()
    config.window.connect("destroy", Gtk.main_quit)
    config.window.show()
    config.entry_clave_servico_comicvine.set_text('7e4368b71c5a66d710a62e996a660024f6a868d4')
    # config.window.maximize()
    Gtk.main()

