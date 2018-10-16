

from Entidades import Init


class Entity_manager:

    def __init__(self, session = None, clase=None, clave=None):
        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.clase = clase
        self.entidad = self.clase()

        self.filtro = None
        self.order = None
        self.direccion = 0

    def save(self):
        if self.entidad is not None:
            print(self.entidad)
            self.session.add(self.entidad)
            self.session.commit()
            self.entidad = self.clase()

    def rm(self):
        if self.entidad is not None:
            self.session.delete(self.entidad)
        self.session.commit()

    def rmAll(self):
        self.session.query(self.clase).delete()
        self.session.commit()

    def get(self,Id):
        if len(self.session.dirty)>0:
            return "cambios pendientes."
        else:
            print(Id)
            self.entidad = self.session.query(self.clase).get(Id)
        return self.entidad

    def tiene_cambio(self):
        if len(self.session.dirty()) > 0:
            return True
        else:
            return False

    def new_record(self):
        if len(self.session.dirty())>0:
            return "hay cambios pendientes. No se puede crear un nuevo registro."
        self.entidad=self.clase()

    def getSize(self):
        return(self.session.query(self.clase()).count())

    def set_order(self,campo, direccion):
        self.order = campo
        param = str(campo)
        self.campo_str = param[param.index(".")+1:]
        self.direccion=direccion

    def set_filtro(self,filtro):
        self.filtro = filtro

    def getList(self):
        consulta = self._get_consulta()
        return consulta.all()

    def _get_consulta(self):
        consulta = self.session.query(self.clase)
        if self.filtro is not None:
            consulta = consulta.filter(self.filtro)
        if self.order is not None:
            if self.direccion==0:
                consulta = consulta.order_by(self.order)
            else:
                consulta = consulta.order_by(self.order.desc())
        return consulta

    def getNext(self):
        if self.entidad is None:
            self.entidad = self.getLast()
        else:
            consulta = self._get_consulta()
            entidad = consulta.filter(
                self.order>getattr(self.entidad,self.campo_str)).first()
            if entidad is not None:
                self.entidad=entidad
        return self.entidad

    def getPrev(self):
        if self.entidad is None:
            self.entidad = self.getLast()
        else:
            entidad = self.session.query(self.clase()).filter(
                self.order < getattr(self.entidad, self.campo_str)).order_by(self.order).first()
            if entidad is not None:
                self.entidad = entidad
        return self.entidad

    def getFirst(self):
        entidad = self._get_consulta().first()
        if entidad is not None:
            self.entidad = entidad
        return self.entidad

    def getLast(self):
        self.set_order(self.order, 1)
        entidad = self._get_consulta().first()
        self.set_order(self.order, 0)
        if entidad is not None:
            self.entidad = entidad
        return self.entidad


