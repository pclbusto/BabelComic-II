from sqlalchemy import Column, Integer, String
import Entidades.Init


class SetupVinekeyStatus(Entidades.Init.Base):
    __tablename__='SetupVineKeysStatus'
    key = Column(String, primary_key=True)
    recursoId = Column(String, primary_key=True)
    cantidadConsultas = Column(Integer)
    fechaHoraInicioConsulta = Column(Integer)

    def __repr__(self):
        return "<SetupVinekeyStatus(Clave='%s')>" %(self.key)

