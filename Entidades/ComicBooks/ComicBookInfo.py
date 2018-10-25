from sqlalchemy import Column, Integer, String, Float,ForeignKey,Table
from sqlalchemy.orm import relationship
from Entidades.ArcosArgumentales.ArcoArgumental import ArcoArgumental
import Entidades.Init
from sqlalchemy import Sequence

comicbook_info_arco_argumental = Table('comicbook_info_arco_argumental', Entidades.Init.Base.metadata,
                          Column('id_comicbooks_Info',Integer, ForeignKey('comicbooks_info.id_comicbooks_Info')),
                          Column('id_arco_argumental',Integer, ForeignKey('arcos_argumentales.id_arco_argumental'))
)

'''Esta clase representa la metadata del comic. 
'''
class Comicbooks_Info(Entidades.Init.Base):

    __tablename__='comicbooks_info'

    id_comicbooks_Info = Column(Integer, Sequence('comicbook_id_seq'), primary_key=True)
    id_comicbooks_Info_externo = Column(String,nullable=False,default='')
    titulo = Column(String,nullable=False,default='')
    id_volume = Column(String, nullable=False, default='')
    nombre_volumen = Column(String,nullable=False,default='')
    numero = Column(String,nullable=False,default='0')
    fechaTapa = Column(Integer,nullable=False,default=0)  # como no hay date en sql lite esto es la cantidad de dias desde 01-01-01
    ids_arco_argumental = relationship("ArcoArgumental", secondary=comicbook_info_arco_argumental)
    arcoArgumentalNumero = Column(Integer,nullable=False,default=0) #numero dentro del arco
    resumen = Column(String,nullable=False,default='')
    nota = Column(String,nullable=False,default='')
    rating = Column(Float,nullable=False,default=0.0)
    ratingExterno = Column(Float,nullable=False,default=0.0)

    id_publisher = Column(String,nullable=False,default='')
    api_detail_url = Column(String,nullable=False,default='')
    thumbs_url  = relationship("Comicbook_Info_cover_url")

    '''Este campo se crea para ordenar los comics.
    Se cambia el numero que es de tipo int a string porque hay numeraciones comoc 616a de batman.
    El tema es que por ser string pierdo el orden entonces despues del 1 no viene el 2 si no 10.'''
    orden = Column(Integer,nullable=False,default=0 )


    def __repr__(self):
        return "titulo={}-comic vine id={}".format(self.titulo, self.id_comicbooks_Info_externo)

class Comicbook_Info_cover_url(Entidades.Init.Base):
    __tablename__ = 'comicbooks_info_cover_url'

    id_comicbooks_Info= Column(Integer, ForeignKey('comicbooks_info.id_comicbooks_Info'))
    thumb_url = Column(String, primary_key=True)
    # numero_dentro_arco = Column(Integer, nullable=False,default=0)

    def __repr__(self):
        return "thumb_url={}".format(self.thumb_url)


