from PIL import  Image
from zipfile import ZipFile
import io

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject,GLib

class Test_Thumnails():

    def __init__(self,  session=None, funcion_callback=None):

        # self.handlers = {'borrarComics': self.borrarComics,'scannearDirectorio':self.scannearDirectorio}
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../Glade_files/Comicbook_reader.glade")
        self.window = self.builder.get_object("Reader")
        self.load_zip_file()

    def load_zip_file(self):
        file_name = "small.cbz"
        with ZipFile(file_name, 'r') as zip:
            # printing all the contents of the zip file
            print(zip.namelist())
            data = zip.read('small/Batman 076-000.jpg')
            Image.open(io.BytesIO(data)).show()

            # extracting all the files
            print('Extracting all the files now...')
            print('Done!')


if __name__ == "__main__":
    pub = Test_Thumnails()
    pub.window.connect("destroy", Gtk.main_quit)

    pub.window.show_all()
    Gtk.main()