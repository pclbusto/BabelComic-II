from sqlalchemy import Column, Integer, String, and_
import Entidades.Init
from Entidades.ArcosArgumentales.ArcosArgumentalesComics import ArcosArgumentalesComics


class ArcoArgumental(Entidades.Init.Base):
    __tablename__ = 'ArcosArgumentales'
    id = Column(String,primary_key=True)
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

    def getCantidadTitulos(self):
        return (len(self.comics))

