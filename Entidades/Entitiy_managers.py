from Entidades.Entity_manager import Entity_manager
from Entidades.Agrupado_Entidades import Arco_Argumental, Arcos_Argumentales_Comics_Reference
from Entidades.Agrupado_Entidades import Publisher, Volume
from Entidades import Init

class ArcosArgumentales(Entity_manager):
    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Arco_Argumental, id_externo=Arco_Argumental.id_arco_argumental_externo)
        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Arco_Argumental.nombre, 0)
        self.lista_opciones = {'Id': Arco_Argumental.id_arco_argumental, 'Arco Argumental': Arco_Argumental.nombre}

        self.status = 1
        self.entidad = Arco_Argumental()
        self.filtro = None
        self.set_order(Arco_Argumental.id_arco_argumental)
        self.direccion = 0

    def rm(self, Id):
        Entity_manager.rm(self)
        self.session.query(Arcos_Argumentales_Comics_Reference).filter(Arco_Argumental.id_arco_argumental==Id).delete()
        self.session.commit()

class Publishers(Entity_manager):

    def __init__(self, session = None, clase=Publisher):
        Entity_manager.__init__(self, session=session, clase=clase)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Publisher.id_publisher,0)
        self.lista_opciones = {'Id': Publisher.id_publisher, 'Editorial': Publisher.name}

        self.status = 1
        self.filtro = None
        self.order = None
        self.direccion = 0

class Volumens(Entity_manager):

    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Volume, id_externo=Volume.id_volume_externo)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Volume.nombre,0)
        self.lista_opciones = {'Id': Volume.id_volume, 'Volumen': Volume.nombre}

        self.status = 1
        self.entidad=Volume()
        self.filtro = None
        self.set_order(Volume.id_volume)
        self.direccion = 0

if (__name__=='__main__'):
    ArcosArgumentales().rm(55691)

    #print(arco.getCantidadTitulos())
