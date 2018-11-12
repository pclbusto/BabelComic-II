
from _datetime import datetime
import Extras.ComicVineSearcher
import os
import Entidades.Init
import Entidades.Agrupado_Entidades
from Entidades.Agrupado_Entidades import Setup_Vinekey_Status
from sqlalchemy import and_
import shutil
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
    def __init__(self, session=None):
        self.listaTipos = []
        self.listaDirectorios = []
        self.listaClaves = []
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

        # recuperamos la lista de tipos, claves y directorios

        for setupTipoArchivo in Entidades.Init.Session().query(Entidades.Agrupado_Entidades.Setup_Tipo_Archivo):
            self.listaTipos.append(setupTipoArchivo.tipoArchivo)
        for setupDirectorio in Entidades.Init.Session().query(Entidades.Agrupado_Entidades.Setup_Directorio):
            self.listaDirectorios.append(setupDirectorio.pathDirectorio)
        for setupVinekey in Entidades.Init.Session().query(Entidades.Agrupado_Entidades.Setup_Vinekey):
            self.listaClaves.append(setupVinekey.key)

        self.setup = self.session.query(Entidades.Agrupado_Entidades.Setup).first()
        if not self.setup:
            self.setup = Entidades.Agrupado_Entidades.Setup()
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


        vinekey = Entidades.Agrupado_Entidades.Setup_Vinekey()

        vinekey = self.session.query(Entidades.Agrupado_Entidades.Setup_Vinekey).filter(Entidades.Agrupado_Entidades.Setup_Vinekey.key==clave).first()
        if (vinekey):
            for entidad in Extras.ComicVineSearcher.ComicVineSearcher.EntidadesPermitidas:
                status = Entidades.Agrupado_Entidades.Setup_Vinekey_Status(key=vinekey.key, recursoId = entidad,cantidadConsultas =0,fechaHoraInicioConsulta=0)
                self.session.add(status)
            self.session.commit()

    def addClave(self, clave):

        claveObj = Entidades.Agrupado_Entidades.Setup_Vinekey()
        claveObj.key=clave
        print(claveObj)
        self.session.add(claveObj)
        self.session.commit()
        self.__initStatus__(clave)

    def addTipo(self, tipo):

        tipoObj = Entidades.Agrupado_Entidades.Setup_Tipo_Archivo(tipoArchivo=tipo)
        self.session.add(tipoObj)
        self.session.commit()

    def __updateStatus__(self, key, recurso):
        '''
        para la clave key  y el recurso recurso incrementa en uno el contador.
        :param key: clave de vine comic
        :param recurso: identifica si es volumes, comic, editoria, etc
        :return: None
        '''
        statusVinekey = self.session.query(Entidades.Agrupado_Entidades.Setup_Vinekey_Status).filter(
            and_(Entidades.Agrupado_Entidades.Setup_Vinekey_Status.key==key,
                 Entidades.Agrupado_Entidades.Setup_Vinekey_Status.recursoId==recurso)).first()
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
        self.session.commit()

    def addDirectorio(self, directorio):
        directorioObj = Entidades.Agrupado_Entidades.Setup_Directorio(pathDirectorio=directorio)
        self.session.add(directorioObj)
        self.session.commit()
        if not os.path.exists(directorio):
            os.makedirs(directorio+os.sep+'images'+os.sep+'coversvolumes')

    def __delAllTipos__(self):
        self.session.query(Entidades.Agrupado_Entidades.Setup_Tipo_Archivo).delete()
        self.session.commit()
        self.listaTipos = []

    def __delAllDirectorios__(self):
        self.session.query(Entidades.Agrupado_Entidades.Setup_Directorio).delete()
        self.session.commit()
        self.listaDirectorios = []

    def __delAllClaves__(self):
        self.session.query(Entidades.Agrupado_Entidades.Setup_Vinekey).delete()
        self.session.query(Entidades.Agrupado_Entidades.Setup_Vinekey_Status).delete()
        self.session.commit()
        self.listaClaves = []

    def setListaTipos(self, listaTipos=[]):
        self.__delAllTipos__()
        if listaTipos is not None:
            for tipo in listaTipos:
                self.addTipo(tipo)

    def delClave(self, clave):
        self.session.query(Entidades.Agrupado_Entidades.Setup_Vinekey).filter(
            Entidades.Agrupado_Entidades.Setup_Vinekey.key==clave).delete()
        self.session.query(Entidades.Agrupado_Entidades.Setup_Vinekey_Status).filter(
            Entidades.Agrupado_Entidades.Setup_Vinekey_Status.key == clave).delete()

        self.session.commit()

    def delTipo(self, tipo):
        self.session.query(Entidades.Agrupado_Entidades.Setup_Tipo_Archivo).filter(
            Entidades.Agrupado_Entidades.Setup_Tipo_Archivo.tipoArchivo==tipo).delete()
        self.session.commit()

    def delDirectorio(self, directorio):
        self.session.query(Entidades.Agrupado_Entidades.Setup_Tipo_Archivo).filter(
            Entidades.Agrupado_Entidades.Setup_Directorio.pathDirectorio == directorio).delete()
        self.session.commit()

    def setListaDirectorios(self, listaDirectorios=[]):
        self.__delAllDirectorios__()
        if listaDirectorios:
            for directorio in listaDirectorios:
                self.addDirectorio(directorio)

    def setListaClaves(self, listaClaves=[]):
        self.__delAllClaves__()
        if listaClaves is not None:
            for clave in listaClaves:
                self.addClave(clave)

    def __dellAllConfig__(self):
        self.session.query(Entidades.Agrupado_Entidades.Setup).delete()
        self.session.commit()

    def setConfig(self, directorioBase, cantidadComicsPorPagina):
        self.__borrarCrearDirectoriosDesdeBase__(directorioBase)
        if directorioBase is not None:
            self.setup.directorioBase = directorioBase
        else:
            self.setup.directorioBase = ''
        if cantidadComicsPorPagina<=30 and cantidadComicsPorPagina>=1:
            self.setup.cantidadComicsPorPagina = cantidadComicsPorPagina

        self.addSetup(self.setup)

    def __borrarCrearDirectoriosDesdeBase__(self,directorioBase):
        if os.path.exists(self.setup.directorioBase+os.sep+'images'):
            shutil.rmtree(self.setup.directorioBase+os.sep+'images')
        os.makedirs(directorioBase+os.sep+'images')
        os.makedirs(directorioBase + os.sep + 'images'+os.sep+'coversvolumes')
        os.makedirs(directorioBase + os.sep + 'images' + os.sep + 'logo publisher')
        os.makedirs(directorioBase + os.sep + 'images' + os.sep + 'searchCache')
        os.makedirs(directorioBase + os.sep + 'images' + os.sep + 'coverIssuesThumbnails')
        shutil.copyfile("../sin_caratula.jpg", "../images/coverIssuesThumbnails/sin_caratula.jpg")
        shutil.copyfile("../sin_caratula_publisher.jpg", "../images/logo publisher/sin_caratula_publisher.jpg")

    def addSetup(self, setup):
        setupObj = setup
        self.session.add(setupObj)
        self.session.commit()


    def __getClaveMenosUsadaPorRecurso__(self, recurso):
        statusVineStatus = self.session.query(Setup_Vinekey_Status).filter(Setup_Vinekey_Status.recursoId==recurso).order_by(
            Setup_Vinekey_Status.cantidadConsultas.desc()).first()
        if statusVineStatus is not None:
            self.__updateStatus__(statusVineStatus.key,recurso)
            return  statusVineStatus.key
        return ""
    def validarRecurso(self,recurso):
        return recurso in ["volumes","issues", "publishers","issue","volume","story_arc_credits"]
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
    config.addClave('7e4368b71c5a66d710a62e996a660024f6a868d4')
    # config.__delAllTipos__()
    config.addTipo('cbz')
    config.addTipo('cbr')
    # config.__delAllClaves__()
    # config.addClave('64f7e65686c40cc016b8b8e499f46d6657d26752')
    # config.__initStatus__('64f7e65686c40cc016b8b8e499f46d6657d26752')
    # config.addClave('7e4368b71c5a66d710a62e996a660024f6a868d4')
        # config.__initStatus__('7e4368b71c5a66d710a62e996a660024f6a868d4')
    # config.__updateStatus__('7e4368b71c5a66d710a62e996a660024f6a868d4','volumes')

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


