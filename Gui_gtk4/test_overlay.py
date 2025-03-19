import sys
import gi
from gi.overrides.Gtk import GTK4

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Gtk, Adw

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.builder = None

    def on_activate(self, app):
        # Create a Builder
        self.builder = Gtk.Builder()
        # help(self.builder)
        self.builder.add_from_file("test.ui")

        # Obtain the button widget and connect it to a function
        self.win = self.builder.get_object("side_window")
        self.boton_sidebar = self.builder.get_object("boton_sidebar")
        self.boton_sidebar.connect("clicked", self.boton_sidebar_clicked)
        self.win.set_application(self)  # Application will close once it no longer has active windows attached to it
        self.scroll = self.builder.get_object("")
        self.gridview = self.builder.get_object("gridview")
        self.modelo = self.gridview.get_model()

        self.cover = Pixbuf.new_from_file("/home/pedro/PycharmProjects/BabelComic-II/images/issues_covers/773-Superman/4504-773-4918-1-superman.jpg")
        self.cover.scale_simple(50, 10, 3)
        print(type(self.modelo.get_model().get_item_type()))
        self.modelo.get_model().append(self.cover)
        # self.navigation_page = self.builder.get_object("navigation_page02")
        # self.navigation_view.add(self.navigation_page)
        # self.btn = self.builder.get_object("btn_next_page")
        # self.btn.connect("clicked", self.next_page)
        self.win.present()
        # self.win.maximize()

    def boton_sidebar_clicked(self, button):
        navigation_split_view = self.builder.get_object("navigation_split_view")
        navigation_split_view.set_collapsed(not navigation_split_view.get_collapsed())
        if navigation_split_view.get_collapsed():
            contenido = self.builder.get_object("contenido")
            navigation_split_view.set_show_content(True)

    def siguiente(self, button):
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.revealer.set_reveal_child(False)
        btn = self.builder.get_object("grid02")
        self.revealer.set_child(btn)
        self.revealer.set_reveal_child(True)


def click_boton_acerca_de(self, button):
    self.acerca_de_window = self.builder.get_object("acerca_de")
    self.acerca_de_window.present()
    popover = self.builder.get_object("menu_principal_popover")
    popover.destroy()

    def click_boton_salir(self, button):
        self.win.destroy()




app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)