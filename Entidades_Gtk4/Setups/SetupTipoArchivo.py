from sqlalchemy import Column, Integer, String
import Entidades.Init


class SetupTipoArchivo(Entidades.Init.Base):
    __tablename__='SetupTiposArchivo'
    tipoArchivo = Column(String, primary_key=True)

    def __repr__(self):
        return "<SetupTiposArchivo(tipoArchivo='%s')>" %(self.tipoArchivo)

