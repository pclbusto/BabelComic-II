from sqlalchemy import Column, Integer, String, Float,ForeignKey
import Entidades.Init

class ComicBookDetails(Entidades.Init.Base):
    __tablename__ = 'Comicbooksdetails'
    COVER = 1
    comicId = Column(Integer, primary_key=True)
    indicePagina = Column(Integer,default=0,primary_key=True)
    ordenPagina = Column(Integer, nullable=False, default=0)
    #portada = 1, pagina = 2
    tipoPagina = Column(Integer, nullable=False, default=2)
    