from sqlalchemy import Column, Integer, String
import Entidades.Init
import os
import urllib.request
from  iconos.Iconos import Iconos
from Entidades.Setups.Setup import Setup
import Extras.Config
from PIL import Image, ImageTk

class Publisher(Entidades.Init.Base):
    __tablename__='Publishers'
    id_publisher = Column(String, primary_key=True)
    name = Column(String,nullable=False,default='')
    deck = Column(String,nullable=False,default='')
    description = Column(String,nullable=False,default='')
    logoImagePath  = Column(String,nullable=False,default='')
    localLogoImagePath = Column(String,nullable=False,default='')
    siteDetailUrl = Column(String,nullable=False,default='')

    def hasImageCover(self):
        '''
        que validar aca. es una url no sabemos si tiene o no algo
        asi que solo valido si tiene la barra como para calcular el

        '''
        if "/" in self.logoImagePath:
            nombreImagen = self.logoImagePath[self.logoImagePath.rindex('/') + 1:]
            session = Entidades.Init.Session()
            setup = session.query(Setup).first()
            fullPath = setup.directorioBase + os.sep + 'images' + os.sep + 'logo publisher' + os.sep + self.logoImagePath[
                                                                                                      self.logoImagePath.rindex(
                                                                                                          '/') + 1:]
            if not (os.path.isfile(fullPath)):
                jpg = urllib.request.urlopen(self.logoImagePath)
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
    def getImageCover(self):
        if not self.hasImageCover():
            return (Iconos.pilImageLogo)

        nombreImagen = self.logoImagePath[self.logoImagePath.rindex('/') + 1:]
        session = Entidades.Init.Session()
        setup = session.query(Setup).first()

        fullPath = setup.directorioBase+os.sep+'images'+os.sep+'logo publisher' + os.sep + self.logoImagePath[self.logoImagePath.rindex('/') + 1:]
        # print("imagen: "+ fullPath)

        size = (320, 496)
        if not (os.path.isfile(fullPath)):
            print('No existe el cover recuperando de : '+self.logoImagePath)
            jpg = urllib.request.urlopen(self.logoImagePath)
            jpgImage = jpg.read()
            fImage = open(fullPath, 'wb')
            fImage.write(jpgImage)
            fImage.close()
        fImage = open(fullPath, 'rb')
        return (Image.open(fImage))

    def __repr__(self):
        return "<Publisher(id_publisher='%s',name='%s')>" %(self.id_publisher, self.name)

