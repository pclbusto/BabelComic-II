import os
import zipfile
import rarfile
from PIL import Image, ImageTk
from sqlalchemy import Column, Integer, String, Numeric
import Entidades.Init


class ComicBook(Entidades.Init.Base):
    __tablename__='Comicbooks'
    extensionesSoportadas = ['jpg', 'png', 'gif']

    path = Column(String, primary_key=True)
    comicId = Column(String)
    titulo = Column(String)
    volumeId = Column(String)
    volumeNombre = Column(String)
    numero = Column(Integer)
    fechaTapa = Column(Integer)  # como no hay date en sql lite esto es la cantidad de dias desde 01-01-01
    arcoArgumentalId = Column(Integer) #id arco
    arcoArgumentalNumero = Column(Integer) #numero dentro del arco
    resumen = Column(String)
    nota = Column(String)
    rating = Column(Numeric)
    ratingExterno = Column(Numeric)

    def __repr__(self):
        return "<Comicbooks(nombre='%s', numero='%s', path='%s')>" %(self.volumeNombre, self.numero,self.path)

    # ##        rarfile.UNRAR_TOOL = 'C:\\Program Files\\WinRAR'

    def create(self, path, titulo='', volume=-1, numero=-1):
        self.path = path
        self.comicId = -1
        self.titulo = titulo
        self.volumeId = volume  # de descubre que el campo deck de volume tiene la version del volumen.
        self.numero= numero
        self.fechaTapa = 1 # como no hay date en sql lite esto es la cantidad de dias desde 01-01-01
        self.arcoArgumentalId = -1
        self.arcoArgumentalNumero = -1
        self.resumen = ''
        self.paginas = []

    def tieneArcoAlterno(self):
         return self.arcoArgumentalId != -1

    def openCbFile(self):
        #print('En openCbFile: '+self.getTipo())
        if (self.getTipo().lower()=='cbz'):
            self.cbFile = zipfile.ZipFile(self.path, 'r')
            self.paginas = [x for x in self.cbFile.namelist() if (x[-3:].lower() in self.extensionesSoportadas)]
        elif (self.getTipo().lower()=='cbr'):
            self.cbFile = rarfile.RarFile(self.path, 'r')
            self.paginas = [x.filename for x in self.cbFile.infolist() if (x.filename[-3:].lower() in ComicBook.extensionesSoportadas)]
        #print(len(self.paginas))
        self.paginas.sort()
        self.indicePaginaActual = 0

    def getImagePage(self):
        return (Image.open(self.getPage()))

    def getCantidadPaginas(self):
        return (len(self.paginas))

    def getPage(self):
        return(self.cbFile.open(self.paginas[self.indicePaginaActual]))

    def getPageExtension(self):
        #print('En Comicbook getPageExtension:'+str(len(self.paginas)))
        return (self.paginas[self.indicePaginaActual][-4:])

    def goto(self,index):
        if index < len(self.paginas):
            self.indicePaginaActual = index

    def getTitulo(self):
        return(self.titulo)

    def getPath(self):
        return(self.path)

    def getNumero(self):
        return(self.numero)

    def getKey(self):
        return(self.path)

    def getTipo(self):
        return(self.path[-3:])

    def getSize(self):
        tam = os.stat(self.path).st_size
        return tam

    def getNombreArchivo(self,conExtension=True):
        if conExtension:
            return(self.path[self.path.rfind(os.sep)+1:])
        else:
            return (self.path[self.path.rfind(os.sep) + 1:-4])

# ##    def __str__(self):
# ##        return ('<NOMBRE: '+self.nombre+' PATH :'+self.path)
# if __name__ == "__main__":
#     clave1 = '/root/Imagenes/Comics/superman1.cbz'
# ##    comic1=ComicBook(clave1,'Superman inicio',1,1)
# ##    comic2=ComicBook('/root/Imagenes/Comics/Green Lantern1.cbz','Origenes',1,1)
# ##    comic3=ComicBook('/root/Imagenes/Comics/Flash1.cbz','Rebirth',1,1)
# ##    comic1 = db[clave1]
# ##    print(comic1.getPath())
# ##    comic1.seriesAlternasNumero=([(1,6),(2,1)])
# ##    db[clave1]=comic1



