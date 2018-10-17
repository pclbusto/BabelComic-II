
from Entidades.Volumens.Volume import Volume
from Entidades.Entity_manager import Entity_manager
from Entidades import Init



class Volumens(Entity_manager):

    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Volume)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Volume.nombre,0)
        self.lista_opciones = {'Id': Volume.id_volumen, 'Volumen': Volume.nombre}

        self.status = 1
        self.entidad=Volume()
        self.filtro = None
        self.order = None
        self.direccion = 0


