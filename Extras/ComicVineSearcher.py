from datetime import datetime
from Entidades.Publishers import Publisher
from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.ArcosArgumentales.ArcoArgumental import  ArcoArgumental
from Entidades.ArcosArgumentales.ArcosArgumentales import ArcosArgumentales
from Entidades.ArcosArgumentales.ArcosArgumentalesComics import ArcosArgumentalesComics

import Entidades.Volumes.Volume
import urllib.request
import xml.etree.ElementTree as ET
import Entidades.Init


class ComicVineSearcher():
    EntidadesPermitidas = ['issues', 'volumes', 'publishers', 'issue', 'story_arc_credits']
    def __init__(self, vinekey):

        self.vinekey = vinekey
        self.filter = ''  # el usuario deberia pasar nombreCampo:<valor>,...,nombreCampo:<valor> el nombre del campo depende de la entidad
        self.entidad = ''
        self.listaBusquedaVine = []
        self.listaBusquedaLocal = []
        self.columnas = []
        self.statusMessage = 'Ok'
        # es el techo de cantidad resultados dividido 100
        self.cantidadPaginas = 0
        # valor entre 0 y cantidadPaginas
        self.paginaActual = 0
        self.cantidadResultados = 0
        self.offset = 0
        # Cantidad de resultados que retorno la ultima consulta
        self.numberPageResults = 0
        self.numberTotalResults = 0
        # Cantidad de resultados por pagina no puede ser mayor a 100
        self.limit = 100
        ##1:OK
        ##100:Invalid API Key
        ##101:Object Not Found
        ##102:Error in URL Format
        ##103:'jsonp' format requires a 'json_callback' argument
        ##104:Filter Error
        ##105:Subscriber only video is for subscribers only
        self.statusCode = 1

    def localSearch(self, filtro, columnasBuscar=(1), columnasMostrar=(0, 1, 2, 3, 4, 5, 6, 7)):
        del self.listaBusquedaLocal[:]
        self.columnas = columnasMostrar
        self.listaBusquedaLocal = [item for item in self.listaBusquedaVine if (item[1].find(filtro) != -1)]

    def print(self):

        for item in self.listaBusquedaLocal:
            print([item[x] for x in self.columnas])
            ##                item[7],'---',item[1],'---', item[3])

    def clearFilter(self):
        self.filter=""
        self.listaBusquedaVine.clear()

    def setEntidad(self, entidad):

        if entidad in ComicVineSearcher.EntidadesPermitidas:
            self.entidad = entidad
            self.filter = ''
            del self.listaBusquedaVine[:]
        else:
            print('la entidad:' + entidad + ' es invalida.')

    def addFilter(self, filtro):
        if len(self.filter) == 0:
            self.filter = '&filter=' + filtro
        else:
            self.filter = self.filter + ',' + filtro
            ##        print('http://www.comicvine.com/api/'+self.entidad+'/?api_key='+self.vinekey+self.filter+'&offset='+str(0)+'&sort=id:asc')

    def getVineEntity(self, id):
        # TODO: Este metodo debe incrementar el contador de consulta para la clave. asi no sobrecargamos
        if (self.entidad == 'issue'):
            print('http://comicvine.gamespot.com/api/issue/4000-' + str(id) + '/?api_key=' + self.vinekey)
            response = urllib.request.urlopen(
                'http://comicvine.gamespot.com/api/issue/4000-' + str(id) + '/?api_key=' + self.vinekey)
        elif (self.entidad == 'story_arc_credits'):
            print('http://comicvine.gamespot.com/api/story_arc/4045-' + str(id) + '/?api_key=' + self.vinekey)
            response = urllib.request.urlopen(
                'http://comicvine.gamespot.com/api/story_arc/4045-' + str(id) + '/?api_key=' + self.vinekey)

        else:
            print("entidad invalidad: " + self.entidad)
            return
        # si estamos aca entoces la consulta se ralizao porque la entidad estaba OK.
        html = response.read()
        xml = html.decode()
        print(xml)
        root = ET.fromstring(xml)
        self.statusCode = int(root.find('status_code').text)
        if self.statusCode == 1:
            if (self.entidad == 'issue'):
                # dummy comic me interesa el resto de los campos que los sacamos de la consulta a comic vine
                comic = ComicBook()
                comic.path = 'path'
                issue = root.find('results')
                if issue.find('name').text is not None:
                    comic.titulo = issue.find('name').text
                else:
                    comic.titulo =''
                comic.numero = issue.find('issue_number').text
                comic.fechaTapa = datetime.strptime(issue.find('cover_date').text,"%Y-%m-%d").timestamp()
                comic.serieId = issue.find('volume').find('id').text
                comic.volumeId = issue.find('volume').find('id').text
                comic.volumeName = issue.find('volume').find('name').text
                comic.idExterno = int(issue.find('id').text)
                if issue.find('description').text is not None:
                    comic.resumen = issue.find('description').text
                else:
                    comic.resumen = ''
                comic.ratingExterno=0
                comic.rating=0
                comic.nota=""
                comic.arcoArgumentalId = ''
                comic.arcoArgumentalNumero = 0
                if (issue.find('story_arc_credits') != None):
                    # vamos a verificar si existe el arco si no existe lo damos de alta
                    # al dar de alta el arco tenemos que recuperar el numero u orden dentro del arco.
                    print('buscamos arco')
                    session = Entidades.Init.Session()
                    for item in issue.find('story_arc_credits').findall('story_arc'):
                        idArco = int(item.find('id').text)
                        # .find('story_arc_credits').find('story_arc')
                        print('ARCOOOOOOO: ' + str(idArco))
                        arco = session.query(ArcoArgumental).get(idArco)
                        if arco:
                            print('el arco existe. obtenemos el numero del comic')
                            numeroDentroArco = arco.getIssueOrder(comic.idExterno)
                            print('Arco y numero:', arco.id, str(numeroDentroArco))
                        else:
                            print('el arco  NO EXISTEexiste. Cargamos el arco y luego obtenemos el numero del comic')
                            self.entidad = 'story_arc_credits'
                            arco = self.getVineEntity(idArco)
                            session.add(arco)
                            session.commit()
                            numeroDentroArco = arco.getIssueOrder(comic.idExterno)

                        print(arco.id)
                        print(numeroDentroArco)
                        comic.arcoArgumentalId = arco.id
                        comic.arcoArgumentalNumero = numeroDentroArco

                return comic

            if (self.entidad == 'story_arc_credits'):
                story_arc = root.find('results')
                arco = ArcoArgumental()
                arco.id = story_arc.find('id').text
                arco.nombre = story_arc.find('name').text
                arco.deck = story_arc.find('deck').text
                arco.descripcion = story_arc.find('description').text
                arco.ultimaFechaActualizacion = datetime.today().toordinal()
                issues = story_arc.find('issues')
                pos = 1
                session = Entidades.Init.Session()
                session.add(arco)
                session.commit()
                session.query(ArcosArgumentalesComics).filter(ArcosArgumentalesComics.idArco == arco.id).delete()
                session.commit()
                for issue in issues:
                    arcoComic = ArcosArgumentalesComics()
                    arcoComic.idArco = arco.id
                    arcoComic.idComic = issue.find('id').text
                    arcoComic.orden = pos
                    session.add(arcoComic)
                    pos += 1
                session.commit()
                return arco
            else:
                print('Entidad %1 sin implementar', self.entidad)

        elif self.statusCode == 100:
            self.statusMessage = 'revisar'
        elif self.statusCode == 101:
            self.statusMessage = 'Invalid API Key'
        elif self.statusCode == 102:
            self.statusMessage = 'Object Not Found'
        elif self.statusCode == 103:
            self.statusMessage = 'Error in URL Format'
        elif self.statusCode == 104:
            self.statusMessage = 'Filter Error'
        elif self.statusCode == 105:
            self.statusMessage = 'Subscriber only video is for subscribers only'

    def vineSearch(self, io_offset=0):
        if self.entidad == '':
            self.statusMessage = ('falta ingresar la entidad')
            ##            print('falta ingresar la entidad')
            return
        self.offset = io_offset
        print(
            'http://www.comicvine.com/api/' + self.entidad + '/?api_key=' + self.vinekey + self.filter + '&offset=' + str(
                self.offset) + '&sort=date_added:asc')
        response = urllib.request.urlopen(
            'http://www.comicvine.com/api/' + self.entidad + '/?api_key=' + self.vinekey + self.filter + '&offset=' + str(
                self.offset) + '&sort=id:asc')

        #response = urllib.request.urlopen('http://comicvine.gamespot.com/api/publishers/?api_key=64f7e65686c40cc016b8b8e499f46d6657d26752&filter=name:DC%20comics&offset=0&sort=date_added:asc')



        html = response.read()
        # print(html.decode())
        xml = html.decode()
        #xml = xml[:130640]+xml[130642:]

        parser = ET.XMLParser(encoding="utf-8")
        root = ET.fromstring(xml, parser= parser)
        self.statusCode = int(root.find('status_code').text)
        if self.statusCode == 1:
            #esto puede ser el limite de resultados por pag o menos que esto cuando es l ultima pagina
            number_of_page_results = int(root.find('number_of_page_results').text)
            # cantidad total de registros este valor dividido por limite no da la cantidad de consultas necesarias para
            # recuperar todos los datos de la consulta
            self.cantidadResultados = int(root.find('number_of_total_results').text)
            self.cantidadPaginas = self.cantidadResultados / self.limit
            status_code = root.find('status_code').text
            results = root.find('results')
            if (self.entidad == 'issues'):
                for item in results:
                    fecha = item.find('cover_date').text
                    titulo = item.find('name').text
                    descripcion = item.find('description').text
                    idExterno = item.find('id').text
                    numero = item.find('issue_number').text
                    api_detail_url = item.find('api_detail_url').text
                    thumb_url = item.find('image').find('thumb_url').text
                    volumeName = item.find('volume').find('name').text
                    volumeId = item.find('volume').find('id').text
                    print(volumeName, volumeId)
                    self.listaBusquedaVine.append(
                        {'fecha': fecha, 'titulo': titulo, 'descripcion': descripcion, 'idExterno': idExterno,
                         'numero': numero, 'api_detail_url': api_detail_url, 'thumb_url': thumb_url,
                         'volumeName': volumeName, 'volumeId': volumeId})

            elif self.entidad == 'volumes':
                for item in results:
                    l_serie = Volume(id = item.find('id').text, nombre = item.find('name').text)

                    l_serie.descripcion = item.find('description').text
                    l_serie.cantidadNumeros = item.find('count_of_issues').text
                    if item.find('image').find('thumb_url') != None:
                        l_serie.image_url = item.find('image').find('thumb_url').text
                    else:
                        l_serie.image_url = ''

                    if item.find('publisher').find('id')!= None:
                        l_serie.publisherId = item.find('publisher').find('id').text
                    else:
                        l_serie.publisherId = "-1"
                    l_serie.AnioInicio = item.find('start_year').text
                    self.listaBusquedaVine.append(l_serie)

                    # self.listaBusquedaVine.append({'count_of_issues': count_of_issues,
                    #                                'description': description,
                    #                                'Id': Id,
                    #                                'image': image,
                    #                                'name': name,
                    #                                'publisher': publisher,
                    #                                'start_year': start_year})

            elif self.entidad == 'publishers':
                # print("publisher")


                for item in results:
                    # help(item)
                    # print(item.tostring())
                    publisher = Publisher.Publisher()
                    publisher.id_publisher = item.find('id').text
                    publisher.name  = item.find('name').text
                    publisher.descripcion = item.find('description').text
                    publisher.deck = item.find('deck').text
                    if item.find('image').find('super_url') != None:
                        publisher.logoImagePath = item.find('image').find('super_url').text
                    else:
                        publisher.logoImagePath = ''
                    publisher.siteDetailUrl = item.find('site_detail_url').text
                    self.listaBusquedaVine.append(publisher)
            self.statusMessage = 'Recuperados: ' + str(self.offset) + ' de ' + str(self.cantidadResultados)

        elif self.statusCode == 100:
            self.statusMessage = 'revisar'
        elif self.statusCode == 101:
            self.statusMessage = 'Invalid API Key'
        elif self.statusCode == 102:
            self.statusMessage = 'Object Not Found'
        elif self.statusCode == 103:
            self.statusMessage = 'Error in URL Format'
        elif self.statusCode == 104:
            self.statusMessage = 'Filter Error'
        elif self.statusCode == 105:
            self.statusMessage = 'Subscriber only video is for subscribers only'

            # print('Recuperados: '+str(loffset)+' de '+number_of_total_results)


if __name__ == '__main__':
    cv = ComicVineSearcher('7e4368b71c5a66d710a62e996a660024f6a868d4')
    ##    cv = comicVineSearcher('64f7e65686c40cc016b8b8e499f46d6657d26752')
    cv.setEntidad('volumes')
    #arco = cv.getVineEntity(55691)
    #print(arco.comics)
##    cv.addFilter('')
    cv.vineSearch()
    print(cv.statusMessage)
    cv.print()
    for serie in cv.listaBusquedaVine:
        print(serie.nombre)
# for offset in range(2300,5900,100):
##    for offset in range(0, 5900, 100):
##        cv.vineSearch(offset)
##        print(cv.statusMessage)
##    for item in cv.listaBusquedaVine :
##        print(item['name'],item['count_of_issues'],item['image'])
##    cv.addfilter('name:Green Lantern')


# 67700 tuvo problemas


##pclbusto
##vinekey = '7e4368b71c5a66d710a62e996a660024f6a868d4'
##pclbusto2
##vinekey = '64f7e65686c40cc016b8b8e499f46d6657d26752'
