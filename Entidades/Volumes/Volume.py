
from PIL import Image, ImageTk
from tkinter import Tk, ttk
import os
import urllib.request
import Extras.Config
from sqlalchemy import Column, Integer, String
import Entidades.Init



class Volume():
    __tablename__='Volumes'
    id = Column(String, primary_key=True)  # idExterno-por cuestiones de como lo tabaja comicVine vamos a hacerlo clave.
    nombre = Column(String)
    deck = Column(String)
    descripcion = Column(String)
    image_url = Column(String)  # la mas grande. Las chicas las hacemos locales.
    publisherId = Column(String)
    AnioInicio = Column(Integer)
    cantidadNumeros = Column(Integer)

    def hasLocalCover(self):
        if self.image_url:
            file_name = self.image_url.split('/')[-1]
            file_name_no_ext = (file_name[:-4])
            if os.path.exists(Extras.Config().getVolumeCoverPath() + file_name_no_ext + ".jpg"):
                return True
        return False

    def getVolumeCoverPath(self):
        file_name = self.image_url.split('/')[-1]
        file_name_no_ext = (file_name[:-4])
        if self.hasLocalCover():
            return Extras.Config().getSerieCoverPath() + file_name_no_ext + ".jpg"

    def getImageCover(self):
        nombreImagen = self.image_url[self.image_url.rindex('/') + 1:]
        fullPath = 'C:\\Users\\bustoped\\PycharmProjects\\BabelComic-II\\images\\covers\\coverImagesCache' + os.sep + self.image_url[self.image_url.rindex('/') + 1:]
        size = (320, 496)
        if not (os.path.isfile(fullPath)):
            print('No existe el cover recuperando de : '+self.image_url)

            jpg = urllib.request.urlopen(self.image_url)
            jpgImage = jpg.read()
            fImage = open(fullPath, 'wb')
            fImage.write(jpgImage)
            fImage.close()
        fImage = open(fullPath, 'rb')
        return (Image.open(fImage))


##        serie.lb = ImageTk.PhotoImage(im.resize(size))
##        root.coverSerie = ttk.Label(root,text='imagenimagenimagen',image=serie.lb).grid(column=1,row=1,rowspan=2)

if (__name__ == '__main__'):
    volume = Volume()
    volume.id = 3816
    volume.nombre='Superman'
    volume.deck='Volume 2.'
    volume.descripcion = '<p><b>Superman (Volume 2). </b><a href="https://comicvine.gamespot.com/superman/4050-773/" data-ref-id="4050-773">Superman Volume 1</a> became <a href="https://comicvine.gamespot.com/adventures-of-superman/4050-3778/" dat'
    volume.AnioInicio = 1987
    volume.cantidadNumeros =228
    volume.image_url = 'https://comicvine.gamespot.com/api/image/scale_avatar/24856-3816-27645-1-superman.jpg'
    root = Tk()

    imagen = volume.getImageCover()
    lb = ImageTk.PhotoImage(imagen)
    coverSerie = ttk.Label(root, text='imagenimagenimagen', image=lb).grid(column=1, row=1, rowspan=2)
    root.grid()
    root.mainloop()

