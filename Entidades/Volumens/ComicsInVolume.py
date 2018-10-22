from sqlalchemy import Column, Integer, String,Numeric
import Entidades.Init

class ComicInVolumes(Entidades.Init.Base):
    __tablename__='ComicsInVolumes'
    # no lo pasamos a numerico porque algunos numeros tiene 11.3B

    numero = Column(String, primary_key=True)
    id_comicbook_externo = Column(String, nullable=False, default='')
    id_volume = Column(Integer, primary_key=True, default='')
    # mantenemos esto para poder borrar
    id_volume_externo = Column(Integer, primary_key=True, default='')
    titulo = Column(String, nullable=False, default='')

    def __repr__(self):
        return "numero={} - id_comicbook_externo={} - id_volume_externo={} - titulo={}".format(self.numero, self.id_comicbook_externo, self.id_volume_externo, self.titulo)