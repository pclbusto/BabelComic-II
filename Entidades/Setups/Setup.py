from sqlalchemy import Column, Integer, String
import Entidades.Init


class Setup(Entidades.Init.Base):
    __tablename__='Setups'
    directorioBaseImagenes = Column(String, primary_key=True)

    def __repr__(self):
        return "<Setup(directorioBaseImagene='%s')>" %(self.pathDirectorio)
