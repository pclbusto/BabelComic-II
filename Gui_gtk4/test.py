import sys
import gi
from gi.overrides.Gtk import GTK4

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.builder = None

    def on_activate(self, app):
        # Create a Buildercam
        self.builder = Gtk.Builder()
        # help(self.builder)
        self.builder.add_from_file("test.ui")

        # Obtain the button widget and connect it to a function
        self.win = self.builder.get_object("main_window")
        self.navigation_view = self.builder.get_object("navigation_view")
        self.win.set_application(self)  # Application will close once it no longer has active windows attached to it
        self.navigation_page = self.builder.get_object("navigation_page02")
        self.navigation_view.add(self.navigation_page)
        self.btn = self.builder.get_object("btn_next_page")
        self.btn.connect("clicked", self.next_page)
        self.win.present()
        # self.win.maximize()

    def next_page(self, button):
        # pagina =
        self.navigation_view.push(self.navigation_page)
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