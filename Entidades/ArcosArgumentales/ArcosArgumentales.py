from Entidades.Entity_manager import Entity_manager
from Entidades.ArcosArgumentales.ArcoArgumental import ArcoArgumental
from Entidades.ArcosArgumentales.ArcosArgumentalesComics import ArcosArgumentalesComics
from Entidades import Init

class ArcosArgumentales():
    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=ArcoArgumental, id_externo=ArcoArgumental.id_arco_argumental_externo)
        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(ArcoArgumental.nombre, 0)
        self.lista_opciones = {'Id': ArcoArgumental.id_arco_argumental, 'Volumen': ArcoArgumental.nombre}

        self.status = 1
        self.entidad = ArcoArgumental()
        self.filtro = None
        self.set_order(ArcoArgumental.id_arco_argumental)
        self.direccion = 0

    def rm(self, Id):
        Entity_manager.rm()
        Entity_manager.session.query(ArcosArgumentalesComics.
        cursor.execute('''DELETE FROM ArcosArgumentales WHERE id=?''',(Id,))
        cursor.execute('''DELETE FROM ArcosArgumentalesComics WHERE idArco = ?''',(Id,))
        self.conexion.commit()


if (__name__=='__main__'):
    ArcosArgumentales().rm(55691)

    #print(arco.getCantidadTitulos())
