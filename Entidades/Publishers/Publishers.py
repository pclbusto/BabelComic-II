
from Entidades.Publishers.Publisher import Publisher
from Entidades import Init

import Extras.BabelComicBookManagerConfig as BC
import Extras.ComicVineSearcher as CV
import xml.etree.ElementTree as ET
import shutil
import os
import sqlite3
import codecs


class Publishers:
    def __init__(self):
        self.conexion = sqlite3.connect(BC.BabelComicBookManagerConfig.PATH)
        self.conexion.row_factory = sqlite3.Row
        self.status = 1
        self.listaComicVineSearch = []
        self.currentKeyName='id'
        self.currentKeyValue=''

    def add(self,publisher):
        c=self.conexion.cursor()
        c.execute('''INSERT INTO publishers (id, name, deck, description, logoImagePath)
Values(?,?,?,?,?)''', (publisher.id,publisher.name,publisher.deck,publisher.description,publisher.logoImagePath))
        self.conexion.commit()

        '''copiamos el logo desde el dir temp al de logos. el temp tiene mas logos
        de lo que he guardados'''
        file_name = publisher.logoImagePath.split('/')[-1]
        file_name_no_ext = (file_name[:-4])
        if os.path.exists(BC.BabelComicBookManagerConfig().getPublisherTempLogoPath() + file_name_no_ext + ".jpg"):
            shutil.copyfile(BC.BabelComicBookManagerConfig().getPublisherTempLogoPath() + file_name_no_ext + ".jpg",
                            BC.BabelComicBookManagerConfig().getPublisherLogoPath() + file_name_no_ext + ".jpg")

    def rm(self,Id):
        cursor=self.conexion.cursor()
        cursor.execute('''DELETE From publishers where id=?''', (Id,))
        self.conexion.commit()

    def rmAll(self):
        cursor=self.conexion.cursor()
        cursor.execute('''DELETE From publishers''')
        self.conexion.commit()

    def __loadRowToObject__(self,row):
        Publisher(row['id'], row['name'])
        publisher = Publisher(row['id'], row['name'])
        publisher.descripcion = row['description']
        publisher.deck = row['deck']
        publisher.logoImagePath = row['logoImagePath']
        publisher.siteDetailUrl = row['siteDetailUrl']
        publisher.localLogoImagePath =row['localLogoImagePath']
        return publisher

    def get(self,Id):
        publisher  = Init.Session().query(Publisher).get(Id)
        return publisher


    def update(self,publisher):
        cursor=self.conexion.cursor()
        cursor.execute('''Update publishers set
name=?,description=?,deck=?,logoImagePath=? where id=?''', (publisher.name,publisher.description,publisher.deck, publisher.logoImagePath,publisher.id))
        self.conexion.commit()
    def getSize(self):
        cursor=self.conexion.cursor()
        cursor.execute('''SELECT count * From publishers''')
        return(cursor.fetchone()[0])
    def loadFromFiles(self):
        cursor = self.conexion.cursor()
        entidad = 'publishers'#para hacer match con el nombre del archivo
        lista =[x for x in range(0,76000,100)]
        for off in lista:
            nombreArchivo ='consultaComicVine'+entidad+'-'+str(off)+'.xml'
            print ('procesando archvo: '+nombreArchivo)
##            fr = open(nombreArchivo, 'r')
            fr = codecs.open(nombreArchivo,'r',encoding='utf-8', errors='ignore')
            xml = fr.read()
            fr.close()
            root = ET.fromstring(xml)
            results = root.find('results')
            for item in results:
                publisher = Publisher(item.find('id').text, item.find('name').text)
                publisher.descripcion = item.find('description').text
                publisher.deck = item.find('deck').text
                if item.find('image').find('super_url')!=None:
                    publisher.logoImagePath = item.find('image').find('super_url').text
                else:
                    publisher.logoImagePath = ''
                self.add(publisher)
            print('procesados: '+str(off)+' de '+str(10000))
            self.conexion.commit()
    def getList(self,valores,filtro=None,orden=None):
        c=self.conexion.cursor()
        if not orden: orden=''
        if filtro:
            c.execute('''SELECT id, name, deck, description, logoImagePath From publishers where '''+filtro+' '+orden, valores)
        else:
            c.execute('''SELECT id, name, deck, description, logoImagePath From publishers'''+' '+orden)
        rows=c.fetchall()
        lista=[]
        for row in rows:
            publisher = self.__loadRowToObject__(row)
            lista.append(publisher)
        print(len(lista))
        return lista

    def getNext(self):
        publisher = None
        if self.currentKeyValue == '':
            publisher = self.getLast()
        else:
            last=Init.Session().query(Publisher).get(self.currentKeyValue)
            publisher = Init.Session().query(Publisher).filter(Publisher.id_publisher > self.currentKeyValue).first()
            print(publisher)
            if publisher == None:
                publisher = last
        return publisher

    def getPrev(self):
        publisher = None
        if self.currentKeyValue == '':
            publisher = self.getFirst()
        else:
            first = Init.Session().query(Publisher).get(self.currentKeyValue)
            publisher = Init.Session().query(Publisher).filter(Publisher.id_publisher < self.currentKeyValue).first()
            print(publisher)
            if publisher == None:
                publisher = first
        return publisher

    def getFirst(self):
        publisher = Init.Session().query(Publisher).first()
        if publisher!=None:
            self.currentKeyValue = publisher.id_publisher
            print('cargamos valores'+publisher.__repr__())
        return publisher

    def getLast(self):
        publisher = Init.Session().query(Publisher).order_by(Publisher.id_publisher.desc()).first()
        if publisher!=None:
            self.currentKeyValue = publisher.id_publisher
        return publisher

    def close(self):
        self.conexion.close()

    def searchInComicVine(self, filtro):
        path = "publishers\\temp\\"
        config = BC.BabelComicBookManagerConfig()
        clave = config.getClave('publishers')
        comic_searcher = CV.ComicVineSearcher(clave)
        comic_searcher.setEntidad('publishers')
        comic_searcher.addFilter("name:"+filtro.replace(" ","%20"))
        comic_searcher.vineSearch(0)
        self.listaComicVineSearch = comic_searcher.listaBusquedaVine
        if not os.path.exists(path):
            os.makedirs(path)
        print('porcentaje completado: ' + str((100 * (len(self.listaComicVineSearch) / comic_searcher.cantidadResultados))))


if __name__ == "__main__":
    publishers = Publishers()
    publishers.searchInComicVine("Marvel")
    publishers.rmAll()
    publisher = Publisher('0','Sin Editoriaasa')
    publishers.add(publisher)


    for publisher in publishers.listaComicVineSearch:
        print(publisher.name,publisher.id, publisher.siteDetailUrl)
    publishers.rmAll()
    publishers.close()
