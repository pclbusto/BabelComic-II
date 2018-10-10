from sqlalchemy import Column, Integer, String,Numeric
import Entidades.Init

class ComicInVolumes(Entidades.Init.Base):
    __tablename__='ComicsInVolumes'
    # no lo pasamos a numerico porque algunos numeros tiene 11.3B

    numero = Column(String, primary_key=True)
    comicVineId = Column(String, nullable=False, default='')
    volumeId = Column(String, primary_key=True, default='')
    titulo = Column(String, nullable=False, default='')

    def __repr__(self):
        return "numero={} - comicVineId={} - volumeId={} - titulo={}".format(self.numero, self.comicVineId, self.volumeId, self.titulo)