from sqlalchemy import Column, Integer, String
import Entidades.Init


class Setup(Entidades.Init.Base):
    __tablename__='Setups'
    setupkey = Column(Integer, primary_key=True)
    '''desde este direcotrio se calculan el resto de los directorios. Por esto 
    este directorio debe ser donde esta el proyecto
    '''
    directorioBase = Column(String)

    def __repr__(self):
        return "<Setup(directorioBaseImagene='%s')>" %(self.directorioBase)
