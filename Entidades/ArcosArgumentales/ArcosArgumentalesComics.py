from sqlalchemy import Column, Integer, String
import Entidades.Init
#----------
class ArcosArgumentalesComics(Entidades.Init.Base):
    __tablename__='ArcosArgumentalesComics'
    idArco = Column(String,primary_key=True)
    idComic = Column(String,primary_key=True)
    orden = Column(Integer)