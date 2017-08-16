import PIL.Image, PIL.ImageTk
from Entidades.Setups import Setup
import Entidades.Init
import os

class Iconos():
    def __init__(self):
        setup = Entidades.Init.Session().query(Setup.Setup).first()
        path = setup.directorioBase+os.sep+"iconos"+os.sep
        self.pilImagenLookup = PIL.Image.open(path+"Magnifying-Glass-icon.png")
        self.pilImageLogo = PIL.Image.open(path+"Logo-Editorial.png")
        self.pilImageExpansion = PIL.Image.open(path+"expansion.png")
        self.pilImageFirst = PIL.Image.open(path+"first.png")
        self.pilImagePrev = PIL.Image.open(path+"prev.png")
        self.pilImageNext = PIL.Image.open(path+"next.png")
        self.pilImageLast = PIL.Image.open(path+"last.png")
        self.pilImageCoverGenerica =  PIL.Image.open(path+"CoverGenerica.png")
        self.pilImagePaginaDoblada = PIL.Image.open(path + "paginaDoblada.png")
        self.pilImageCataloged = PIL.Image.open(path + "Cataloged.png")
        self.pilCalidadSinCalificacion=PIL.Image.open(path + "01-Scan Sin calificacion.png")
        self.pilCalidadMala = PIL.Image.open(path + "02-Scan Mala Calidad.png")
        self.pilCalidadMedia = PIL.Image.open(path + "03-Scan Media Calidad.png")
        self.pilCalidadBuena = PIL.Image.open(path + "04-Scan Buena Calidad.png")
        self.pilCalidadDigital = PIL.Image.open(path + "05-Scan Excelente Calidad.png")







