from sqlalchemy import Column, Integer, String
import Entidades.Init


class SetupVinekey(Entidades.Init.Base):
    __tablename__='SetupVineKeys'
    key = Column(String, primary_key=True)

    def __repr__(self):
        return "<SetupVineKeys(Clave='%s')>" %(self.key)

