from sqlalchemy import Column, Integer, String, and_
import Entidades.Init
from Entidades.ArcosArgumentales.ArcosArgumentalesComics import ArcosArgumentalesComics
from sqlalchemy import Sequence

class ArcoArgumental(Entidades.Init.Base):
    # todo implementar gui para ver y administar
    __tablename__ = 'ArcosArgumentales'
    id_arco_argumental = Column(Integer, Sequence('arco_id_seq'), primary_key=True)
    id_arco_argumental_externo = Column(String,primary_key=True)
    nombre = Column(String,nullable=False,default='')
    deck = Column(String,nullable=False,default='')
    descripcion = Column(String,nullable=False,default='')
    ultimaFechaActualizacion =  Column(Integer,nullable=False,default='')

    def getIssueOrder(self,idComic):
        session = Entidades.Init.Session()
        orden = session.query(ArcosArgumentalesComics).filter(and_(ArcosArgumentalesComics.idArco == self.id, ArcosArgumentalesComics.idComic==idComic)).first()
        if orden is not None:
            return orden.orden
        return -1
    def getIssuesCount(self):
        session = Entidades.Init.Session()
        cantidad = session.query(ArcosArgumentalesComics).filter(ArcosArgumentalesComics.idArco == self.id).count()
        return cantidad

    def getCantidadTitulos(self):
        return (len(self.comics))

