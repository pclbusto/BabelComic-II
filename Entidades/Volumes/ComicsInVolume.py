from sqlalchemy import Column, Integer, String
import Entidades.Init

class ComicInVolumes(Entidades.Init.Base):
    __tablename__='ComicsInVolumes'
    comicNumber = Column(Integer, primary_key=True)
    volumenId = Column(String, primary_key=True, default=0)

