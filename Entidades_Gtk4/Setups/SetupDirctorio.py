from sqlalchemy import Column, Integer, String
import Entidades.Init


class SetupDirectorio(Entidades.Init.Base):
    __tablename__='SetupDirectorios'
    pathDirectorio = Column(String, primary_key=True)

    def __repr__(self):
        return "<SetupDirectorio(Directorio='%s')>" %(self.pathDirectorio)
