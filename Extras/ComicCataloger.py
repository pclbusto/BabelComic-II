import Entidades.Init
import Entidades.Agrupado_Entidades
from Entidades.Agrupado_Entidades import Comicbook
from Extras.ComicXmlCreator import XmlManager
class Catalogador():
    # todo hacer que la catalogacion sea mediante hilos. De esta forma las consultas se pueden hacer X veces mas rápidas
    # la idea es similar a la consulta en volumenes que hacemos tantasa consultas como paginas.

    session = None
    '''lista comics que queremos catalogar'''
    listaComicsACatalogar = []
    '''lista de comics que se obtiene de la busqueda'''
    listaComicsBusquedaComicVine = []
    '''Aca cargamos una 2-upla origen destino. Para procesar y catalogar'''
    listaComicsParaProcesarCatalogacion = []
    '''Volumen sobre el cual buscar los numeros'''
    volumen = None
    '''Numero desde el cual vamos a filtra la busqueda. la lista "listaComicBusquedaComicVine" no debe tener comics
    cuyo numero sea mayor o menor que el numero desde y numero hasta'''
    numeroDesde=0
    numeroHasta=0


    def __init__(self, session=None):
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

    def catalogar_comics(self, lista_tupla_comicbook_numero, lista_comicbooks_info):
        for comicbook, numero in lista_comicbooks_info:
            for comicbook_info in lista_comicbooks_info:
                if numero == comicbook_info:
                    comicbook.id_comicbook_info = comicbook_info.id_comicbook_Info
                    self.session.add(comicbook)
        self.session.commit()


    def loadComicsFromList(self, lista):
        for nombreComic in lista:
            comic = None
            comic = self.session.query(Comicbook).filter(Comicbook.path == nombreComic).order_by(
                Comicbook.path.asc()).first()
            if comic is not None:
                self.listaComicsACatalogar.append(comic)


    def copyFromComicToComic(self, fuente, destino):
        # print(fuente)
        if fuente.arcoArgumentalId is not None:
            destino.id_arco_argumental = fuente.id_arco_argumental
            destino.arco_argumental_numero = fuente.arco_argumental_numero
        if fuente.id_volume is not None:
            # print(fuente.id_volume)
            volume = self.session.query(Entidades.Volumens.Volume.Volume).get(fuente.id_volume)
            destino.id_publisher = volume.id_publisher

        destino.fechaTapa = fuente.fechaTapa
        destino.titulo = fuente.titulo
        destino.volumeId = fuente.volumeId
        destino.numero = fuente.numero
        destino.resumen = fuente.resumen
        destino.nota = fuente.nota
        destino.rating = fuente.rating
        destino.ratingExterno = fuente.ratingExterno
        # print("DATO NULL")
        destino.id_comicbook_externo = fuente.id_comicbook_externo
        self.session.commit()
        if not destino.has_xml():
            cbFile = destino.editCbFile()
            xml_manager = XmlManager(self.session)
            xml_manager.set_xml_for_comic(destino)





