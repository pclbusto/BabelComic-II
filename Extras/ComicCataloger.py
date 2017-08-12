import Entidades.Init
import Entidades.Volumes.Volume

class Catalogador():

    session = None

    def __init__(self, session=None):
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

    def copyFromComicToComic(self, fuente, destino):
        print(fuente)
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
        # self.session.add(self.comicbook)
        self.session.commit()
        # como lo que traje de vine tiene toda la data directamente actualizo la base de datos
        # ComicBooks().update(completComicInfo)
