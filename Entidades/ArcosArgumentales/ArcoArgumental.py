from sqlalchemy import Column, Integer, String, and_,ForeignKey
from sqlalchemy.orm import relationship
import Entidades.Init

from sqlalchemy import Sequence



class ArcoArgumental():
    # todo implementar gui para ver y administar
    __tablename__ = 'arcos_argumentales'

    id_arco_argumental = Column(Integer, Sequence('arco_id_seq'), primary_key=True)
    id_arco_argumental_externo = Column(String,nullable=False,default='')
    nombre = Column(String,nullable=False,default='')
    deck = Column(String,nullable=False,default='')
    descripcion = Column(String,nullable=False,default='')
    ultimaFechaActualizacion =  Column(Integer,nullable=False,default='')
    ids_comicbooks_Info = relationship("Comicbooks_Info", secondary=comicbook_info_arco_argumental)

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

