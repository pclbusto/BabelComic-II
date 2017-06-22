import codecs
import xml.etree.ElementTree as ET
import sqlite3
from Entidades.Series import Serie
from Extras import  Config
#importamos ComicVineSearcher para poder hacer la rutina que cargue datos desde comicvine
from Extras import ComicVineSearcher

class Series:
    def __init__(self):
        self.conexion = sqlite3.connect('BabelComic.db')
        self.conexion.row_factory = sqlite3.Row
        self.status = 1
        self.entityName = "volumes"
    def add(self, serie):
        c = self.conexion.cursor()
        c.execute('''INSERT INTO series (id,nombre,descripcion,image_url,publisherId,AnioInicio,cantidadNumeros)
Values(?,?,?,?,?,?,?)''', (
        serie.id, serie.nombre, serie.descripcion, serie.image_url, serie.publisherId, serie.AnioInicio,
        serie.cantidadNumeros))
        self.conexion.commit()
        file_name = serie.image_url.split('/')[-1]
        file_name_no_ext = (file_name[:-4])
        if os.path.exists(Config().getSerieTempCoverPath() + file_name_no_ext + ".jpg"):
            shutil.copyfile(Config().getSerieTempCoverPath() + file_name_no_ext + ".jpg",
                            Config().getSerieCoverPath() + file_name_no_ext + ".jpg")

    def rm(self, Id):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE From series where id=?''', (Id,))
        self.conexion.commit()

    def rmAll(self):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE From series''')
        self.conexion.commit()

    def get(self, Id):
        cursor = self.conexion.cursor()
        cursor.execute(
            '''SELECT id,nombre,descripcion,image_url,publisherId,AnioInicio,cantidadNumeros,name From series inner join (select id as pbis,name from publishers )as publishers on series.publisherId = publishers.pbis where id=?''',
            (Id,))
        r = cursor.fetchone()
        if (r):
            self.status = 1
            serie = Serie.Serie(r['id'], r['nombre'])
            serie.descripcion = r['descripcion']
            serie.image_url = r['image_url']
            serie.publisherId = r['publisherId']
            serie.publisherName = r['name']
            serie.AnioInicio = r['AnioInicio']
            serie.cantidadNumeros = r['cantidadNumeros']
            return serie
        else:
            self.status = 0
            return None

    def update(self, serie):
        cursor = self.conexion.cursor()
        cursor.execute('''Update series set
nombre=?,descripcion=?,image_url=?,publisherId=?,AnioInicio=?,cantidadNumeros=?
where id=?''', (
        serie.nombre, serie.descripcion, serie.image_url, serie.publisherId, serie.AnioInicio, serie.cantidadNumeros,
        serie.id))
        self.conexion.commit()

    def getSize(self):
        cursor = self.conexion.cursor()
        cursor.execute('''SELECT count * From series''')
        cursor.fetchone()
        return (c.fetchone()[0])

    def loadFromFiles(self):
        cursor = self.conexion.cursor()
        entidad = 'volumes'  # para hacer match con el nombre del archivo
        lista = [x for x in range(0, 76000, 100)]
        for off in lista:
            nombreArchivo = 'consultaComicVine' + entidad + '-' + str(off) + '.xml'
            print('procesando archvo: ' + nombreArchivo)
            ##            fr = open(nombreArchivo, 'r')
            fr = codecs.open(nombreArchivo, 'r', encoding='utf-8', errors='ignore')
            xml = fr.read()
            fr.close()
            root = ET.fromstring(xml)
            results = root.find('results')
            for item in results:
                serie = Serie(item.find('id').text, item.find('name').text)
                serie.cantidadNumeros = int(item.find('count_of_issues').text)
                serie.descripcion = item.find('description').text
                if item.find('image').find('super_url') != None:
                    serie.image_url = item.find('image').find('super_url').text
                else:
                    serie.image_url = ''
                if item.find('publisher').find('id') != None:
                    serie.publisherId = item.find('publisher').find('id').text
                else:
                    serie.publisherId = '-1'
                serie.AnioInicio = item.find('start_year').text
                cursor.execute('''INSERT INTO series (id,nombre,descripcion,image_url,publisherId,AnioInicio,cantidadNumeros)
Values(?,?,?,?,?,?,?)''', (
                serie.id, serie.nombre, serie.descripcion, serie.image_url, serie.publisherId, serie.AnioInicio,
                serie.cantidadNumeros))
            print('procesados: ' + str(off) + ' de ' + str(10000))
            self.conexion.commit()

    def getList(self, valores, filtro=None, orden=None):
        c = self.conexion.cursor()
        if not orden: orden = ''
        if filtro:
            print('''SELECT id,nombre,descripcion,image_url,publisherId,AnioInicio,cantidadNumeros, date_added,name From series left join (select id as pbis,name from publishers )as publishers on series.publisherId = publishers.pbis where ''' + filtro + ' ' + orden)
            c.execute(
                '''SELECT id,nombre,descripcion,image_url,publisherId,AnioInicio,cantidadNumeros, date_added,name From series left join (select id as pbis,name from publishers )as publishers on series.publisherId = publishers.pbis where ''' + filtro + ' ' + orden,
                valores)
        else:
            c.execute(
                '''SELECT id, nombre, descripcion, image_url,publisherId,AnioInicio, cantidadNumeros, date_added,name From series
                left join (select id as pbis,name from publishers )as publishers on series.publisherId = publishers.pbis ''' + ' ' + orden)

        rows = c.fetchall()
        lista = []
        for row in rows:
            serie = Serie.Serie(row['id'], row['nombre'])
            serie.descripcion = row['descripcion']
            serie.image_url = row['image_url']
            serie.publisherId = row['publisherId']
            serie.publisherName = row['name']
            serie.AnioInicio = row['AnioInicio']
            serie.cantidadNumeros = row['cantidadNumeros']
            lista.append(serie)
        print(len(lista))
        return lista

    def getNext(self, campo='id'):
        cursor = self.conexion.cursor()
        return None

    def close(self):
        self.conexion.close()

    def loadDataFromComicVine(self):
        config = Config()
        clave = config.getClave('volumes')
        print(clave)
        comic_searcher = ComicVineSearcher(clave)

        comic_searcher.setEntidad('volumes')
        lista_series = series.getList('')
        #comic_searcher.vineSearch(len(lista_series)+1)
        comic_searcher.vineSearch(67700)
        for serie in comic_searcher.listaBusquedaVine:
            self.add(serie)
        print('porcentaje completado: '+str((100*(len(lista_series)/comic_searcher.cantidadResultados))))

    def searchInComicVine(self, filtro):
        config = Config()
        clave = config.getClave(self.entityName)
        comic_searcher = ComicVineSearcher(clave)
        comic_searcher.setEntidad(self.entityName)
        comic_searcher.addFilter("name:"+filtro.replace(" ","%20"))
        comic_searcher.vineSearch(0)
        self.listaComicVineSearch = comic_searcher.listaBusquedaVine
        # if not os.path.exists(path):
        #     os.makedirs(path)
if __name__ == "__main__":

    series = Series()
    series.searchInComicVine("Green arrow")

    for serie in series.listaComicVineSearch:
        print("nombre: {} editorial: {}".format(serie.nombre, serie.publisherId))
