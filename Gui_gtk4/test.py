import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.builder = None

    def on_activate(self, app):
        # Create a Builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("babel.ui")

        # Obtain the button widget and connect it to a function
        button = self.builder.get_object("btn_acerca_de")
        button.connect("clicked", self.click_boton_acerca_de)
        # Obtain and show the main window
        self.win = self.builder.get_object("main_window")
        self.win.set_application(self)  # Application will close once it no longer has active windows attached to it
        self.win.present()
        self.win.maximize()

    def click_boton_acerca_de(self, button):
        self.acerca_de_window = self.builder.get_object("acerca_de")
        self.acerca_de_window.present()
        popover = self.builder.get_object("menu_principal_popover")
        popover.destroy()





app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)