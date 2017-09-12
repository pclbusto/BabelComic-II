from datetime import datetime
from Entidades.Publishers import Publisher
from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.ArcosArgumentales.ArcoArgumental import ArcoArgumental
from Entidades.ArcosArgumentales.ArcosArgumentalesComics import ArcosArgumentalesComics

import Entidades.Volumes.Volume
import urllib.request
import xml.etree.ElementTree as ET

import Entidades.Init
from Entidades.Volumes.ComicsInVolume import ComicInVolumes


class ComicVineSearcher:
    EntidadesPermitidas = ['issues', 'volumes', 'publishers', 'issue', 'story_arc_credits', 'volume']

    def __init__(self, vinekey, session):
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

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

    def localSearch(self, filtro, columnasBuscar=1, columnasMostrar=(0, 1, 2, 3, 4, 5, 6, 7)):
        del self.listaBusquedaLocal[:]
        self.columnas = columnasMostrar
        self.listaBusquedaLocal = [item for item in self.listaBusquedaVine if (item[1].find(filtro) != -1)]

    def print(self):

        for item in self.listaBusquedaLocal:
            print([item[x] for x in self.columnas])
            ##                item[7],'---',item[1],'---', item[3])

    def clearFilter(self):
        self.filter = ""
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
        if self.entidad == 'issue':
            print('http://comicvine.gamespot.com/api/issue/4000-' + str(id) + '/?api_key=' + self.vinekey)
            response = urllib.request.urlopen(
                'http://comicvine.gamespot.com/api/issue/4000-' + str(id) + '/?api_key=' + self.vinekey)
        elif self.entidad == 'story_arc_credits':
            print('http://comicvine.gamespot.com/api/story_arc/4045-' + str(id) + '/?api_key=' + self.vinekey)
            response = urllib.request.urlopen(
                'http://comicvine.gamespot.com/api/story_arc/4045-' + str(id) + '/?api_key=' + self.vinekey)
        elif self.entidad == 'volume':
            print('http://comicvine.gamespot.com/api/volume/4050-' + str(id) + '/?api_key=' + self.vinekey)
            response = urllib.request.urlopen(
                'http://comicvine.gamespot.com/api/volume/4050-' + str(id) + '/?api_key=' + self.vinekey)

        else:
            print("entidad invalidad: " + self.entidad)
            return
        # si estamos aca entoces la consulta se ralizao porque la entidad estaba OK.
        html = response.read()
        xml = html.decode()
        # root = ET.parse('e:\\descarga.xml')
        print(xml)
        root = ET.fromstring(xml)
        self.statusCode = int(root.find('status_code').text)
        if self.statusCode == 1:
            if self.entidad == 'issue':
                # dummy comic me interesa el resto de los campos que los sacamos de la consulta a comic vine
                comic = ComicBook()
                comic.path = 'path'
                issue = root.find('results')
                if issue.find('name').text is not None:
                    comic.titulo = issue.find('name').text
                else:
                    comic.titulo = ''
                comic.numero = issue.find('issue_number').text
                print("Fecha: " + issue.find('cover_date').text)
                comic.fechaTapa = datetime.strptime(issue.find('cover_date').text, "%Y-%m-%d").date().toordinal()
                comic.serieId = issue.find('volume').find('id').text
                comic.volumeId = issue.find('volume').find('id').text
                comic.volumeName = issue.find('volume').find('name').text
                comic.comicVineId = int(issue.find('id').text)
                if issue.find('description').text is not None:
                    comic.resumen = issue.find('description').text
                else:
                    comic.resumen = ''
                comic.ratingExterno = 0
                comic.rating = 0
                comic.nota = ""
                comic.arcoArgumentalId = '0'
                comic.arcoArgumentalNumero = 0
                if issue.find('story_arc_credits') != None:
                    # vamos a verificar si existe el arco si no existe lo damos de alta
                    # al dar de alta el arco tenemos que recuperar el numero u orden dentro del arco.
                    print('buscamos arco')

                    for item in issue.find('story_arc_credits').findall('story_arc'):
                        idArco = int(item.find('id').text)
                        # .find('story_arc_credits').find('story_arc')
                        print('ARCOOOOOOO: ' + str(idArco))
                        arco = self.session.query(ArcoArgumental).get(idArco)
                        if arco is not None:
                            print('el arco existe. obtenemos el numero del comic')
                            numeroDentroArco = arco.getIssueOrder(comic.comicVineId)
                            print('Arco y numero:', arco.id, str(numeroDentroArco))
                        else:
                            print('el arco  NO EXISTEexiste. Cargamos el arco y luego obtenemos el numero del comic')
                            self.entidad = 'story_arc_credits'
                            arco = self.getVineEntity(idArco)
                            self.session.add(arco)
                            self.session.commit()
                            numeroDentroArco = arco.getIssueOrder(comic.comicVineId)

                        print(arco.id)
                        print(numeroDentroArco)
                        comic.arcoArgumentalId = arco.id
                        comic.arcoArgumentalNumero = numeroDentroArco

                return comic

            if self.entidad == 'story_arc_credits':
                story_arc = root.find('results')
                arco = ArcoArgumental()
                arco.id = story_arc.find('id').text
                arco.nombre = story_arc.find('name').text
                arco.deck = story_arc.find('deck').text
                arco.descripcion = story_arc.find('description').text
                arco.ultimaFechaActualizacion = datetime.today().toordinal()
                issues = story_arc.find('issues')
                pos = 1
                self.session.add(arco)
                self.session.commit()
                self.session.query(ArcosArgumentalesComics).filter(ArcosArgumentalesComics.idArco == arco.id).delete()
                self.session.commit()
                for issue in issues:
                    arcoComic = ArcosArgumentalesComics()
                    arcoComic.idArco = arco.id
                    arcoComic.idComic = issue.find('id').text
                    arcoComic.orden = pos
                    self.session.add(arcoComic)
                    pos += 1
                self.session.commit()
                return arco

            if self.entidad == 'volume':
                volumeVine = root.find('results')
                volume = Entidades.Volumes.Volume.Volume()
                volume.id = volumeVine.find('id').text
                volume.nombre = volumeVine.find('name').text
                volume.deck = volumeVine.find('deck').text
                volume.AnioInicio =volumeVine.find('start_year').text
                volume.descripcion = volumeVine.find('description').text
                volume.cantidadNumeros = volumeVine.find('count_of_issues').text
                if volumeVine.find('image').find('super_url') is not None:
                    volume.image_url = volumeVine.find('image').find('super_url').text
                if volumeVine.find('publisher').find('id') is not None:
                    print("Recuperando Editorial")
                    volume.publisherId = volumeVine.find('publisher').find('id').text
                    volume.publisher_name = volumeVine.find('publisher').find('name').text
                if volumeVine.find('issues'):
                    '''
                    La cantidad de numeros esta mal en el xml al menos para linterna verde vol2 
                    estaba mal. Por esto se decide contar los issues
                    '''
                    volume.cantidadNumeros = len(volumeVine.find('issues').findall('issue'))
                    '''se cargan los issues que trae el xml. no toda la info solo los numeros.
                    esto se usa para poder calcular los offset correctos en la busqueda de issues
                    '''
                    print("ACA ESTAMOS")
                    comicIds = []
                    for index, issue in enumerate(volumeVine.find('issues').findall('issue')):
                        comicInVolumes = ComicInVolumes()
                        comicInVolumes.volumeId = volume.id
                        comicInVolumes.comicVineId = issue.find("id").text
                        comicInVolumes.numero = issue.find("issue_number").text
                        comicInVolumes.titulo = issue.find("name").text

                        comicIds.append(comicInVolumes)

                return volume, comicIds
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

    def vineSearchMore(self):
        return self.vineSearch(self.offset + self.limit)

    def vineSearch(self, io_offset=0):
        if self.entidad == '':
            self.statusMessage = 'falta ingresar la entidad'
            ##            print('falta ingresar la entidad')
            return
        self.offset = io_offset

        url = 'http://www.comicvine.com/api/' + self.entidad + '/?api_key=' + self.vinekey + self.filter + '&offset=' + str(
                    self.offset)
        print("Clave: {}\noffset:{}\nurl:{}".format(self.vinekey, self.offset,url))
        response = urllib.request.urlopen(url)
        '''
        if self.entidad == 'issues':
            response = urllib.request.urlopen(
                'http://www.comicvine.com/api/' + self.entidad + '/?api_key=' + self.vinekey + self.filter + '&offset=' + str(
                    self.offset * 100) + '&sort=cover_date:asc')
            print(
                'http://www.comicvine.com/api/' + self.entidad + '/?api_key=' + self.vinekey + self.filter + '&offset=' + str(
                    self.offset * 100) + '&sort=cover_date:asc')
        else:
            response = urllib.request.urlopen(
                'http://www.comicvine.com/api/' + self.entidad + '/?api_key=' + self.vinekey + self.filter + '&offset=' + str(
                    self.offset ) + '&sort=id:asc')
            print(
                'http://www.comicvine.com/api/' + self.entidad + '/?api_key=' + self.vinekey + self.filter + '&offset=' + str(
                    self.offset * 100) + '&sort=id:asc')

        # response = urllib.request.urlopen('http://comicvine.gamespot.com/api/publishers/?api_key=64f7e65686c40cc016b8b8e499f46d6657d26752&filter=name:DC%20comics&offset=0&sort=date_added:asc')

        '''

        html = response.read()
        # print(html.decode())
        xml = html.decode()
        # xml = xml[:130640]+xml[130642:]

        parser = ET.XMLParser(encoding="utf-8")
        root = ET.fromstring(xml, parser=parser)
        self.statusCode = int(root.find('status_code').text)
        if self.statusCode == 1:
            # esto puede ser el limite de resultados por pag o menos que esto cuando es l ultima pagina
            number_of_page_results = int(root.find('number_of_page_results').text)
            # cantidad total de registros este valor dividido por limite no da la cantidad de consultas necesarias para
            # recuperar todos los datos de la consulta
            self.cantidadResultados = int(root.find('number_of_total_results').text)
            self.cantidadPaginas = self.cantidadResultados / self.limit
            status_code = root.find('status_code').text
            results = root.find('results')
            if self.entidad == 'issues':
                for item in results:
                    comic = ComicBook()
                    comic.fechaTapa = item.find('cover_date').text
                    # fecha = item.find('cover_date').text
                    comic.titulo = item.find('name').text
                    # titulo = item.find('name').text
                    comic.resumen = item.find('description').text
                    # descripcion = item.find('description').text
                    comic.comicVineId = item.find('id').text
                    # idExterno = item.find('id').text
                    comic.numero = int(item.find('issue_number').text)
                    # numero = item.find('issue_number').text
                    comic.api_detail_url = item.find('api_detail_url').text
                    # api_detail_url = item.find('api_detail_url').text
                    comic.thumb_url = item.find('image').find('small_url').text
                    # thumb_url = item.find('image').find('small_url').text
                    comic.volumeNombre = item.find('volume').find('name').text
                    # volumeName = item.find('volume').find('name').text
                    comic.volumeId = item.find('volume').find('id').text
                    # volumeId = item.find('volume').find('id').text
                    print(comic)
                    self.listaBusquedaVine.append(
                        comic)


            elif self.entidad == 'volumes':
                for item in results:
                    l_serie = Entidades.Volumes.Volume.Volume(id=item.find('id').text, nombre=item.find('name').text)

                    l_serie.descripcion = item.find('description').text
                    l_serie.cantidadNumeros = item.find('count_of_issues').text
                    if item.find('image').find('thumb_url') != None:
                        l_serie.image_url = item.find('image').find('super_url').text
                    else:
                        l_serie.image_url = ''

                    if item.find('publisher').find('id') != None:
                        l_serie.publisherId = item.find('publisher').find('id').text
                        l_serie.publisher_name = item.find('publisher').find('name').text
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
                    publisher.name = item.find('name').text
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
    cv.setEntidad('volume')
    volumen = cv.getVineEntity('2839')
    print(volumen)
    # arco = cv.getVineEntity(55691)
    # print(arco.comics)
##    cv.addFilter('')
# cv.vineSearch()
# print(cv.statusMessage)
# cv.print()
# for serie in cv.listaBusquedaVine:
#     print(serie.nombre)
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
