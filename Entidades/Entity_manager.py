
import os
from Entidades import Init
from Entidades.Agrupado_Entidades import Setup


class Entity_manager:

    CTE_OK = 0
    CTE_CAMBIOS_PENDIENTES = 1
    CTE_ENTIDAD_NULA = 2
    ORDER_ASC=0
    ORDER_DESC=1


    def __init__(self, session = None, clase=None):
        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.clase = clase
        self.entidad = self.clase()

        self.filtro = None
        self.order = None
        self.direccion = 0
        self.offset=0
        directorioBase  = self.session.query(Setup).first().directorioBase
        self.pahThumnails = directorioBase + os.sep + 'images' + os.sep + 'logo publisher'+ os.path.sep
        self.status = Entity_manager.CTE_OK
        self.lista_estados_mansajes={0:"OK",
                                     1:"Hay cambios pendientes",
                                     2:"Entidad Nula."}

    def get_mensaje(self, clave):
        return self.lista_estados_mansajes[clave]

    def save(self):
        if self.entidad is not None:
            self.session.add(self.entidad)
            self.session.commit()
            self.entidad = self.clase()
            self.status = Entity_manager.CTE_OK

    def rm(self):
        if self.entidad is not None:
            self.session.delete(self.entidad)
            self.session.commit()
            self.status = Entity_manager.CTE_OK
        else:
            self.status = Entity_manager.CTE_ENTIDAD_NULA


    def rmAll(self):
        self.session.query(self.clase).delete()
        self.session.commit()
        self.new_record()

    def get(self,Id):
        if not self.hay_cambios_pendientes():
            print("ID: {}".format(Id))
            self.entidad = self.session.query(self.clase).get(Id)
        else:
            self.status = Entity_manager.CTE_CAMBIOS_PENDIENTES
        return self.entidad

    def hay_cambios_pendientes(self):
        if self.session.is_modified(self.entidad):
            return True
        else:
            return False

    def new_record(self):
        if not self.hay_cambios_pendientes():
            self.entidad=self.clase()


    def get_count(self):
        return(self._get_consulta().count())

    def set_order(self,campo, direccion=0):
        self.order = campo
        param = str(campo)
        self.campo_str = param[param.index(".")+1:]
        self.direccion=direccion

    def set_filtro(self,filtro):
        self.filtro = filtro

    def getList(self):
        consulta = self._get_consulta()
        return consulta.all()

    def get_by_id_externo(self, id_externo):
        return self.session.query(self.clase).filter(self.id_externo==id_externo).first()

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
        if not self.hay_cambios_pendientes():
            if self.entidad is None:
                self.entidad = self.getLast()
            else:
                self.offset += 1
                consulta = self._get_consulta()
                # entidad = consulta.filter(
                #     self.order>getattr(self.entidad,self.campo_str)).first()
                entidad = consulta.filter().offset(self.offset).first()
                if entidad is not None:
                    self.entidad=entidad
        else:
            self.status=Entity_manager.CTE_CAMBIOS_PENDIENTES
        # print(self.entidad)
        return self.entidad

    def getPrev(self):
        if not self.hay_cambios_pendientes():
            if self.entidad is None:
                self.entidad = self.getFirst()
            else:
                self.offset -= 1
                # entidad = self.session.query(self.clase).filter(
                #     self.order < getattr(self.entidad, self.campo_str)).order_by(self.order).first()
                consulta = self._get_consulta()
                # print(consulta)
                entidad = consulta.filter().offset(self.offset).first()
                if entidad is not None:
                    self.entidad = entidad
        else:
            self.status=Entity_manager.CTE_CAMBIOS_PENDIENTES
        return self.entidad

    def getFirst(self):
        if not self.hay_cambios_pendientes():
            self.offset = 0
            self.entidad = self._get_consulta().first()
        else:
            self.status=Entity_manager.CTE_CAMBIOS_PENDIENTES
        return self.entidad

    def getLast(self):
        if not self.hay_cambios_pendientes():
            self.set_order(self.order, 1)
            self.entidad = self._get_consulta().first()
            self.set_order(self.order, 0)
            self.offset = self._get_consulta().count()-1
        else:
            self.status=Entity_manager.CTE_CAMBIOS_PENDIENTES
        return self.entidad


