
from _datetime import datetime
import Extras.ComicVineSearcher
import os
import Entidades.Init
import Entidades.Setups.SetupTipoArchivo
import Entidades.Setups.SetupDirctorio
import Entidades.Setups.SetupVineKey
from Entidades.Setups.SetupVinekeysStatus import SetupVinekeyStatus
import Entidades.Setups.Setup
from sqlalchemy import and_
'''

configuracion->lista de directorios
    \
     \
      \->lista de extensiones
esta clase gestiona todo. mas alla que use tres tablas.
la tabla principal no tiene ningun atributo por ahora
se deja por uso futuo cuando surjan necesidades.


'''

class Config:
    PATH = "/home/pedro/Documentos/pycharmProjects/BabelComic-II/BabelComic.db"
    # PATH = "C:\\Users\\pclbu\\PycharmProjects\\BabelComic-II\\BabelComic.db"
    #PATH = "C:\\Users\\bustoped\\PycharmProjects\\BabelComic-II\\BabelComic.db"
    def __init__(self):
        # print (Config.PATH)
        # self.conexion = sqlite3.connect(Config.PATH)
        # self.conexion.row_factory = sqlite3.Row
        self.listaTipos = []
        self.listaDirectorios = []
        self.listaClaves = []

        # recuperamos la lista de tipos, claves y directorios

        for setupTipoArchivo in Entidades.Init.Session().query(Entidades.Setups.SetupTipoArchivo.SetupTipoArchivo):
            self.listaTipos.append(setupTipoArchivo.tipoArchivo)
        for setupDirectorio in Entidades.Init.Session().query(Entidades.Setups.SetupDirctorio.SetupDirectorio):
            self.listaDirectorios.append(setupDirectorio.pathDirectorio)
        for setupVinekey in Entidades.Init.Session().query(Entidades.Setups.SetupVineKey.SetupVinekey):
            self.listaClaves.append(setupVinekey.key)

        self.setup = Entidades.Init.Session().query(Entidades.Setups.Setup.Setup).first()
        if not self.setup:
            self.setup = Entidades.Setups.Setup.Setup()
            self.setup.setupkey=1
            self.setup.directorioBase=""

    def getPublisherTempLogoPath(self):
        return self.__getTempPath__("publisher")

    def getPublisherLogoPath(self):
        return self.__getPath__("publisher")

    def getSerieCoverPath(self):
        return self.__getPath__("volume")

    def getSerieTempCoverPath(self):
        return self.__getTempPath__("volume")

    def __getTempPath__(self,entidad):
        path = "imagenes\\{}\\temp\\".format(entidad)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def __getPath__(self, entidad):
        path = "imagenes\\{}\\".format(entidad)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def __initStatus__(self,clave):
        """
        para la clave de comicvine cargamos para cada recurso (entidad por la cual se consulta {publisher, publishers, story_arc, series, etc}) la cantidad de consultas
        y fecha inicio en 0. Esto es una inicializacion. Si existe para esa clave un status se deja. Esta situación ocurre cuando se modifica algo de la conf. La Gui borra las claves
        y las vuelve a cargar nuevamente.
        :param clave: key del sitio comicvine.
        :return:None
        """

        session = Entidades.Init.Session()
        vinekey = Entidades.Setups.SetupVineKey.SetupVinekey()

        vinekey = session.query(Entidades.Setups.SetupVineKey.SetupVinekey).filter(Entidades.Setups.SetupVineKey.SetupVinekey.key==clave).first()
        if (vinekey):
            for entidad in Extras.ComicVineSearcher.ComicVineSearcher.EntidadesPermitidas:
                status = Entidades.Setups.SetupVinekeysStatus.SetupVinekeyStatus(key=vinekey.key, recursoId = entidad,cantidadConsultas =0,fechaHoraInicioConsulta=0)
                session.add(status)
        session.commit()

    def addClave(self, clave):
        session = Entidades.Init.Session()
        claveObj = Entidades.Setups.SetupVineKey.SetupVinekey(key=clave)
        session.add(claveObj)
        session.commit()

    def addTipo(self, tipo):
        session = Entidades.Init.Session()
        tipoObj = Entidades.Setups.SetupTipoArchivo.SetupTipoArchivo(tipoArchivo=tipo)
        session.add(tipoObj)
        session.commit()

    def __updateStatus__(self, key, recurso):
        '''
        para la clave key  y el recurso recurso incrementa en uno el contador.
        :param key: clave de vine comic
        :param recurso: identifica si es volumes, comic, editoria, etc
        :return: None
        '''
        session = Entidades.Init.Session()
        statusVinekey = session.query(Entidades.Setups.SetupVinekeysStatus.SetupVinekeyStatus).filter(
            and_(Entidades.Setups.SetupVinekeysStatus.SetupVinekeyStatus.key==key,
                 Entidades.Setups.SetupVinekeysStatus.SetupVinekeyStatus.recursoId==recurso)).first()
        print(statusVinekey)
        if (statusVinekey):
            fecha_previa_stamp = statusVinekey.fechaHoraInicioConsulta
            fecha_actual_stamp = datetime.now().timestamp()
            if (fecha_actual_stamp - fecha_previa_stamp) >3600:
                statusVinekey.cantidadConsultas = 0
                statusVinekey.fechaHoraInicioConsulta = datetime.now().timestamp()
            else:
                statusVinekey.cantidadConsultas += 1
        #actualizamos
        session.commit()

    def addDirectorio(self, directorio):
        session = Entidades.Init.Session()
        directorioObj = Entidades.Setups.SetupDirctorio.SetupDirectorio(pathDirectorio=directorio)
        session.add(directorioObj)
        session.commit()
        if not os.path.exists(directorio):
            os.makedirs(directorio+os.sep+'images'+os.sep+'coversvolumes')



    def __delAllTipos__(self):
        session = Entidades.Init.Session()
        session.query(Entidades.Setups.SetupTipoArchivo.SetupTipoArchivo).delete()
        session.commit()
        self.listaTipos = []

    def __delAllDirectorios__(self):
        session = Entidades.Init.Session()
        session.query(Entidades.Setups.SetupDirctorio.SetupDirectorio).delete()
        session.commit()
        self.listaDirectorios = []

    def __delAllClaves__(self):
        session = Entidades.Init.Session()
        session.query(Entidades.Setups.SetupVineKey.SetupVinekey).delete()
        session.commit()
        self.listaClaves = []

    def setListaTipos(self, listaTipos=[]):
        self.__delAllTipos__()
        if listaTipos is not None:
            for tipo in listaTipos:
                self.addTipo(tipo)

    def delClave(self, clave):
        session = Entidades.Init.Session()
        session.query(Entidades.Setups.SetupVineKey.SetupVinekey).filter(
            Entidades.Setups.SetupVineKey.SetupVinekey.key==clave).delete()
        session.commit()

    def delTipo(self, tipo):
        session = Entidades.Init.Session()
        session.query(Entidades.Setups.SetupTipoArchivo.SetupTipoArchivo).filter(
            Entidades.Setups.SetupTipoArchivo.SetupTipoArchivo.tipoArchivo==tipo).delete()
        session.commit()

    def delDirectorio(self, directorio):
        session = Entidades.Init.Session()
        session.query(Entidades.Setups.SetupTipoArchivo.SetupTipoArchivo).filter(
            Entidades.Setups.SetupDirctorio.SetupDirectorio.pathDirectorio == directorio).delete()
        session.commit()

    def setListaDirectorios(self, listaDirectorios=[]):
        self.__delAllDirectorios__()
        if listaDirectorios:
            for directorio in listaDirectorios:
                self.addDirectorio(directorio)

    def setListaClaves(self, listaClaves=[]):
        self.__delAllClaves__()
        if listaClaves:
            for clave in listaClaves:
                self.addClave(clave)

    def __dellAllConfig__(self):
        session = Entidades.Init.Session()
        session.query(Entidades.Setups.Setup.Setup).delete()
        session.commit()

    def setConfig(self, directorioBase):
        #self.__dellAllConfig__()
        #print("DIRECTORIO: "+directorioBase)
        if directorioBase is not None:
         #   print("por aca")
            self.setup.directorioBase = directorioBase
        else:
            self.setup.directorioBase = ''
        self.addSetup(self.setup)

    def addSetup(self, setup):
        session = Entidades.Init.Session()
        setupObj = setup
        session.add(setupObj)
        session.commit()


    def __getClaveMenosUsadaPorRecurso__(self, recurso):
        session = Entidades.Init.Session()
        statusVineStatus = session.query(SetupVinekeyStatus).filter(SetupVinekeyStatus.recursoId==recurso).order_by(
            SetupVinekeyStatus.cantidadConsultas.desc()).first()
        if statusVineStatus is not None:
            self.__updateStatus__(statusVineStatus.key,recurso)
            return  statusVineStatus.key
        return ""
    def validarRecurso(self,recurso):
        return recurso in ["volumes","issues", "publishers","issue"]
    def getClave(self, recurso):
        if self.validarRecurso(recurso):
            clave = self.__getClaveMenosUsadaPorRecurso__(recurso)
            print("CLAVE: "+clave)
            return clave
        else:
            print("no existe el recurso " + recurso)
        return ""

if __name__ == "__main__":
    config = Config()
    config.addTipo('cbz')
    config.delTipo('cbz')
    config.__delAllClaves__()
    config.addClave('64f7e65686c40cc016b8b8e499f46d6657d26752')
    config.__initStatus__('64f7e65686c40cc016b8b8e499f46d6657d26752')
    config.addClave('7e4368b71c5a66d710a62e996a660024f6a868d4')
    config.__initStatus__('7e4368b71c5a66d710a62e996a660024f6a868d4')
    config.__updateStatus__('7e4368b71c5a66d710a62e996a660024f6a868d4','volumes')
    config.__delAllTipos__()
    config.addTipo('cbz')
    config.addTipo('cbr')
    # clave = config.getClave("volumes")
    # print(clave)
    #    config.addDirectorio('c:\\Users\\bustoped\\Downloads\\Comics\\')
    #    config.delDirectorio('c:\\Users\\bustoped\\Downloads\\Comics\\')
    #    config.addTipo('cbz')
    # cursor = config.conexion.cursor()

    #    config.delTipo('cb7')
    #    config.delDirectorio('home')

    # for dire in config.listaClaves:
    #   print(dire)
#    config.addTipo('cb7')


