from Entidades.Entity_manager import Entity_manager
from Entidades.Agrupado_Entidades import Arco_Argumental, Arcos_Argumentales_Comics_Reference, Setup, Comicbook_Detail
from Entidades.Agrupado_Entidades import Publisher, Volume, Comicbook_Detail, Comicbook_Info, Comicbook, Comicbook_Info_Cover_Url
from Entidades import Init
from sqlalchemy import func, join, and_
import os
import urllib.request
from PIL import Image

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
        self.lista_covers = []

    def load_cover_list(self):
        self.index_lista_covers = 0
        self.lista_covers = self.session.query(Comicbook_Info_Cover_Url).filter(
            Comicbook_Info_Cover_Url.id_comicbook_info == self.entidad.id_comicbook_info).all()

    def _get_cover_complete_path(self):
        print("Comicbooks_Info._get_cover_complete_path")
        print(self.lista_covers)
        print("self.index_lista_covers {}".format(self.index_lista_covers))
        print("self.lista_covers count {}".format(len(self.lista_covers)))
        comicbook_info_cover_url = self.lista_covers[self.index_lista_covers]
        #comicbook_info_cover_url = self.lista_covers[0]
        webImage = comicbook_info_cover_url.thumb_url
        nombreImagen = webImage[webImage.rindex('/') + 1:]
        print(webImage)
        print(nombreImagen)
        path = self.setup.directorioBase + os.sep + "images" + os.sep + "searchCache" + os.sep
        if not (os.path.isfile(path + nombreImagen)):
            print('no existe')
            print(nombreImagen)
            jpg = urllib.request.urlopen(webImage)
            jpgImage = jpg.read()
            fImage = open(path + nombreImagen, 'wb')
            fImage.write(jpgImage)
            fImage.close()
        return path + nombreImagen

    def get_next_cover_complete_path(self):
        print("get_next_cover_complete_path");
        if len(self.lista_covers) - 1 > self.index_lista_covers:
            self.index_lista_covers += 1
        return self._get_cover_complete_path()

    def get_prev_cover_complete_path(self):
        if self.index_lista_covers > 0:
            self.index_lista_covers -= 1
        return self._get_cover_complete_path()

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
        entidad = super().get(id_comicbook_info)
        self.load_cover_list()
        return entidad

    def getNext(self):
        entidad = super().getNext()
        self.load_cover_list()
        return entidad

    def getPrev(self):
        entidad = super().getPrev()
        self.load_cover_list()
        return entidad


class ArcosArgumentales(Entity_manager):
    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Arco_Argumental, id_externo=Arco_Argumental.id_arco_argumental_externo)
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

        self.set_order(Publisher.id_publisher,0)
        self.lista_opciones = {'Id': Publisher.id_publisher, 'Editorial': Publisher.name}

        self.status = 1
        self.filtro = None
        self.order = None
        self.direccion = 0

class Volumens(Entity_manager):

    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Volume)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Volume.nombre,0)
        self.lista_opciones = {'Id': Volume.id_volume, 'Volumen': Volume.nombre}

        self.status = 1
        self.entidad=Volume()
        self.filtro = None
        self.set_order(Volume.id_volume)
        self.direccion = 0

    def get_comicbook_info_by_volume(self):
        sq = self.session.query(Comicbook.id_comicbook_info, func.count(1).label('cantidad')).join(Comicbook_Info,
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
        sq = self.session.query(Comicbook.id_comicbook_info).join(Comicbook_Info,
                                                             Comicbook_Info.id_comicbook_info == Comicbook.id_comicbook_info).filter(
            Comicbook_Info.id_volume == self.entidad.id_volume).subquery("sq")
        cantidad = self.session.query(Comicbook_Info.id_comicbook_info).join(sq,
                                                                      sq.c.id_comicbook_info == Comicbook_Info.id_comicbook_info).count()

        return cantidad

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
        self.entidad=Comicbook_Detail()
        self.filtro = None
        self.set_order(Comicbook_Detail.comicbook_id)
        self.direccion = 0

class Commicbooks_detail(Entity_manager):
    def __init__(self, session = None):
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

    def save_page_datail(self, id_page):
        self.new_record()

    def set_comicbook(self, comicbookid):
        self.comicbook_id = comicbookid

    def set_page_type(self, nro_pagina, tipo):
        #recuperamos una instancia de comick_detail que representa la pagina que le vamos a cambiar el tipo
        self.get((self.comicbook_id, nro_pagina))
        self.entidad.tipoPagina = tipo
        self.save()

    def crear_thumnail_cover(self, recrear=False):
        try:
            pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                               "coverIssuesThumbnails" + os.path.sep

            comicbooks = Commicbooks(self.session)
            comicbooks.get(self.comicbook_id)
            nombreThumnail = pahThumnails + str(comicbooks.entidad.id_comicbook) + '.jpg'
            print("Generando thumnail {}".format(nombreThumnail))
            cover = None
            if not os.path.isfile(nombreThumnail) or recrear:
                if comicbooks.entidad.openCbFile() == -1:
                    raise Exception("Error añ abrir el archuivo {}".format(comicbooks.entidad.id_comicbook))
                else:
                    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                    #vampos a buscar que nro de page es la cover
                    self.set_filtro(and_(Comicbook_Detail.comicbook_id == self.comicbook_id, Comicbook_Detail.tipoPagina == Comicbook_Detail.PAGE_TYPE_COVER))
                    get_nro_pagina_cover_nro_uno = self.getFirst()
                    print("NUMERO PAGINA COVER: {}".format(get_nro_pagina_cover_nro_uno.ordenPagina))
                    comicbooks.entidad.goto(get_nro_pagina_cover_nro_uno.ordenPagina)
                    imagen_height_percent = 350 / comicbooks.entidad.getImagePage().size[1]
                    self.size = (int(imagen_height_percent * comicbooks.entidad.getImagePage().size[0]), int(350))
                    cover = comicbooks.entidad.getImagePage().resize(self.size, Image.LANCZOS)
                    cover.save(nombreThumnail)
                    comicbooks.entidad.closeCbFile()
        except Exception :
            print('error en el archivo ' + self.entidad.path)
        print('termiando crear_thumnails_background')


class Commicbooks(Entity_manager):
    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Comicbook)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Comicbook.id_comicbook, 0)
        self.lista_opciones = {'Id': Comicbook.id_comicbook, 'Path':Comicbook.path}

        self.status = 1
        self.entidad = Comicbook()
        self.filtro = None
        self.set_order(Comicbook.path)
        self.direccion = 0

    def tiene_detalle(self):
        print("IIIIIID {}".format(self.entidad.id_comicbook))
        cantidad_registros = self.session.query(Comicbook_Detail.indicePagina).filter(Comicbook_Detail.comicbook_id == self.entidad.id_comicbook).count()
        print("Cantidad {}".format(cantidad_registros))
        return cantidad_registros > 0

if (__name__=='__main__'):
    # cbdm = Comicbooks_Detail()
    # cbd = cbdm.entidad
    # cbd.comicbook_id = 1
    # cbd.indicePagina = 1
    # cbd.ordenPagina = 1
    # cbd.tipoPagina = Comicbook_Detail.COVER
    # cbdm.save()
    cbm = Commicbooks_detail()
    cbm.getFirst()
    cb = cbm.entidad
    cb.openCbFile()
    cb.getImagePage().show()
    print(cb)


    #print(arco.getCantidadTitulos())
