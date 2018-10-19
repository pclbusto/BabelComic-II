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
    ultimoNumeroConsultadoDesde = Column(Integer,default=0)
    ultimoNumeroConsultadoHasta = Column(Integer,default=0)
    anchoArbol = Column(Integer,default=100)
    '''Expresion regular para calcular donde esta el numeradoer en path del archivo'''
    expresionRegularNumero= Column(String,default='',nullable=False)

    def __repr__(self):
        return "<Setup(setupkey = '%s'\n" \
               "Cantidad Comics PorPagina = '%s'\n" \
               "Ultimo VolumeId Utilizado = '%s'\n" \
               "Ultimo Numero Consultado Desde= '%s'\n" \
               "Ultimo Numero Consultado Hasta= '%s'\n" \
               "Expresion Regular Numero= '%s'\n" \
               "Directorio Base Imagene='%s'\n)>" %(self.setupkey,
                                                  self.cantidadComicsPorPagina,
                                                  self.ultimoVolumeIdUtilizado,
                                                  self.ultimoNumeroConsultadoDesde,
                                                  self.ultimoNumeroConsultadoHasta,
                                                  self.expresionRegularNumero,
                                                  self.directorioBase)
