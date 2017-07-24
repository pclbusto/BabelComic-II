from sqlalchemy import Column, Integer, String, Float,ForeignKey
import Entidades.Init

class ComicBookDetails(Entidades.Init.Base):
    __tablename__ = 'Comicbooksdetails'
    comicId = Column(Integer, primary_key=True)
    nombreArchivoPagina = Column(String,nullable=False,default='',primary_key=True)
    ordenPagina = Column(Integer, nullable=False, default=0)
    #portada = 1, pagina = 2
    tipoPagina = Column(Integer, nullable=False, default=2)
    