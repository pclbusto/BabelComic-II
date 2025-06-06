

from Entidades.Entity_manager import Entity_manager
from Entidades.Agrupado_Entidades import Arco_Argumental, Arcos_Argumentales_Comics_Reference, Setup, Comicbook_Detail
from Entidades.Agrupado_Entidades import Publisher, Volume, Comicbook_Detail, Comicbook_Info, Comicbook, Comicbook_Info_Cover_Url
from Entidades import Init
from sqlalchemy import func, join, and_
import os
import urllib.request
from PIL import Image
import threading
import gi
import ssl
import shutil

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from sqlalchemy import func

class Comicbooks_Info(Entity_manager):


    def __init__(self, session=None):
        Entity_manager.__init__(self, session=session, clase=Comicbook_Info)
        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()
        self.setup = self.session.query(Setup).first()
        self.set_order(Comicbook_Info.titulo, 0)
        self.lista_opciones = {'Número': Comicbook_Info.numero, 'Título': Comicbook_Info.titulo}

        self.status = 1
        self.entidad = Comicbook_Info()
        self.filtro = None
        self.id_volume = None
        self.set_order(Comicbook_Info.numero)
        self.direccion = 0
        self.index_lista_covers = 0
        self.index_lista_arcs = 0
        self.lista_covers = []
        self.lista_arcs = []
        self.lock = threading.Lock()
        self.lock_principal = threading.Lock()
        self.lista_covers_downloading = []
        self.callback = None
        ssl._create_default_https_context = ssl._create_unverified_context



    def load_cover_list(self):
        self.index_lista_covers = 0
        self.lista_covers = self.session.query(Comicbook_Info_Cover_Url).filter(
            Comicbook_Info_Cover_Url.id_comicbook_info == self.entidad.id_comicbook_info).all()

    def load_arcs_list(self):
        self.index_lista_arcs = 0
        self.lista_arcs = self.session.query(Arcos_Argumentales_Comics_Reference).filter(
            Arcos_Argumentales_Comics_Reference.id_comicbook_info == self.entidad.id_comicbook_info).all()

    def _get_cover_complete_path(self, callback):
        self.callback = callback
        comicbook_info_cover_url = self.lista_covers[self.index_lista_covers]
        #comicbook_info_cover_url = self.lista_covers[0]
        web_image = comicbook_info_cover_url.thumb_url
        nombreImagen = web_image[web_image.rindex('/') + 1:]
        carpeta_volumen_covers = self.entidad.nombre_volumen.replace('/', '-').replace('\\', '-')
        if not os.path.isdir(self.setup.directorioBase + os.sep + "images" + os.sep + "issues_covers" + os.sep + "{}-{}".format(self.entidad.id_volume, carpeta_volumen_covers) + os.sep):
            os.mkdir(self.setup.directorioBase + os.sep + "images" + os.sep + "issues_covers" + os.sep + "{}-{}".format(self.entidad.id_volume, carpeta_volumen_covers) + os.sep)
        path = self.setup.directorioBase + os.sep + "images" + os.sep + "issues_covers" + os.sep + "{}-{}".format(self.entidad.id_volume, carpeta_volumen_covers) + os.sep
        if not (os.path.isfile(path + nombreImagen)):
            self.descargar_imagen(web_image, path + nombreImagen)
        return path + nombreImagen

    def _get_cover_complete_path_no_thread(self):
        comicbook_info_cover_url = self.lista_covers[self.index_lista_covers]
        #comicbook_info_cover_url = self.lista_covers[0]
        web_image = comicbook_info_cover_url.thumb_url
        nombreImagen = web_image[web_image.rindex('/') + 1:]
        carpeta_volumen_covers = self.entidad.nombre_volumen.replace('/', '-').replace('\\', '-')
        if not os.path.isdir(self.setup.directorioBase + os.sep + "images" + os.sep + "issues_covers" + os.sep + "{}-{}".format(self.entidad.id_volume, carpeta_volumen_covers)+os.sep):
            os.mkdir(self.setup.directorioBase + os.sep + "images" + os.sep + "issues_covers" + os.sep + "{}-{}".format(self.entidad.id_volume, carpeta_volumen_covers)+os.sep)
        path = self.setup.directorioBase + os.sep + "images" + os.sep + "issues_covers" + os.sep + "{}-{}".format(self.entidad.id_volume, carpeta_volumen_covers)+os.sep
        if not (os.path.isfile(path + nombreImagen)):
            #esto se llama sin Thread porque se maneja mas arriba esto para poder sincronizar con Gui
            self.descargar_imagen_thread(web_image, path + nombreImagen)
        return path + nombreImagen

    def descargar_imagen(self, web_image, nombre_imagen):
        threading.Thread(target=self.descargar_imagen_thread, args=[web_image, nombre_imagen]).start()


    '''
    Descarga todas las imagenes y retorna la primera
    '''
    def get_first_cover_complete_path(self):
        #esta imagen la recuperamos sin hilo para estar seguros que bajamos la primera o si ya esta retornarla
        path = self._get_cover_complete_path_no_thread()
        #esto deberia de crear n hilos pero retornar a la ventana
        for index in range(1, len(self.lista_covers)):
            self.index_lista_covers = index
            self._get_cover_complete_path(None)
        self.index_lista_covers = 0
        return path

    def get_cover_complete_path(self):
        #esta imagen la recuperamos sin hilo para estar seguros que bajamos la primera o si ya esta retornarla
        path = self._get_cover_complete_path_no_thread()
        return path

    def descargar_imagen_thread(self, web_image, nombre_imagen):
        self.lock_principal.acquire(True)
        if nombre_imagen not in self.lista_covers_downloading:
            self.lock.acquire(True)
            self.lista_covers_downloading.append(nombre_imagen)
            self.lock.release()
            print('no existe')
            print(nombre_imagen)
            print(web_image)
            jpg = urllib.request.urlopen(web_image)
            jpgImage = jpg.read()
            fImage = open(nombre_imagen, 'wb')
            fImage.write(jpgImage)
            fImage.close()
            self.lock.acquire(True)
            self.lista_covers_downloading.remove(nombre_imagen)
            self.lock.release()
        self.lock_principal.release()

    def get_next_cover_complete_path(self):
        if self.index_lista_covers < len(self.lista_covers)-1:
            self.index_lista_covers += 1
        print(self.index_lista_covers)
        return self._get_cover_complete_path(None)

    def get_prev_cover_complete_path(self):
        if self.index_lista_covers > 0:
            self.index_lista_covers -= 1
        return self._get_cover_complete_path(None)

    def set_volume(self, id_volume):
        self.id_volume = id_volume
        filtro = Comicbook_Info.id_volume == id_volume
        self.set_filtro(filtro)

    def getFirst(self):
        entidad = super().getFirst()
        self.load_cover_list()
        return entidad

    def getLast(self):
        entidad = super().getLast()
        self.load_cover_list()
        return entidad

    def get(self, id_comicbook_info):
        #print("Revision existencia de comickbook_info: {}".format(id_comicbook_info))
        entidad = super().get(id_comicbook_info)
        if entidad is not None:
            self.load_cover_list()
            self.load_arcs_list()
        else:
            print("comickbook_info: {} no existe".format(id_comicbook_info))
        return entidad

    def getNext(self):
        entidad = super().getNext()
        self.load_cover_list()
        return entidad

    def getPrev(self):
        entidad = super().getPrev()
        self.load_cover_list()
        return entidad

    def rm_from_volumen(self, id_volumen):
        self.set_filtro(Comicbook_Info.id_volume == id_volumen)
        print("aca estamos ahora por borrar el filtro")
        for item in self.getList():
            print(item.titulo)
        self.rm_by_filter()



class ArcosArgumentales(Entity_manager):
    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Arco_Argumental)
        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Arco_Argumental.nombre, 0)
        self.lista_opciones = {'Id': Arco_Argumental.id_arco_argumental, 'Arco Argumental': Arco_Argumental.nombre}

        self.status = 1
        self.entidad = Arco_Argumental()
        self.filtro = None
        self.set_order(Arco_Argumental.id_arco_argumental)
        self.direccion = 0

    def rm(self, Id):
        Entity_manager.rm(self)
        self.session.query(Arcos_Argumentales_Comics_Reference).filter(Arco_Argumental.id_arco_argumental==Id).delete()
        self.session.commit()

class Publishers(Entity_manager):

    def __init__(self, session = None, clase=Publisher):
        Entity_manager.__init__(self, session=session, clase=clase)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Publisher.id_publisher, 0)
        self.lista_opciones = {'Id': Publisher.id_publisher, 'Editorial': Publisher.name}

        self.status = 1
        self.entidad = Publisher()
        self.filtro = None
        self.set_order(Publisher.id_publisher)
        self.direccion = 0

class Volumens(Entity_manager):

    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Volume)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Volume.nombre, 0)
        self.lista_opciones = {'Id': Volume.id_volume, 'Volumen': Volume.nombre}

        self.status = 1
        self.entidad = Volume()
        self.filtro = None
        self.set_order(Volume.id_volume)
        self.direccion = 0

    def get_comicbook_info_by_volume(self):
        sq = self.session.query(Comicbook.id_comicbook_info, func.count(Comicbook.id_comicbook).label('cantidad')).filter(Comicbook.en_papelera==False).join(Comicbook_Info,
                                                                                              Comicbook_Info.id_comicbook_info == Comicbook.id_comicbook_info).group_by(
            Comicbook.id_comicbook_info).subquery("sq")
        comics = self.session.query(Comicbook_Info.id_comicbook_info, Comicbook_Info.numero,Comicbook_Info.titulo, sq.c.cantidad, Comicbook_Info.orden).outerjoin(sq,
                                                                                     sq.c.id_comicbook_info == Comicbook_Info.id_comicbook_info).filter(Comicbook_Info.id_volume == self.entidad.id_volume).all()

        return comics

    def get_comicbook_info_status(self, id_comicbook_info):
        return self.session.query(Comicbook).filter(Comicbook.id_comicbook_info==id_comicbook_info).count()

    def get_volume_status(self):
        sq = self.session.query(Comicbook.id_comicbook_info).join(Comicbook_Info,
                                                             Comicbook_Info.id_comicbook_info == Comicbook.id_comicbook_info).filter(
            Comicbook_Info.id_volume == self.entidad.id_volume).group_by(Comicbook.id_comicbook_info).subquery("sq")
        cantidad = self.session.query(Comicbook_Info.id_comicbook_info).join(sq,
                                                                      sq.c.id_comicbook_info == Comicbook_Info.id_comicbook_info).count()

        return cantidad

    def get_cantidad_comics_asociados_al_volumen(self):
        sq = self.session.query(Comicbook.id_comicbook_info).filter(Comicbook.en_papelera==False).join(Comicbook_Info,
                                                             Comicbook_Info.id_comicbook_info == Comicbook.id_comicbook_info).filter(
            Comicbook_Info.id_volume == self.entidad.id_volume).subquery("sq")
        cantidad = self.session.query(Comicbook_Info.id_comicbook_info).join(sq,
                                                                      sq.c.id_comicbook_info == Comicbook_Info.id_comicbook_info).count()

        return cantidad

    def get_cantidad_comics_asociados_a_volumenes(self):
        #join para saber a que coicbook_info pertenece y asi tener el volumen id
        lista_cantidades = [Volume.id_volume, 0, 0]
        lista_cantidades = self.session.query(Volume.id_volume, Volume.cantidad_numeros, func.count(Comicbook.id_comicbook)).filter(Comicbook_Info.id_volume == Volume.id_volume).filter(Comicbook.id_comicbook_info == Comicbook_Info.id_comicbook_info).group_by(Volume.id_volume).all()
        self.cantidades_por_volumen = {}
        for registro in lista_cantidades:
            self.cantidades_por_volumen[str(registro[0])] = (registro[1], registro[2])

        #print(self.cantidades_por_volumen)

    def new_record(self):
        super().new_record()
        setup = self.session.query(Setup).first()
        id_volume = setup.ultimoVolumeIdUtilizado
        setup.ultimoVolumeIdUtilizado = str(int(id_volume)+1)
        self.session.add(setup)
        self.session.commit()
        self.entidad.id_volume = -1*int(id_volume)
        self.entidad.cantidad_numeros = 0
        self.entidad.anio_inicio = 0
        self.entidad.deck= ''
        self.entidad.descripcion = ''
        self.entidad.id_publisher = ''
        self.entidad.image_url = ''
        self.entidad.nombre= ''
        self.entidad.publisher_name = ''
        self.entidad.url = ''

    def normalizar_comics_vinculados(self):
        path_final = '/mnt/Green/Comics/Biblioteca de Babelcomics'
        print("Volumen:{} Año:{}".format(self.entidad.nombre, self.entidad.anio_inicio))
        publishers = Publishers(session=self.session)
        publishers.get(self.entidad.id_publisher)
        print(publishers.entidad.name)
        path_final = path_final +os.sep+"{}".format(publishers.entidad.name)
        if not os.path.exists(path_final):
            os.mkdir(path_final)
        path_final = path_final+os.sep+"{}-{}".format(self.entidad.nombre, self.entidad.anio_inicio)
        print(path_final)
        if not os.path.exists(path_final):
            os.mkdir(path_final)
        comics = Comicbooks(session=self.session)
        comics.listar_comic_del_volumen(id_volumen=self.entidad.id_volume)
        comics.copiar_a_nueva_carpeta(new_path=path_final, create_new_comicbooks_entry=True)

    def rm(self):
        print("aca estamos")
        super().rm()
        comicbooks_info = Comicbooks_Info(session=self.session)
        comicbooks_info.rm_from_volumen(self.entidad.id_volume)


class Comicbooks_Detail(Entity_manager):

    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Comicbook_Detail)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Comicbook_Detail.comicbook_id,0)
        self.lista_opciones = {'Id': Comicbook_Detail.comicbook_id}

        self.status = 1
        self.entidad = Comicbook_Detail()
        self.filtro = None
        self.set_order(Comicbook_Detail.comicbook_id)
        self.direccion = 0

class Commicbooks_detail(Entity_manager):
    def __init__(self, session=None):
        Entity_manager.__init__(self, session=session, clase=Comicbook_Detail)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Comicbook_Detail.comicbook_id, 0)
        self.lista_opciones = {'Id': Comicbook_Detail.comicbook_id}

        self.status = 1
        self.entidad = Comicbook_Detail()
        self.filtro = None
        self.set_order(Comicbook_Detail.comicbook_id)
        self.direccion = 0
        self.comicbook_id = None

    def load_setup(self):
        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                            "coverIssuesThumbnails" + os.path.sep
        self.ancho_thumnail = self.session.query(Setup).first().anchoThumnail

        print("self.pahThumnails", self.pahThumnails)

    def save_page_datail(self, id_page):
        self.new_record()

    def set_comicbook(self, comicbookid):
        self.comicbook_id = comicbookid

    def set_page_type(self, page_name, tipo):
        self.entidad = self.session.query(Comicbook_Detail).filter(Comicbook_Detail.nombre_pagina == page_name, Comicbook_Detail.comicbook_id == self.comicbook_id).one()
        self.entidad.tipoPagina = tipo
        self.save()

    def crear_thumnail_cover(self, recrear=False):
        try:
            # pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
            #                    "coverIssuesThumbnails" + os.path.sep
            self.load_setup()
            comicbooks = Comicbooks(self.session)
            comicbooks.get(self.comicbook_id)
            nombreThumnail = self.pahThumnails + str(comicbooks.entidad.id_comicbook) + '.jpg'
            print("Generando thumnail {}".format(nombreThumnail))
            cover = None
            if not os.path.isfile(nombreThumnail) or recrear:
                if comicbooks.entidad.openCbFile() == -1:
                    print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
                    cover = Pixbuf.new_from_file(self.pahThumnails + "error_caratula.png")
                else:

                    #vampos a buscar que nro de page es la cover
                    self.set_filtro(and_(Comicbook_Detail.comicbook_id == self.comicbook_id, Comicbook_Detail.tipoPagina == Comicbook_Detail.PAGE_TYPE_COVER))
                    print("recuperamos el detalle------------")

                    pagina_cover = self.getFirst()
                    if pagina_cover is not None:
                        print("NUMERO PAGINA COVER: {}".format(pagina_cover.nombre_pagina))
                        comicbooks.entidad.goto_page_by_name(pagina_cover.nombre_pagina)
                    else:
                        comicbooks.entidad.goto(0)

                    imagen_ancho_porcentaje = self.ancho_thumnail / comicbooks.entidad.getImagePage().size[0]
                    self.size = (int(self.ancho_thumnail), int(imagen_ancho_porcentaje * comicbooks.entidad.getImagePage().size[1]))
                    cover = comicbooks.entidad.getImagePage()
                    cover = cover.resize(self.size, Image.LANCZOS).crop((0, 0, self.size[0], self.size[1]))
                    cover.convert('RGB').save(nombreThumnail)
                    cover.save(nombreThumnail)
                    comicbooks.entidad.closeCbFile()
                    cover = Pixbuf.new_from_file(nombreThumnail)
            else:
                if os.path.isfile(nombreThumnail):
                    cover = Pixbuf.new_from_file(nombreThumnail)
            #------------------------------
                    #     print("No tiene thumnail vamos a crearlo")
                    #     nombreThumnail = self.pahThumnails + str(comic.id_comicbook) + '.jpg'
                    #     if not os.path.isfile(nombreThumnail):
                    #         first_comicbook_detail = self.session.query(Comicbook_Detail).filter(
                    #             Comicbook_Detail.comicbook_id == comic.id_comicbook).filter(
                    #             Comicbook_Detail.tipoPagina == Comicbook_Detail.PAGE_TYPE_COVER).first()
                    #         if first_comicbook_detail:
                    #             comic.goto(first_comicbook_detail.indicePagina)
                    #         print("cover", comic.getImagePage().size[0])
                    #         imagen_ancho_porcentaje = self.ancho_thumnail / comic.getImagePage().size[0]
                    #         print("Procentaje ancho: ", imagen_ancho_porcentaje)
                    #         self.size = (int(self.ancho_thumnail), int(imagen_ancho_porcentaje*comic.getImagePage().size[1]))
                    #         cover = comic.getImagePage()
                    #         cover = cover.resize(self.size, Image.LANCZOS).crop((0, 0, self.size[0], self.size[1]))
                    #         cover.convert('RGB').save(nombreThumnail)
                    #     cover = Pixbuf.new_from_file(nombreThumnail)
                    #     comic.closeCbFile()
                    #
            #--------------------------------
        except Exception :
            print('error en el archivo ' + self.entidad.path)
        print('termiando crear_thumnails_background')
        return cover


class Comicbooks(Entity_manager):
    def __init__(self, session=None, lista_comics_id=None):
        Entity_manager.__init__(self, session=session, clase=Comicbook)
        # lista_comics_id: Lista de ids con las que quiero que trabaje el manager. Si seteo se usa como filtro contra
        # la base de datos para recuperar los comicbook que se correspondan con los Ids pasados como parametros.

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Comicbook.id_comicbook, 0)
        self.lista_opciones = {'Id': Comicbook.id_comicbook, 'Path': Comicbook.path}
        self.filtro = None
        if lista_comics_id is not None:
            self.set_filtro(Comicbook.id_comicbook.in_(lista_comics_id))
        self.status = 1
        self.entidad = Comicbook()
        self.set_order(Comicbook.path)
        self.direccion = 0
        self.atributo_clave = Comicbook.id_comicbook

    def hay_comics_en_papelera(self):
        retorno = self.session.query(Comicbook).filter(Comicbook.en_papelera == True).count() > 0
        print(retorno)
        return(retorno)

    def tiene_detalle(self):
        print("CONTANDO")
        cantidad_registros = self.session.query(Comicbook_Detail.indicePagina).filter(Comicbook_Detail.comicbook_id == self.entidad.id_comicbook).count()
        print("CONTANDO", cantidad_registros)

        return cantidad_registros > 0

    def listar_comic_del_volumen(self, id_volumen=""):
        comics_info = Comicbooks_Info()
        comics_info.set_filtro(Comicbook_Info.id_volume == id_volumen)
        lista_ids_comic_info = []
        for comic_info in comics_info.getList():
            lista_ids_comic_info.append(comic_info.id_comicbook_info)
        self.set_filtro(Comicbook.id_comicbook_info.in_(lista_ids_comic_info))
        self.set_filtro(Comicbook.en_papelera == False)
        return self.getList()

    def borrar_comics_de_papelera(self, lista_comics = None):
        if lista_comics is not None:
            print(lista_comics)
            for comicbook in lista_comics:
                comicbook_aux = self.get(int(comicbook.id_comicbook))
                if os.path.exists(comicbook_aux.path):
                    os.remove(comicbook_aux.path)
                self.rm()

    def copiar_a_nueva_carpeta(self, new_path=None, create_new_comicbooks_entry=False):
        if new_path is not None:
            lista_comics = self.getList()
            for comicbook in lista_comics:
                comics_info = Comicbooks_Info()
                comic_info = None
                if "Biblioteca de Babelcomics" not in comicbook.path:
                    if comicbook.id_comicbook_info != '':
                        comics_info.set_filtro(Comicbook_Info.id_comicbook_info == comicbook.id_comicbook_info)
                        comic_info = comics_info.getList()[0]
                    if comics_info is not None:
                        volumens = Volumens()
                        volumens.set_filtro(Volume.id_volume == comic_info.id_volume)
                        volume = volumens.getList()[0]

                        new_file_path = new_path+os.sep+volume.nombre+" - V"+str(volume.anio_inicio)+" - " +comic_info.numero.rjust(4,"0")+"."+comicbook.getTipo()
                    else:
                        new_file_path = new_path + os.sep + comicbook.getNombreArchivo()
                    secuencia = 0
                    if os.path.exists(new_file_path):
                        secuencia = 1
                        file_path_aux = new_file_path[:-4] + "-" + str(secuencia).rjust(2, "0") + new_file_path[-4:]
                        while os.path.exists(file_path_aux):
                            secuencia += 1
                            file_path_aux = new_file_path[:-4] + "-" + str(secuencia).rjust(2, "0") + new_file_path[-4:]
                            print(file_path_aux)

                    if secuencia >=1:
                    #     la estructura de new_file_path es nombre.<extension>
                        new_file_path = new_file_path[:-4]+"-"+str(secuencia).rjust(2,"0")+new_file_path[-4:]
                    print(new_file_path)
                    shutil.copyfile(comicbook.path,new_file_path)
                    # Creamos la nueva entrada en la base de datos para mantener los comics que ya estan catalogados como catalogados y no perder esa info
                    new_comicbook = Comicbook()
                    new_comicbook.path = str(new_file_path)
                    new_comicbook.id_comicbook_info = comicbook.id_comicbook_info
                    comic_aux = self.session.query(Comicbook).filter(Comicbook.path == new_file_path).first()
                    if comic_aux is None:
                        self.session.add(new_comicbook)
                        comicbook.en_papelera = True
                        self.session.commit()


if (__name__=='__main__'):

    path = "/home/pedro/test"
    lista = os.listdir(path)
    lista_directorios = []
    for item in lista:
        if os.path.isdir(path+os.sep+item):
            lista_directorios.append(path+os.sep+item)
    for item in lista_directorios:
        print('zip -r "{}.cbz" "{}"'.format(item, item))

