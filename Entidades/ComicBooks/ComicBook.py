import os
import zipfile
import rarfile
from PIL import Image, ImageTk
from sqlalchemy import Column, Integer, String, Float,ForeignKey
import Entidades.Init
from sqlalchemy import Sequence


class ComicBook(Entidades.Init.Base):

    __tablename__='Comicbooks'
    __table_args__ = {'sqlite_autoincrement': True}

    extensionesSoportadas = ['jpg', 'png', 'gif']


    path = Column(String,unique=True)
    comicVineId = Column(String,nullable=False,default='')
    titulo = Column(String,nullable=False,default='')
    volumeId = Column(String, nullable=False, default='')
    volumeNombre = Column(String,nullable=False,default='')
    numero = Column(Integer,nullable=False,default=0)
    fechaTapa = Column(Integer,nullable=False,default=0)  # como no hay date en sql lite esto es la cantidad de dias desde 01-01-01
    arcoArgumentalId = Column(String,nullable=False,default=0) #id arco
    arcoArgumentalNumero = Column(Integer,nullable=False,default=0) #numero dentro del arco
    resumen = Column(String,nullable=False,default='')
    nota = Column(String,nullable=False,default='')
    rating = Column(Float,nullable=False,default=0.0)
    ratingExterno = Column(Float,nullable=False,default=0.0)
    comicId = Column(Integer, primary_key=True)
    publisherId = Column(String,nullable=False,default='')
    api_detail_url = Column(String,nullable=False,default='')
    thumb_url  = Column(String,nullable=False,default='')
    calidad = Column(Integer,nullable=False,default=0)#Sin calificar = 0 Scan malo = 1, Scan Medio=2, scan bueno=3, digital=4


    def __repr__(self):
        return "<Comicbooks(Id Volumen='%s'\n" \
               "Título='%s'\n" \
               "Path='%s'\n" \
               "arco id: '%s'\n" \
               "arco numero:'%s'\n" \
               "id Comic Vine:'%s')\n" \
               "Numero='%s'>" % (
        self.volumeId,  self.titulo, self.path, self.arcoArgumentalId, self.arcoArgumentalNumero,self.comicVineId,self.numero)

    # ##        rarfile.UNRAR_TOOL = 'C:\\Program Files\\WinRAR'

    def tieneArcoAlterno(self):
        return self.arcoArgumentalId != '0'

    def openCbFile(self):
        #print('En openCbFile: '+self.getTipo())
        if (self.getTipo().lower()=='cbz'):
            self.cbFile = zipfile.ZipFile(self.path, 'r')
            self.paginas = [x for x in self.cbFile.namelist() if (x[-3:].lower() in self.extensionesSoportadas)]
        elif (self.getTipo().lower()=='cbr'):
            self.cbFile = rarfile.RarFile(self.path, 'r')
            self.paginas = [x.filename for x in self.cbFile.infolist() if (x.filename[-3:].lower() in ComicBook.extensionesSoportadas)]
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



