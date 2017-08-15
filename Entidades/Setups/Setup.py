from sqlalchemy import Column, Integer, String
import Entidades.Init
import os

class Setup(Entidades.Init.Base):
    __tablename__='Setups'
    setupkey = Column(Integer, primary_key=True)
    '''desde este direcotrio se calculan el resto de los directorios. Por esto 
    este directorio debe ser donde esta el proyecto
    '''
    directorioBase = Column(String,default='')

    '''sirve para paginar la consulta. Manejar tanatos elementos de una puede ser bloqueante para la gui'''
    cantidadComicsPorPagina = Column(Integer,nullable=False,default=18)
    '''guarda el id del ultimo volumen utilizado'''
    ultimoVolumeIdUtilizado = Column(String,default='')
    '''guarda el ultimo numero consultado'''
    ultimoNumeroConsultado = Column(Integer,default=0)

    # print(os.sep)
    # print(os.getcwd()[:os.getcwd().rfind(os.sep)])

    def __repr__(self):
        return "<Setup(directorioBaseImagene='%s')>" %(self.directorioBase)
