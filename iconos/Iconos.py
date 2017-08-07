import PIL.Image, PIL.ImageTk
from Entidades.Setups import Setup
import Entidades.Init
import os

class Iconos:
    setup = Entidades.Init.Session().query(Setup.Setup).first()
    path = setup.directorioBase+os.sep+"iconos"+os.sep
    pilImagenLookup = PIL.Image.open(path+"Magnifying-Glass-icon.png")
    pilImageLogo = PIL.Image.open(path+"Logo-Editorial.png")
    pilImageExpansion = PIL.Image.open(path+"expansion.png")
    pilImageFirst = PIL.Image.open(path+"first.png")
    pilImagePrev = PIL.Image.open(path+"prev.png")
    pilImageNext = PIL.Image.open(path+"next.png")
    pilImageLast = PIL.Image.open(path+"last.png")
    pilImageCoverGenerica =  PIL.Image.open(path+"CoverGenerica.png")
    pilImagePaginaDoblada = PIL.Image.open(path + "paginaDoblada.png")
    pilImageCataloged = PIL.Image.open(path + "Cataloged.png")
    pilCalidadSinCalificacion=PIL.Image.open(path + "01-Scan Sin calificacion.png")
    pilCalidadMala = PIL.Image.open(path + "02-Scan Mala Calidad.png")
    pilCalidadMedia = PIL.Image.open(path + "03-Scan Media Calidad.png")
    pilCalidadBuena = PIL.Image.open(path + "04-Scan Buena Calidad.png")
    pilCalidadDigital = PIL.Image.open(path + "05-Scan Excelente Calidad.png")







