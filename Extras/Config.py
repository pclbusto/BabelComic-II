import sqlite3
import datetime
# import Extras.ComicVineSearcher
import os

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
    # PATH = "/home/pedro/Documentos/pycharmProjects/BabelComic-II/BabelComic.db"
    # PATH = "C:\\Users\\pclbu\\PycharmProjects\\BabelComic-II\\BabelComic.db"
    PATH = "C:\\Users\\bustoped\\PycharmProjects\\BabelComic-II\\BabelComic.db"
    def __init__(self):
        print (Config.PATH)
        self.conexion = sqlite3.connect(Config.PATH)
        self.conexion.row_factory = sqlite3.Row
        self.listaTipos = []
        self.listaDirectorios = []
        self.listaClaves = []

        cursor = self.conexion.cursor()
        # recuperamos la lista de tipos
        cursor.execute('''SELECT tipo From config_TipoArchivo''')
        rows = cursor.fetchall()
        for row in rows:
            self.listaTipos.append(row['tipo'])
        # recuperamos la lista de directorios
        cursor.execute('''SELECT pathDirectorio From config_Directorios''')
        rows = cursor.fetchall()
        for row in rows:
            self.listaDirectorios.append(row['pathDirectorio'])
        # recuperamos la lista de claves
        cursor.execute('''SELECT key  From config_VineKeys''')
        rows = cursor.fetchall()
        for row in rows:
            # print(row['key'])
            self.listaClaves.append(row['key'])

    def getPublisherTempLogoPath(self):
        return self.__getTempPath__("publisher")

    def getPublisherLogoPath(self):
        return self.__getPath__("publisher")

    def getSerieCoverPath(self):
        return self.__getPath__("serie")

    def getSerieTempCoverPath(self):
        return self.__getTempPath__("serie")

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
        cursor = self.conexion.cursor()
        cursor.execute('''SELECT key FROM config_VineKeysStatus WHERE key=:key AND recurso=:recurso''', {"key": clave,"recurso":'volumes'})
        row = cursor.fetchone()
        if (not row):
            for entidad in Extras.ComicVineSearcher.ComicVineSearcher.EntidadesPermitidas:
                cursor.execute('''INSERT INTO config_VineKeysStatus (key, recurso, cantidadTotalConsultas, fechaHoraInicioConsulta) values (?,?,?,?)''', (clave,entidad,0,datetime.datetime.now().timestamp() ))
        self.conexion.commit()

    def addClave(self, clave):
        cursor = self.conexion.cursor()
        cursor.execute('''INSERT INTO config_VineKeys (key) values (:key)''', {"key":clave})
        self.listaClaves.append(clave)
        self.conexion.commit()
        self.__initStatus__(clave)

    def addTipo(self, tipo):
        cursor = self.conexion.cursor()
        cursor.execute('''INSERT INTO config_TipoArchivo (tipo) values (:tipo)''', {"tipo":tipo})
        self.listaTipos.append(tipo)
        self.conexion.commit()

    def __updateStatus__(self, key, recurso):
        '''
        para la clave key  y el recurso recurso incrementa en uno el contador.
        :param key: clave de vine comic
        :param recurso: identifica si es volumes, comic, editoria, etc
        :return: None
        '''
        cursor = self.conexion.cursor()
        #actualizamos
        cursor.execute('''UPDATE config_VineKeysStatus SET cantidadTotalConsultas = cantidadTotalConsultas+1 , fechaHoraInicioConsulta = :fechaHoraInicioConsulta where key=:key and recurso = :recurso''', {"key":key, "recurso":recurso, "fechaHoraInicioConsulta":datetime.datetime.now().timestamp()})
        self.conexion.commit()

    def addDirectorio(self, directorio):
        cursor = self.conexion.cursor()
        cursor.execute('''INSERT INTO config_Directorios (pathDirectorio) values (:path)''', {"path":directorio})
        self.listaDirectorios.append(directorio)
        self.conexion.commit()

    def __delAllTipos__(self):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE FROM config_TipoArchivo''')
        self.conexion.commit()
        self.listaTipos = []

    def __delAllDirectorios__(self):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE FROM config_Directorios''')
        self.conexion.commit()
        self.listaDirectorios = []

    def __delAllClaves__(self):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE FROM config_VineKeys''')
        self.conexion.commit()
        self.listaClaves = []

    def setListaTipos(self, listaTipos=[]):
        self.__delAllTipos__()
        if listaTipos:
            for tipo in listaTipos:
                self.addTipo(tipo)

    def delClave(self, clave):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE FROM config_VineKeys WHERE key=?''', (clave,))
        self.listaClaves.remove(clave)
        self.conexion.commit()

    def delTipo(self, tipo):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE FROM config_TipoArchivo WHERE tipo=?''', (tipo,))
        self.listaTipos.remove(tipo)
        self.conexion.commit()

    def delDirectorio(self, directorio):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE FROM config_Directorios WHERE pathDirectorio=?''', (directorio,))
        self.listaDirectorios.remove(directorio)
        self.conexion.commit()

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

    def __getClaveMenosUsadaPorRecurso__(self, recurso):
        cursor = self.conexion.cursor()
        print("SELECT key,min(cantidadTotalConsultas) as cantidadTotalConsultas FROM config_VineKeysStatus WHERE recurso="+ recurso)
        cursor.execute('''SELECT key,min(cantidadTotalConsultas) as cantidadTotalConsultas FROM config_VineKeysStatus WHERE recurso=?''', (recurso,))
        row = cursor.fetchone()
        if row:
            self.__updateStatus__(row['key'],recurso)
            return  row['key']
        return ""
    def validarRecurso(self,recurso):
        return recurso in ["volumes","issues", "publishers"]
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
    config.__delAllClaves__()
    config.addClave('64f7e65686c40cc016b8b8e499f46d6657d26752')
    config.addClave('7e4368b71c5a66d710a62e996a660024f6a868d4')
    clave = config.getClave("volumes")
    print(clave)
    #    config.addDirectorio('c:\\Users\\bustoped\\Downloads\\Comics\\')
    #    config.delDirectorio('c:\\Users\\bustoped\\Downloads\\Comics\\')
    #    config.addTipo('cbz')
    cursor = config.conexion.cursor()

    #    config.delTipo('cb7')
    #    config.delDirectorio('home')

    for dire in config.listaClaves:
      print(dire)
#    config.addTipo('cb7')


