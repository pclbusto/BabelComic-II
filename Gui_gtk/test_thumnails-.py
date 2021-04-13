from PIL import  Image, ImageDraw
from zipfile import ZipFile
import io
import threading

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

class Test_Thumnails():

    def __init__(self,  session=None, funcion_callback=None):

        # self.handlers = {'borrarComics': self.borrarComics,'scannearDirectorio':self.scannearDirectorio}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Comicbook_reader.glade")
        self.window = self.builder.get_object("Reader")
        self.iconview = self.builder.get_object("iconview")
        self.liststore1 = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.iconview.set_model(self.liststore1)
        self.size = 120
        self.window.maximize()
        self.iconview.set_model(self.liststore1)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.set_column_spacing(-1)
        self.iconview.set_item_padding(10)
        self.iconview.set_item_width(1)
        self.iconview.set_spacing(30)
        self.load_zip_file()


    def image2pixbuf(self, im):
        """Convert Pillow image to GdkPixbuf"""
        data = im.tobytes()
        w, h = im.size
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                              False, 8, w, h, w * 3)
        return pix

    def create_thumnail(self, zip, archivo_nombre, index):
        data = zip.read(archivo_nombre)
        image = Image.open(io.BytesIO(data)).convert("RGB")
        size = (self.size, int(image.size[1] * self.size / image.size[0]))
        image.thumbnail(size, 3, 3)
        img_aux = image.copy()
        d1 = ImageDraw.Draw(img_aux)
        d1.polygon([(0, 0), (size[0]-1, 0), (size[0]-1, size[1]-1), (0, size[1]-1)], outline=(0, 0, 0))

        gdkpixbuff_thumnail = self.image2pixbuf(img_aux)

        GLib.idle_add(self.update_progess, gdkpixbuff_thumnail, index)


    def update_progess(self, gdkpixbuff_thumnail, index):

        self.liststore1[index][0] = gdkpixbuff_thumnail

    def update_progess2(self, gdkpixbuff_thumnail, archivo_nombre):
        self.liststore1.append([gdkpixbuff_thumnail, archivo_nombre])

    def create_grey_tumnails(self, cantidad):
        img = Image.new("RGB", (self.size, self.size*2), (150, 150, 150))
        for i in range(0, cantidad):
            img_aux = img.copy()
            d1 = ImageDraw.Draw(img_aux)
            d1.text(((self.size/2)-20, self.size/2), str(i),  fill=(255, 255, 255))
            d1.polygon([(0, 0), (self.size, 0), (self.size, self.size*2), (0, self.size*2)], outline=(0, 0, 0))
            gdkpixbuff_thumnail = self.image2pixbuf(img_aux)
            GLib.idle_add(self.update_progess2, gdkpixbuff_thumnail, str(i))

    def create_thumnails(self, zip_name):
        with ZipFile(zip_name, 'r') as zip:
            lista_archivos = zip.namelist()
            lista_nombre_archivos = [nombre_archivo for nombre_archivo in lista_archivos if
                                     nombre_archivo[-3:] in ['jpg', 'png']]
            for index, archivo_nombre in enumerate(lista_nombre_archivos):
                print(archivo_nombre)
                t = threading.Thread(name=archivo_nombre, args=(zip, archivo_nombre, index,), target=self.create_thumnail)
                t.start()

    def load_zip_file(self):
        file_name = "/run/media/pedro/Green/Comics/DC/Action Comics V1938 #883 (2010).cbz"
        with ZipFile(file_name, 'r') as zip:
            lista_archivos = zip.namelist()
            lista_nombre_archivos = [nombre_archivo for nombre_archivo in lista_archivos if nombre_archivo[-3:] in ['jpg', 'png']]
            self.create_grey_tumnails(len(lista_nombre_archivos))
            t = threading.Thread(name='my_service', args=(file_name,), target=self.create_thumnails)
            t.start()

            # extracting all the files
            print('Extracting all the files now...')
            print('Done!')


if __name__ == "__main__":
    pub = Test_Thumnails()
    pub.window.connect("destroy", Gtk.main_quit)

    pub.window.show_all()
    Gtk.main()