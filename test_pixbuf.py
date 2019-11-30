import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
from PIL import Image, ImageFile

class test_pixbuf():
    def __init__(self):


        self.handlers = {}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("test_pixbuf.glade")
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("test_pixbuf")
        self.liststore1 = self.builder.get_object("liststore1")

        # self.liststore = Gtk.ListStore(Pixbuf, str)
        cataloged_pix = Pixbuf.new_from_file('iconos/Cataloged.png')
        imagen = Pixbuf.new_from_file_at_size ('6373148-blank.png',200,200)
        cataloged_pix.composite(imagen,0,0,100,100,0,0,1,1,3,255)
        self.liststore1.append([imagen,""])


if (__name__ == '__main__'):
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    imagen = Image.open("/home/pclbusto/Imágenes/test/action047-med.gif")
    imagen.show()
    #open("/home/pclbusto/Imágenes/test/action047-med.gif")
