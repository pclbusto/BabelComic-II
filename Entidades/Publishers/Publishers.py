
from Entidades.Publishers.Publisher import Publisher
from Entidades.Entity_manager import Entity_manager
from Entidades import Init



class Publishers(Entity_manager):

    def __init__(self, session = None):
        Entity_manager.__init__(self, session=session, clase=Publisher)

        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.set_order(Publisher.id_publisher,0)
        self.lista_opciones = {'Id': Publisher.id_publisher, 'Editorial': Publisher.name}

        self.status = 1
        self.listaComicVineSearch = []
        self.currentKeyName='id'
        self.currentKeyValue=''
        self.publisher=Publisher()
        self.filtro = None
        self.order = None
        self.direccion = 0


