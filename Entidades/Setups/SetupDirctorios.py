from sqlalchemy import Column, Integer, String
import Entidades.Init


class SetupDirectorios(Entidades.Init.Base):
    __tablename__='SetupDirectorios'
    pathDirectorio = Column(String, primary_key=True)

    def __repr__(self):
        return "<SetupDirectorios(Directorio='%s')>" %(self.pathDirectorio)

