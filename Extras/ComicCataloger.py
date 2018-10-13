import Entidades.Init
import Entidades.Volumes.Volume
from Entidades.ComicBooks.ComicBook import ComicBook
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

    def loadComicsFromList(self, lista):
        for nombreComic in lista:
            comic = None
            comic = self.session.query(ComicBook).filter(ComicBook.path == nombreComic).order_by(
                ComicBook.path.asc()).first()
            if comic is not None:
                self.listaComicsACatalogar.append(comic)


    def copyFromComicToComic(self, fuente, destino):
        # print(fuente)
        if fuente.arcoArgumentalId is not None:
            destino.arcoArgumentalId = fuente.arcoArgumentalId
            destino.arcoArgumentalNumero = fuente.arcoArgumentalNumero
        if fuente.volumeId is not None:
            print(fuente.volumeId)
            volume = self.session.query(Entidades.Volumes.Volume.Volume).get(fuente.volumeId)
            destino.publisherId = volume.publisherId

        destino.fechaTapa = fuente.fechaTapa
        destino.titulo = fuente.titulo
        destino.volumeId = fuente.volumeId
        destino.numero = fuente.numero
        destino.resumen = fuente.resumen
        destino.nota = fuente.nota
        destino.rating = fuente.rating
        destino.ratingExterno = fuente.ratingExterno
        destino.comicVineId = fuente.comicVineId
        self.session.commit()
        if not destino.has_xml():
            cbFile = destino.editCbFile()
            xml_manager = XmlManager(self.session)
            xml_manager.set_xml_for_comic(destino)





