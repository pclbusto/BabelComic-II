from datetime import datetime
from Servicios_Externos.Comic_vine.comic_vine_info_issue_searcher import Comic_Vine_Info_Searcher
from Entidades.Agrupado_Entidades import Comicbook, Comicbook_Info, Publisher, Arco_Argumental
from Entidades.Agrupado_Entidades import Arcos_Argumentales_Comics_Reference, Volume, Comics_In_Volume
from Entidades.Entitiy_managers import Comicbooks_Info
import urllib.request
import xml.etree.ElementTree as ET

import Entidades.Init

import math
import threading
# from multiprocessing import Process
import time
import random


class ComicVineSearcher:
    # todo hacer mas robusta la busqueda y tratar de tener toda la logica de la ventana en esta clase para poder
    # se mas senccillo el cambio de gui

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
        self.lista_comicbooks_info = []
        self.lista_arco_argumental_comic_reference = []
        self.lock = threading.Lock()
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
        self.lista_hilos_ejecucion = {}
        self.detener = False
        self.actualizar_solo_numeros_nuevos = True
        self.comicbooks_info_manager = Comicbooks_Info(self.session)
        ##1:OK
        ##100:Invalid API Key
        ##101:Object Not Found
        ##102:Error in URL Format
        ##103:'jsonp' format requires a 'json_callback' argument
        ##104:Filter Error
        ##105:Subscriber only video is for subscribers only
        self.statusCode = 1
        self.porcentaje_procesado = 0

    def localSearch(self, filtro, columnasBuscar=1, columnasMostrar=(0, 1, 2, 3, 4, 5, 6, 7)):
        del self.listaBusquedaLocal[:]
        self.columnas = columnasMostrar
        self.listaBusquedaLocal = [item for item in self.listaBusquedaVine if (item[1].find(filtro) != -1)]

    def print(self):

        for item in self.listaBusquedaLocal:
            print([item[x] for x in self.columnas])
            ##                item[7],'---',item[1],'---', item[3])

    def insert_update_volumen(self, volumen):
        volumen_in_db = self.session.query(Volume).filter(Volume.id_volume == volumen.id_volume).first()
        if volumen_in_db is not None:
            # actualizo la cantidad de ejemplares nada mas
            print(volumen)
            volumen_in_db.actualizar_con(volumen)
            volumen = volumen_in_db
        self.session.add(volumen)
        self.session.commit()
        for comicbook_info in self.lista_comicbooks_info:
            cbi_db = self.session.query(Entidades.Agrupado_Entidades.Comicbook_Info).get(
                comicbook_info.id_comicbook_info)
            if cbi_db is not None and not cbi_db.actualizado_externamente:
                self.session.query(Comicbook_Info).filter(
                    Comicbook_Info.id_comicbook_info == comicbook_info.id_comicbook_info).delete()
                self.session.commit()
                self.session.add(comicbook_info)
            elif cbi_db is not None and cbi_db.actualizado_externamente:
                print("Actualizando info de comicbook_info DATOS A ACTUALIZAR")
                cbi_db.numero = comicbook_info.numero
                cbi_db.fecha_tapa = comicbook_info.fecha_tapa
                cbi_db.orden = comicbook_info.orden
                cbi_db.url = comicbook_info.url
                cbi_db.api_detail_url = comicbook_info.api_detail_url

                for url_cover in comicbook_info.thumbs_url:
                    copiar_cover = True;
                    for url_cover_cbi in cbi_db.thumbs_url:
                        if url_cover.thumb_url == url_cover_cbi.thumb_url:
                            copiar_cover = False
                            break;

                    if copiar_cover:
                        cbi_db.thumbs_url.append(url_cover)

                    # cbi_db.thumbs_url = comicbook_info.thumbs_url
                print(cbi_db)
            else:
                print("agregando comic por primera vez")
                print(cbi_db)
                self.session.add(comicbook_info)
            self.session.commit()
        lista_arcos = []
        for arco in self.lista_arcos:
            arco_db = self.session.query(Arco_Argumental).filter(
                Arco_Argumental.id_arco_argumental == arco.id_arco_argumental).first()
            if arco_db is not None:
                lista_arcos.append(arco_db)
                arco_db.lista_ids_comicbook_info_para_procesar = arco.lista_ids_comicbook_info_para_procesar
            else:
                self.session.add(arco)
                lista_arcos.append(arco)
        self.session.commit()
        # reemplazo todos los arcos por los que estan la base o los que acabo de guardar
        self.lista_arcos = lista_arcos
        # construimos la relacion para cada arco con la lista de comics.
        for arco in self.lista_arcos:
            try:
                print("Lista de arcos de cv {}".format(arco.lista_ids_comicbook_info_para_procesar))
            except Exception:
                print("Arco con error {}".format(arco))
                raise
            for comicbook_info in self.lista_comicbooks_info:
                for pos, arco_comicbook_info in enumerate(arco.lista_ids_comicbook_info_para_procesar):
                    # print("Comic Info {} tipo {} comic info arco {} tipo {}".format(comicbook_info.id_comicbook_info,
                    #                                                                 type(comicbook_info.id_comicbook_info),
                    #                                                                 arco_comicbook_info,
                    #                                                                 type(arco_comicbook_info)))
                    if int(comicbook_info.id_comicbook_info) == arco_comicbook_info:
                        comicbook_info_db = self.session.query(Comicbook_Info).get(comicbook_info.id_comicbook_info)
                        rel = self.session.query(Arcos_Argumentales_Comics_Reference).get(
                            (comicbook_info.id_comicbook_info, arco.id_arco_argumental))
                        if rel is None:
                            print("El comic book_info {} pertenece al arco {}".format(comicbook_info.id_comicbook_info,
                                                                                      arco.id_arco_argumental))
                            arco_argumental_comicsbook_reference = Arcos_Argumentales_Comics_Reference()
                            arco_argumental_comicsbook_reference.orden = pos
                            arco_argumental_comicsbook_reference.ids_arco_argumental = arco
                            print("COMIC A RELACIONAR")
                            print(type(comicbook_info))
                            print(type(comicbook_info_db))
                            if comicbook_info_db is not None:
                                arco_argumental_comicsbook_reference.ids_comicbooks_info = comicbook_info_db
                            else:
                                arco_argumental_comicsbook_reference.ids_comicbooks_info = comicbook_info
                            self.session.add(arco_argumental_comicsbook_reference)
                            self.session.commit()

        # Descargamos los covers de los issues del volumen
        for comicbook_info in self.lista_comicbooks_info:
            print('Bajando covers {}'.format(comicbook_info.id_comicbook_info))
            # comicbook_info.get_first_cover_complete_path()
            comicbooks_info_manager = Comicbooks_Info(session=self.session)
            comicbooks_info_manager.get(comicbook_info.id_comicbook_info)
            print(comicbooks_info_manager.get)
            threading.Thread(target=comicbooks_info_manager.get_first_cover_complete_path).start()


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
        print("FILTRO: {}".format(filtro))
        if len(self.filter) == 0:
            self.filter = '&filter=' + filtro
        else:
            self.filter = self.filter + ',' + filtro
            ##        print('http://www.comicvine.com/api/'+self.entidad+'/?api_key='+self.vinekey+self.filter+'&offset='+str(0)+'&sort=id:asc')

    def getVineEntity(self, id):

        print("Vamos a porcesoar el arco {}".format(id))
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
        # print(xml)
        root = ET.fromstring(xml)
        self.statusCode = int(root.find('status_code').text)
        if self.statusCode == 1:
            if self.entidad == 'story_arc_credits':
                story_arc = root.find('results')
                arco = Arco_Argumental()
                arco.id_arco_argumental = id
                arco.nombre = story_arc.find('name').text
                arco.deck = story_arc.find('deck').text
                arco.descripcion = story_arc.find('description').text
                arco.ultimaFechaActualizacion = datetime.today().toordinal()
                arco.lista_ids_comicbook_info_para_procesar.clear()
                urls_issues = story_arc.find('site_detail_url').text
                issues = story_arc.find('issues')
                '''hay que cargar de nuevo los numeros dentro del arco'''
                pos = 1
                comics_searcher = Comic_Vine_Info_Searcher(self.session)
                print("procesando arco: {}".format(arco.id_arco_argumental))
                arco.lista_ids_comicbook_info_para_procesar = comics_searcher.search_issues_in_arc(
                    urls_issues + "issues/")
                arco.cantidad_comicbooks = len(arco.lista_ids_comicbook_info_para_procesar)
                print("lista issues {}".format(arco.lista_ids_comicbook_info_para_procesar))
                return arco

            if self.entidad == 'volume':
                # todo al cargar un volumen verificar si existe el id externo de no existir cargo uno nuevo de existir
                # actualizar los datos.

                volumeVine = root.find('results')
                # creamos un volumen para almacenar la info recuperada del servicio web
                volume = Entidades.Agrupado_Entidades.Volume()
                volume.id_volume = volumeVine.find('id').text
                volume.nombre = volumeVine.find('name').text
                volume.deck = volumeVine.find('deck').text
                if volume.deck is None:
                    volume.deck = ''
                volume.anio_inicio = volumeVine.find('start_year').text
                volume.descripcion = volumeVine.find('description').text
                volume.cantidad_numeros = volumeVine.find('count_of_issues').text
                volume.url = volumeVine.find('site_detail_url').text
                if volumeVine.find('image').find('super_url') is not None:
                    volume.image_url = volumeVine.find('image').find('super_url').text
                if volumeVine.find('publisher').find('id') is not None:
                    print("Recuperando Editorial")
                    volume.id_publisher = volumeVine.find('publisher').find('id').text
                    volume.publisher_name = volumeVine.find('publisher').find('name').text
                if volumeVine.find('issues'):
                    '''
                    La cantidad de numeros esta mal en el xml al menos para linterna verde vol2 
                    estaba mal. Por esto se decide contar los issues
                    '''
                    volume.cantidad_numeros = len(volumeVine.find('issues').findall('issue'))
                    '''se cargan los issues que trae el xml. no toda la info solo los numeros.
                    esto se usa para poder calcular los offset correctos en la busqueda de issues
                    '''
                    print("cargamos issues del volumen")
                    self.comicIds = []
                    for index, issue in enumerate(volumeVine.find('issues').findall('issue')):
                        comicInVolumes = Comics_In_Volume()
                        comicInVolumes.id_volume = volume.id_volume
                        comicInVolumes.id_comicbook_info = issue.find("id").text
                        comicInVolumes.numero = issue.find("issue_number").text
                        comicInVolumes.titulo = issue.find("name").text
                        comicInVolumes.site_detail_url = issue.find("site_detail_url").text
                        self.comicIds.append(comicInVolumes)

                    #     cargamos la info de los comics los arcos que hagan falta este proceso es largo pero
                    # solo debería tardar la primera vezç
                    return volume
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

    def hilo_procesar_comic_in_volume(self, comic_in_volume, volumen, index):
        print("Ejecutando {}".format(comic_in_volume))
        comics_searcher = Comic_Vine_Info_Searcher(self.session)
        comicbook_info = comics_searcher.search_issue(comic_in_volume.site_detail_url)
        comicbook_info.id_comicbook_info = comic_in_volume.id_comicbook_info
        comicbook_info.id_volume = volumen.id_volume
        comicbook_info.nombre_volumen = volumen.nombre
        self.lista_comicbooks_info.append(comicbook_info)
        print('Lista Comics {}'.format(self.lista_comicbooks_info))
        self.lock.acquire(True)
        self.cantidad_hilos -= 1
        del self.lista_hilos_ejecucion[index]
        self.lock.release()

    def hilo_procesar_arco(self, id_arco):
        # arco = self.session.query(Arco_Argumental).filter(Arco_Argumental.id_arco_argumental == id_arco).first()
        # if arco is None:
        self.entidad = 'story_arc_credits'
        arco = self.getVineEntity(id_arco)
        self.lista_arcos.append(arco)
        self.lock.acquire(True)
        self.cantidad_hilos -= 1
        self.lock.release()

    def hilo_cargar_comicbook_info(self, volumen):

        index = 0
        self.cantidad_hilos = 0
        cantidad_elementos = len(self.comicIds)
        while index < cantidad_elementos and not self.detener:
            if self.cantidad_hilos < 30:
                cbi = self.session.query(Comicbook_Info).get(self.comicIds[index].id_comicbook_info)
                if cbi is None or not self.actualizar_solo_numeros_nuevos:
                    print("ACCCCCCCCCCCCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAAAAAaA")
                    hilo = threading.Thread(target=self.hilo_procesar_comic_in_volume, name=str(index),
                                            args=[self.comicIds[index], volumen, index])
                    self.lock.acquire(True)
                    self.lista_hilos_ejecucion[index] = hilo
                    self.cantidad_hilos += 1
                    self.lock.release()
                    hilo.start()

                index += 1
                '''multiplicamos por dos porque una vez que cargue todo los issues vamos a buscar los arcos
                en el peor de los casos tenemos un arco por issue por eso es el 2'''
                self.porcentaje_procesado = int(100 * (index - 1) / (2 * cantidad_elementos))
            else:
                time.sleep(2)
            print("Procesado {} de {}".format(index, cantidad_elementos))
        # Aca iteramos hasta que todos los hilos terminen  de ejecutar.
        contador_intentos = 0
        while self.cantidad_hilos > 0:
            print("ESPERANDO A TERMINAR Hilos: {}".format(self.cantidad_hilos))
            elementos = [(self.comicIds[index], index) for index, elemento in self.lista_hilos_ejecucion.items()]
            print("hilos {}".format(elementos))
            time.sleep(5)
            if contador_intentos == 3:
                contador_intentos = 0
                lista = self.lista_hilos_ejecucion.items()
                for hilo in lista:
                    print("HILO: {}".format(hilo))
                    index = hilo[0]
                    print("Relanzando hilo {}".format(index))
                    # lo mato con un timeout y luego lo
                    hilo[1].join(1)
                    hilo_nuevo = threading.Thread(target=self.hilo_procesar_comic_in_volume, name=str(index),
                                                  args=[self.comicIds[index], volumen, index])
                    hilo_nuevo.start()
            contador_intentos += 1
        print("TERMINAMOSSSSSSSSSSSSSSSSSSSSSs")
        print(self.lista_comicbooks_info)
        if self.detener:
            print("Proceso detenido")
            return
        # si los calculos salieron bien aca deberíamos estar en el 50%
        self.porcentaje_procesado = 50

        # vamos a recuperar los arcos que haya en los comics usamos conjunto para eliminar repetidos
        set_ids_arcos = set()
        for issue in self.lista_comicbooks_info:
            print('ISSIE {}'.format(issue.id_comicbook_info))
            for arco in issue.lista_ids_arcos_para_procesar:
                set_ids_arcos.add(arco.id_arco_argumental)

        list_ids_arcos = list(set_ids_arcos)
        # creamos una lista de arcos y recuperamos toda su info
        cantidad_elementos = len(set_ids_arcos)
        print("lista de arcos{}".format(list_ids_arcos))
        self.lista_arcos = []
        index = 0
        while index < cantidad_elementos:
            if self.cantidad_hilos < 20:
                # print("Numero {} url:{}".format(index, lista_comics_in_volumen[index].site_detail_url))
                threading.Thread(target=self.hilo_procesar_arco, name=str(index), args=[list_ids_arcos[index]]).start()
                index += 1
                self.lock.acquire(True)
                self.cantidad_hilos += 1
                self.lock.release()
                self.porcentaje_procesado = 50 + int(100 * (index - 1) / (2 * cantidad_elementos))
            else:
                time.sleep(2)

        # Aca iteramos hasta que todos los hilos terminen  de ejecutar.
        while self.cantidad_hilos > 0:
            time.sleep(2)

        for arco in self.lista_arcos:
            print(arco)



        self.porcentaje_procesado = 100
        print("TERMINO")

    def cargar_comicbook_info(self, volumen):
        self.porcentaje_procesado = 0
        self.lista_comicbooks_info.clear()
        threading.Thread(target=self.hilo_cargar_comicbook_info, args=[volumen]).start()

    def vineSearchMore(self):
        return self.vineSearch(self.offset + self.limit)

    def vine_Search_all(self):
        # este llamado no da info de cuantas paginas tiene la consulta en total

        self.vineSearch()
        if self.cantidadPaginas > 150:
            return 1
        self.hilos = []
        for i in range(1, self.cantidadPaginas):
            self.hilos.append(threading.Thread(target=self.vineSearch, args=[i * self.limit]))
        for hilo in self.hilos:
            hilo.start()
        while len(self.hilos) > 0:
            print("quedan {} hilos".format(len(self.hilos)))
            time.sleep(2)
        print("recuperacion de informacion finalizada")
        return 0

    def vineSearch(self, io_offset=0):
        if self.entidad == '':
            self.statusMessage = 'falta ingresar la entidad'
            print("Status: {}".format(self.statusMessage))
            return
        if self.filter == '' or len(self.filter) < 3:
            print("FILTRO: {}".format(self.filter))
            self.statusMessage = 'falta ingresar un filtro o su longitud debe ser mayor o igual a 3 caracteres'
            print("Status: {}".format(self.statusMessage))
            return

        self.offset = io_offset

        url = 'http://www.comicvine.com/api/' + self.entidad + '/?api_key=' + self.vinekey + self.filter + '&offset=' + str(
            self.offset)
        print("Clave: {}\noffset:{}\nurl:{}".format(self.vinekey, self.offset, url))
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
            self.cantidadPaginas = math.ceil(self.cantidadResultados / self.limit)
            status_code = root.find('status_code').text
            results = root.find('results')
            if self.entidad == 'issues':
                for item in results:
                    comic = Comicbook()
                    comic.fechaTapa = item.find('cover_date').text
                    comic.titulo = item.find('name').text
                    if comic.titulo is None:
                        comic.titulo = ''
                    comic.resumen = item.find('description').text
                    comic.comicVineId = item.find('id').text
                    comic.numero = item.find('issue_number').text
                    comic.api_detail_url = item.find('api_detail_url').text
                    comic.thumb_url = item.find('image').find('small_url').text
                    comic.volumeNombre = item.find('volume').find('name').text
                    comic.volumeId = item.find('volume').find('id').text
                    self.listaBusquedaVine.append(
                        comic)

            elif self.entidad == 'volumes':
                for item in results:
                    l_serie = Entidades.Agrupado_Entidades.Volume(id_volume=int(item.find('id').text),
                                                                  nombre=item.find('name').text)

                    l_serie.descripcion = item.find('description').text
                    l_serie.cantidad_numeros = item.find('count_of_issues').text
                    if item.find('image').find('thumb_url') != None:
                        l_serie.image_url = item.find('image').find('super_url').text
                    else:
                        l_serie.image_url = ''

                    if item.find('publisher').find('id') != None:
                        l_serie.id_publisher = int(item.find('publisher').find('id').text)
                        l_serie.publisher_name = item.find('publisher').find('name').text
                    else:
                        l_serie.id_publisher_externo = "-1"
                    l_serie.anio_inicio = item.find('start_year').text
                    self.listaBusquedaVine.append(l_serie)

            elif self.entidad == 'publishers':
                for item in results:
                    publisher = Publisher()
                    publisher.id_publisher = item.find('id').text
                    # publisher.id_publisher se auto calcula esto ahora
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

        if io_offset > 0:
            self.hilos.pop()
        self.statusMessage = 'Ok'


if __name__ == '__main__':
    cv = ComicVineSearcher('7e4368b71c5a66d710a62e996a660024f6a868d4', None)
    comics_searcher = Comic_Vine_Info_Searcher(cv.session)
    ##    cv = comicVineSearcher('64f7e65686c40cc016b8b8e499f46d6657d26752')
    # cv.setEntidad('volumes')
    # cv.addFilter("name:" + 'batman')
    # cv.vine_Search_all()
    # # volumen = cv.getVineEntity('2839')
    # for comic in cv.listaBusquedaVine:
    #     print(comic)
    comics_searcher = Comic_Vine_Info_Searcher(self.session)
    comicbook_info = comics_searcher.search_issue(comic_in_volume.site_detail_url)
    comicbook_info.id_comicbook_info = comic_in_volume.id_comicbook_info
    comicbook_info.id_volume = volumen.id_volume
    comicbook_info.nombre_volumen = volumen.nombre

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
