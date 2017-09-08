from sqlalchemy import Column, Integer, String,Numeric
import Entidades.Init

class ComicInVolumes(Entidades.Init.Base):
    __tablename__='ComicsInVolumes'
    comicOrder = Column(Integer,nullable=False,default=0)
    comicNumber = Column(String, primary_key=True)
    comicVineId = Column(String, nullable=False, default='')
    volumenId = Column(String, primary_key=True, default='')
    offset = Column(Integer,nullable=False,default=0)
