from sqlalchemy import Column, Integer, String
import Entidades.Init


'''Esta clase nos da un orden del arco. No se como construir esto desde el sistema porque si usuara el id_comic 
esto implicaría 
'''
class ArcosArgumentalesComics(Entidades.Init.Base):
    __tablename__='ArcosArgumentalesComics'
    id_arco_argumental = Column(String,primary_key=True)
    id_comicbook_externo = Column(String,primary_key=True)

    orden = Column(Integer)