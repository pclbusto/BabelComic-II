
from PIL import Image, ImageTk
from tkinter import Tk, ttk
import os
import urllib.request
import Extras.Config
from sqlalchemy import Column, Integer, String
import Entidades.Init
from Entidades.Setups.Setup import Setup
from  iconos.Iconos import Iconos
import Entidades.ComicBooks.ComicBook
from sqlalchemy import Sequence

class Volume(Entidades.Init.Base):
    # todo comics que si tenemos y comics que faltan. poder tener ese dato para mostrar
    __tablename__='Volumens'
    id_volume = Column(Integer, Sequence('volumen_id_seq'), primary_key=True)
    id_externo = Column(String, nullable=False, default='')
    nombre = Column(String,nullable=False,default='')
    deck = Column(String,nullable=False,default='')
    descripcion = Column(String,nullable=False,default='')
    image_url = Column(String,nullable=False,default='')  # la mas grande. Las chicas las hacemos locales.
    publisherId = Column(String,nullable=False,default='')
    publisher_name=Column(String,nullable=False,default='')
    AnioInicio = Column(Integer,nullable=False,default=0)
    cantidadNumeros = Column(Integer,nullable=False,default=0)


    def hasPublisher(self):
        return (self.publisherId!='0')


    def getIssuesCount(self,session):
        '''

        :param session: para poder obtener el resultado mas fresco y no tener errores de threads y esas cosas.
        :return: la cantidad total de issues asociados a este volumen sin importar si estan duplicados.
        '''
        return session.query(Entidades.ComicBooks.ComicBook.ComicBook).filter(Entidades.ComicBooks.ComicBook.ComicBook.volumeId==self.id).count()

    def get_url(self):
        return("http://comicvine/"+self.id_externo)

    def __repr__(self):
        return "<Volume(name={},  cantidad nros={}, descripcion={}, id_volume={}," \
               "image_url={}, publisher_name={}, Año inicio={} )>".format(self.nombre, self.cantidadNumeros,self.descripcion,
                                                                          self.id_volumen, self.image_url, self.publisher_name,
                                                                          self.AnioInicio)

    # volume.nombre,

    #                                                           volume.cantidadNumeros,
    #                                                           volume.descripcion,
    #                                                           volume.id,
    #                                                           volume.image_url,
    #                                                           volume.publisher_name,
    #                                                           volume.AnioInicio

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

    def hasImageCover(self):
        '''
        que validar aca. es una url no sabemos si tiene o no algo
        asi que solo valido si tiene la barra como para calcular el

        '''
        if "/" in self.image_url:
            nombreImagen = self.image_url[self.image_url.rindex('/') + 1:]
            session = Entidades.Init.Session()
            setup = session.query(Setup).first()
            fullPath = setup.directorioBase + os.sep + 'images' + os.sep + 'coversvolumes' + os.sep + self.image_url[
                                                                                                      self.image_url.rindex(
                                                                                                          '/') + 1:]
            if not (os.path.isfile(fullPath)):
                jpg = urllib.request.urlopen(self.image_url)
                jpgImage = jpg.read()
                fImage = open(fullPath, 'wb')
                fImage.write(jpgImage)
                fImage.close()
                if jpgImage is not None:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    def getImagePath(self):
        if not self.hasImageCover():
            self.getImageCover()

        session = Entidades.Init.Session()
        setup = session.query(Setup).first()

        return setup.directorioBase + os.sep + 'images' + os.sep + 'coversvolumes' + os.sep + self.image_url[
                                                                                       self.image_url.rindex('/') + 1:]

    def getImageCover(self):

        if not self.hasImageCover():
            return (Iconos.pilImageCoverGenerica)
        '''Asumo que se llamo antes al has cover'''
        nombreImagen = self.image_url[self.image_url.rindex('/') + 1:]
        session = Entidades.Init.Session()
        setup = session.query(Setup).first()

        fullPath = setup.directorioBase+os.sep+'images'+os.sep+'coversvolumes' + os.sep + self.image_url[self.image_url.rindex('/') + 1:]
        # print("imagen: "+ fullPath)
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


