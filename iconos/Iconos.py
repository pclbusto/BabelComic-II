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




