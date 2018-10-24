from sqlalchemy import Column, Integer, String, Float
import Entidades.Init
from sqlalchemy import Sequence


'''Esta clase representa la metadata del comic. 
'''
class Comicbooks_Info(Entidades.Init.Base):

    __tablename__='Comicbooks_Info'

    id_comicbooks_Info = Column(Integer, Sequence('comicbook_id_seq'), primary_key=True)
    id_comicbooks_Info_externo = Column(String,nullable=False,default='')
    titulo = Column(String,nullable=False,default='')
    id_volume = Column(String, nullable=False, default='')
    nombre_volumen = Column(String,nullable=False,default='')
    numero = Column(String,nullable=False,default='0')
    fechaTapa = Column(Integer,nullable=False,default=0)  # como no hay date en sql lite esto es la cantidad de dias desde 01-01-01
    id_arco_argumental = Column(String,nullable=False,default='') #id arco
    arcoArgumentalNumero = Column(Integer,nullable=False,default=0) #numero dentro del arco
    resumen = Column(String,nullable=False,default='')
    nota = Column(String,nullable=False,default='')
    rating = Column(Float,nullable=False,default=0.0)
    ratingExterno = Column(Float,nullable=False,default=0.0)

    id_publisher = Column(String,nullable=False,default='')
    api_detail_url = Column(String,nullable=False,default='')
    thumb_url  = Column(String,nullable=False,default='')
    '''Este campo se crea para ordenar los comics.
    Se cambia el numero que es de tipo int a string porque hay numeraciones comoc 616a de batman.
    El tema es que por ser string pierdo el orden entonces despues del 1 no viene el 2 si no 10.'''
    orden = Column(Integer,nullable=False,default=0 )


    def __repr__(self):
        # return "<Comicbooks(Id Volumen='%s'\n" \
        #        "Título='%s'\n" \
        #        "Path='%s'\n" \
        #        "arco id: '%s'\n" \
        #        "arco numero:'%s'\n" \
        #        "id Comic Vine:'%s'\n" \
        #        "Numero='%s'\n" \
        #        "id interno='%s'>" % (
        # self.volumeId,  self.titulo, self.path, self.arcoArgumentalId, self.arcoArgumentalNumero,self.comicVineId,self.numero,self.comicId)
        return "titulo={}-comic vine id={}".format(self.titulo, self.id_comicbooks_Info_externo)
    # ##        rarfile.UNRAR_TOOL = 'C:\\Program Files\\WinRAR'
