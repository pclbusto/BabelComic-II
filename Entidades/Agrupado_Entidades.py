import Entidades.Init
import os
import zipfile
import rarfile
import Entidades.Init
from PIL import Image, ImageTk
from sqlalchemy import Column, Integer, String, and_,ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from rarfile import NotRarFile, BadRarFile
from zipfile import BadZipFile
from io import BytesIO
from sqlalchemy import Sequence


comicbook_info_arco_argumental = Table('comicbook_info_arco_argumental', Entidades.Init.Base.metadata,
                          Column('id_comicbooks_Info',Integer, ForeignKey('comicbooks_info.id_comicbooks_Info')),
                          Column('id_arco_argumental',Integer, ForeignKey('arcos_argumentales.id_arco_argumental'))
)

class Setup(Entidades.Init.Base):
    __tablename__='Setups'
    setupkey = Column(Integer, primary_key=True)
    '''desde este direcotrio se calculan el resto de los directorios. Por esto 
    este directorio debe ser donde esta el proyecto
    '''
    directorioBase = Column(String,default='')

    '''sirve para paginar la consulta. Manejar tanatos elementos de una puede ser bloqueante para la gui'''
    cantidadComicsPorPagina = Column(Integer,nullable=False,default=18)
    '''guarda el id del ultimo volumen utilizado'''
    ultimoVolumeIdUtilizado = Column(String,default='')
    '''guarda el ultimo numero consultado'''
    ultimoNumeroConsultadoDesde = Column(Integer,default=0)
    ultimoNumeroConsultadoHasta = Column(Integer,default=0)
    anchoArbol = Column(Integer,default=100)
    '''Expresion regular para calcular donde esta el numeradoer en path del archivo'''
    expresionRegularNumero= Column(String,default='',nullable=False)

    def __repr__(self):
        return "<Setup(setupkey = '%s'\n" \
               "Cantidad Comics PorPagina = '%s'\n" \
               "Ultimo VolumeId Utilizado = '%s'\n" \
               "Ultimo Numero Consultado Desde= '%s'\n" \
               "Ultimo Numero Consultado Hasta= '%s'\n" \
               "Expresion Regular Numero= '%s'\n" \
               "Directorio Base Imagene='%s'\n)>" %(self.setupkey,
                                                  self.cantidadComicsPorPagina,
                                                  self.ultimoVolumeIdUtilizado,
                                                  self.ultimoNumeroConsultadoDesde,
                                                  self.ultimoNumeroConsultadoHasta,
                                                  self.expresionRegularNumero,
                                                  self.directorioBase)

class ArcoArgumental(Entidades.Init.Base):
    # todo implementar gui para ver y administar
    __tablename__ = 'arcos_argumentales'

    id_arco_argumental = Column(Integer, Sequence('arco_id_seq'), primary_key=True)
    id_arco_argumental_externo = Column(String,nullable=False,default='')
    nombre = Column(String,nullable=False,default='')
    deck = Column(String,nullable=False,default='')
    descripcion = Column(String,nullable=False,default='')
    ultimaFechaActualizacion =  Column(Integer,nullable=False,default='')
    ids_comicbooks_Info = relationship("Comicbooks_Info", secondary=comicbook_info_arco_argumental)

    def getIssueOrder(self,idComic):
        session = Entidades.Init.Session()
        orden = session.query(Arcos_Argumentales_Comics_Reference).filter(and_(Arcos_Argumentales_Comics_Reference.idArco == self.id, ArcosArgumentalesComics.idComic==idComic)).first()
        if orden is not None:
            return orden.orden
        return -1
    def getIssuesCount(self):
        session = Entidades.Init.Session()
        cantidad = session.query(Arcos_Argumentales_Comics_Reference).filter(Arcos_Argumentales_Comics_Reference.idArco == self.id).count()
        return cantidad

    def getCantidadTitulos(self):
        return (len(self.comics))

class Arcos_Argumentales_Comics_Reference(Entidades.Init.Base):
    '''Esta clase nos da un orden del arco. No tienen que existir los comic books info, solo guardo los
    Id externos para saber el orden y saber cuantos me faltan para completar el arco. Por esto no
    hacemos relacion de many to many que seria 1 arco contiene varios isses y 1 issue contiene varios
    arcos
    '''
    __tablename__='arcos_argumentales_comics_reference'
    id_arco_argumental = Column(String,primary_key=True)
    id_comicbook_externo = Column(String,primary_key=True)

    orden = Column(Integer)

class ComicBook(Entidades.Init.Base):

    __tablename__='Comicbooks'
    __table_args__ = {'sqlite_autoincrement': True}

    extensionesSoportadas = ['jpg', 'png', 'gif', 'jpeg']

    path = Column(String,unique=True)
    id_comicbook = Column(Integer, Sequence('comicbook_id_seq'), primary_key=True)
    id_comicbook_info = Column(String,nullable=False,default='')
    calidad = Column(Integer,nullable=False,default=0)#Sin calificar = 0 Scan malo = 1, Scan Medio=2, scan bueno=3, digital=4

    def __repr__(self):
        return "id interno={}-comic vine id={}".format(self.id_comicbook, self.id_comicbook_externo)

    def tieneArcoAlterno(self):
        return self.arcoArgumentalId != '0'

    def openCbFile(self):
        #print('En openCbFile: '+self.getTipo())
        self.paginas=[]
        if (self.getTipo().lower()=='cbz'):
            try:
                self.cbFile = zipfile.ZipFile(self.path, 'r')
                for x in self.cbFile.namelist():
                    if '.' in x:
                        if x[(x.rindex('.')-len(x)+1):].lower() in self.extensionesSoportadas:
                            self.paginas.append(x)
            except BadZipFile:
                self.cbFile = rarfile.RarFile(self.path, 'r')
                for x in self.cbFile.infolist():
                    if '.' in x.filename:
                        if x.filename[(x.filename.rindex('.')-len(x.filename)+1):].lower() in self.extensionesSoportadas:
                            self.paginas.append(x.filename)

                #self.paginas = [x.filename for x in self.cbFile.infolist() if (x.filename[-3:].lower() in ComicBook.extensionesSoportadas)]
        elif (self.getTipo().lower()=='cbr'):
            try:
                self.cbFile = rarfile.RarFile(self.path, 'r')
                for x in self.cbFile.infolist():
                    if '.' in x.filename:
                        if x.filename[(x.filename.rindex('.')-len(x.filename)+1):].lower() in self.extensionesSoportadas:
                            self.paginas.append(x.filename)

                #self.paginas = [x.filename for x in self.cbFile.infolist() if (x.filename[-3:].lower() in ComicBook.extensionesSoportadas)]
            except BadRarFile:
                self.cbFile = zipfile.ZipFile(self.path, 'r')
                for x in self.cbFile.namelist():
                    if '.' in x:
                        if x[(x.rindex('.') - len(x) + 1):].lower() in self.extensionesSoportadas:
                            self.paginas.append(x)
                #self.paginas = [x for x in self.cbFile.namelist() if (x[-3:].lower() in self.extensionesSoportadas)]

        self.paginas.sort()
        self.indicePaginaActual = 0

    def has_xml(self):
        self.openCbFile()
        xmls = [x for x in self.cbFile.namelist() if (x[-3:].lower() in ["xml"])]
        if str(self.comicId)+'.xml' in xmls:
            return True
        else:
            return False

    def editCbFile(self):
        #print('En openCbFile: '+self.getTipo())
        self.paginas=[]
        if (self.getTipo().lower()=='cbz'):
            try:
                self.cbFile = zipfile.ZipFile(self.path, 'a')
                for x in self.cbFile.namelist():
                    if '.' in x:
                        if x[(x.rindex('.')-len(x)+1):].lower() in self.extensionesSoportadas:
                            self.paginas.append(x)
            except BadZipFile:
                self.cbFile = rarfile.RarFile(self.path, 'a')
                for x in self.cbFile.infolist():
                    if '.' in x.filename:
                        if x.filename[(x.filename.rindex('.')-len(x.filename)+1):].lower() in self.extensionesSoportadas:
                            self.paginas.append(x.filename)

                #self.paginas = [x.filename for x in self.cbFile.infolist() if (x.filename[-3:].lower() in ComicBook.extensionesSoportadas)]
        elif (self.getTipo().lower()=='cbr'):
            try:
                self.cbFile = rarfile.RarFile(self.path, 'a')
                for x in self.cbFile.infolist():
                    if '.' in x.filename:
                        if x.filename[(x.filename.rindex('.')-len(x.filename)+1):].lower() in self.extensionesSoportadas:
                            self.paginas.append(x.filename)

                #self.paginas = [x.filename for x in self.cbFile.infolist() if (x.filename[-3:].lower() in ComicBook.extensionesSoportadas)]
            except BadRarFile:
                self.cbFile = zipfile.ZipFile(self.path, 'a')
                for x in self.cbFile.namelist():
                    if '.' in x:
                        if x[(x.rindex('.') - len(x) + 1):].lower() in self.extensionesSoportadas:
                            self.paginas.append(x)
                #self.paginas = [x for x in self.cbFile.namelist() if (x[-3:].lower() in self.extensionesSoportadas)]

        self.paginas.sort()
        self.indicePaginaActual = 0


    def getImagePage(self):
        print('getImagePage'+self.getNombreArchivo())
        return (Image.open(self.getPage()))

    def getCantidadPaginas(self):
        return (len(self.paginas))

    def getPage(self):
        return(BytesIO(self.cbFile.read(self.paginas[self.indicePaginaActual])))

    def getPageExtension(self):
        index = self.paginas[self.indicePaginaActual].rindex(".")-len(self.paginas[self.indicePaginaActual])

        return (self.paginas[self.indicePaginaActual][index:])

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

class Comicbooks_Info(Entidades.Init.Base):
    '''Esta clase representa la metadata del comic.
    '''
    __tablename__='comicbooks_info'

    id_comicbooks_Info = Column(Integer, Sequence('comicbook_id_seq'), primary_key=True)
    id_comicbooks_Info_externo = Column(String,nullable=False,default='')
    titulo = Column(String,nullable=False,default='')
    id_volume = Column(String, nullable=False, default='')
    nombre_volumen = Column(String,nullable=False,default='')
    numero = Column(String,nullable=False,default='0')
    fechaTapa = Column(Integer,nullable=False,default=0)  # como no hay date en sql lite esto es la cantidad de dias desde 01-01-01
    ids_arco_argumental = relationship("ArcoArgumental", secondary=comicbook_info_arco_argumental)
    arcoArgumentalNumero = Column(Integer,nullable=False,default=0) #numero dentro del arco
    resumen = Column(String,nullable=False,default='')
    nota = Column(String,nullable=False,default='')
    rating = Column(Float,nullable=False,default=0.0)
    ratingExterno = Column(Float,nullable=False,default=0.0)

    id_publisher = Column(String,nullable=False,default='')
    api_detail_url = Column(String,nullable=False,default='')
    thumbs_url  = relationship("Comicbook_Info_cover_url")

    '''Este campo se crea para ordenar los comics.
    Se cambia el numero que es de tipo int a string porque hay numeraciones comoc 616a de batman.
    El tema es que por ser string pierdo el orden entonces despues del 1 no viene el 2 si no 10.'''
    orden = Column(Integer,nullable=False,default=0 )


    def __repr__(self):
        return "titulo={}-comic vine id={}".format(self.titulo, self.id_comicbooks_Info_externo)

class Comicbook_Info_cover_url(Entidades.Init.Base):
    __tablename__ = 'comicbooks_info_cover_url'

    id_comicbooks_Info= Column(Integer, ForeignKey('comicbooks_info.id_comicbooks_Info'))
    thumb_url = Column(String, primary_key=True)
    # numero_dentro_arco = Column(Integer, nullable=False,default=0)

    def __repr__(self):
        return "thumb_url={}".format(self.thumb_url)

class ComicInVolumes(Entidades.Init.Base):
    __tablename__='ComicsInVolumes'
    # no lo pasamos a numerico porque algunos numeros tiene 11.3B

    numero = Column(String, primary_key=True)
    id_comicbook_externo = Column(String, nullable=False, default='')
    id_volume = Column(Integer, primary_key=True, default='')
    # mantenemos esto para poder borrar
    id_volume_externo = Column(Integer, primary_key=True, default='')
    titulo = Column(String, nullable=False, default='')
    site_detail_url = Column(String, nullable=False, default='')

    def __repr__(self):
        return "numero={} - id_comicbook_externo={} - id_volume_externo={} - titulo={}".format(self.numero, self.id_comicbook_externo, self.id_volume_externo, self.titulo)

class Publisher(Entidades.Init.Base):
    __tablename__='Publishers'


    id_publisher = Column(Integer, Sequence('publisher_id_seq'), primary_key=True)
    id_publisher_externo = Column(String, nullable=False, default='')
    name = Column(String, nullable=False,default='')
    deck = Column(String, nullable=False,default='')
    description = Column(String, nullable=False,default='')
    logoImagePath  = Column(String, nullable=False,default='')
    localLogoImagePath = Column(String, nullable=False,default='')
    siteDetailUrl = Column(String, nullable=False,default='')

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

    def getImageCoverPath(self):
        if not self.hasImageCover():
            self.getImageCover()
        nombreImagen = self.logoImagePath[self.logoImagePath.rindex('/') + 1:]
        session = Entidades.Init.Session()
        setup = session.query(Setup).first()

        fullPath = setup.directorioBase + os.sep + 'images' + os.sep + 'logo publisher' + os.sep + self.logoImagePath[
                                                                                                   self.logoImagePath.rindex(
                                                                                                       '/') + 1:]
        return(fullPath)

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
        return "<Publisher(id_publisher='{}',name='{}', id_publisher_externo='{}'".format(self.id_publisher, self.localLogoImagePath, self.id_publisher_externo)

class Volume(Entidades.Init.Base):
    # todo comics que si tenemos y comics que faltan. poder tener ese dato para mostrar
    __tablename__='Volumens'
    id_volume = Column(Integer, Sequence('volumen_id_seq'), primary_key=True)
    id_volume_externo = Column(String, nullable=False, default='')
    nombre = Column(String,nullable=False,default='')
    deck = Column(String,nullable=False,default='')
    descripcion = Column(String,nullable=False,default='')
    image_url = Column(String,nullable=False,default='')  # la mas grande. Las chicas las hacemos locales.
    id_publisher = Column(String,nullable=False,default='')
    id_publisher_externo= Column(String, nullable=False, default='')
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
        return("http://comicvine/"+self.id_volume_externo)

    def __repr__(self):
        return "<Volume(name={}, id_volume={}, id_volume_externo={}, cantidad nros={}, descripcion={}," \
               "image_url={}, publisher_name={}, Año inicio={} )>".format(self.nombre,self.id_volume,self.id_volume_externo, self.cantidadNumeros,self.descripcion,
                                                                           self.image_url, self.publisher_name,
                                                                          self.AnioInicio)


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
            setup = session.query(Entidades.Setups.Setup.Setup).first()
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
        setup = session.query(Entidades.Setups.Setup.Setup).first()

        return setup.directorioBase + os.sep + 'images' + os.sep + 'coversvolumes' + os.sep + self.image_url[
                                                                                       self.image_url.rindex('/') + 1:]

    def getImageCover(self):

        if not self.hasImageCover():
            return (Iconos.pilImageCoverGenerica)
        '''Asumo que se llamo antes al has cover'''
        nombreImagen = self.image_url[self.image_url.rindex('/') + 1:]
        session = Entidades.Init.Session()
        setup = session.query(Entidades.Setups.Setup.Setup).first()

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

class SetupDirectorio(Entidades.Init.Base):
    __tablename__='SetupDirectorios'
    pathDirectorio = Column(String, primary_key=True)

    def __repr__(self):
        return "<SetupDirectorio(Directorio='%s')>" %(self.pathDirectorio)

class SetupTipoArchivo(Entidades.Init.Base):
    __tablename__='SetupTiposArchivo'
    tipoArchivo = Column(String, primary_key=True)

    def __repr__(self):
        return "<SetupTiposArchivo(tipoArchivo='%s')>" %(self.tipoArchivo)

class SetupVinekey(Entidades.Init.Base):
    __tablename__='SetupVineKeys'
    key = Column(String, primary_key=True)

    def __repr__(self):
        return "<SetupVineKeys(Clave='%s')>" %(self.key)


class SetupVinekeyStatus(Entidades.Init.Base):
    __tablename__='SetupVineKeysStatus'
    key = Column(String, primary_key=True)
    recursoId = Column(String, primary_key=True)
    cantidadConsultas = Column(Integer)
    fechaHoraInicioConsulta = Column(Integer)

    def __repr__(self):
        return "<SetupVinekeyStatus(Clave='%s')>" %(self.key)