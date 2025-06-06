
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
        self.offset = 0
        self.atributo_clave = None
        directorioBase  = self.session.query(Setup).first().directorioBase
        self.pahThumnails = directorioBase + os.sep + 'images' + os.sep + 'logo publisher'+ os.path.sep
        self.status = Entity_manager.CTE_OK
        self.lista_estados_mansajes={0:"OK",
                                     1:"Hay cambios pendientes",
                                     2:"Entidad Nula."}
        self.consulta = self.session.query(self.clase)

    def get_mensaje(self, clave):
        return self.lista_estados_mansajes[clave]

    def save(self):
        if self.entidad is not None:
            self.session.add(self.entidad)
            self.session.commit()
            # self.entidad = self.clase()
            self.status = Entity_manager.CTE_OK

    def rm(self):
        if self.entidad is not None:
            self.session.delete(self.entidad)
            self.session.commit()
            self.status = Entity_manager.CTE_OK
            print("Eliminado")
        else:
            self.status = Entity_manager.CTE_ENTIDAD_NULA


    def rmAll(self):
        self.session.query(self.clase).delete()
        self.session.commit()
        self.new_record()

    def rm_by_filter(self):
        print(self.consulta)
        if self.consulta is not None:
            print("finalmente")
            self.consulta.delete()
            self.session.commit()
            self.new_record()

    def get(self, id_entidad):
        if not self.hay_cambios_pendientes():
            # Vamos a calcular el offset para poder navegar de forma correcta
            self.entidad = self.session.query(self.clase).get(id_entidad)
        else:
            self.status = Entity_manager.CTE_CAMBIOS_PENDIENTES
        return self.entidad

    def hay_cambios_pendientes(self):

        if self.entidad is not None and self.session.is_modified(self.entidad):
            return True
        else:
            return False

    def new_record(self):
        if not self.hay_cambios_pendientes():
            self.entidad = self.clase()


    def get_count(self):
        return(self._get_consulta().count())

    def set_order(self, campo, direccion=0):
        self.order = campo
        param = str(campo)
        self.campo_str = param[param.index(".")+1:]
        self.direccion=direccion

    def set_filtro(self, filtro):
        if self.consulta is None:
            self.consulta = self.session.query(self.clase).filter(filtro)
        else:
            self.consulta = self.consulta.filter(filtro)

    def clear_filtro(self):
        self.consulta = self.session.query(self.clase)

    def getList(self):
        consulta = self._get_consulta()
        return consulta.all()

    def get_by_id_externo(self, id_externo):
        return self.session.query(self.clase).filter(self.id_externo == id_externo).first()

    def _get_consulta(self):
        consulta = self.consulta
        if self.order is not None:
            if self.direccion == 0:
                consulta = consulta.order_by(self.order)
            else:
                consulta = consulta.order_by(self.order.desc())
        return consulta

    def getNext(self):
        #self.get_count()
        if not self.hay_cambios_pendientes():

            if self.entidad is None:
                self.entidad = self.getLast()
            else:

                if self.offset < self.get_count()-1:
                    self.offset += 1
                consulta = self._get_consulta()
                entidad = consulta.filter().offset(self.offset).first()
                print( self.offset)
                print(entidad)
                if entidad is not None:
                    self.entidad = entidad
        else:
            self.status=Entity_manager.CTE_CAMBIOS_PENDIENTES
        # print(self.entidad)
        return self.entidad

    def getPrev(self):
        self.get_count()
        if not self.hay_cambios_pendientes():
            if self.entidad is None:
                self.entidad = self.getFirst()
            else:
                if self.offset > 0:
                    self.offset -= 1
                consulta = self._get_consulta()
                entidad = consulta.filter().offset(self.offset).first()
                if entidad is not None:
                    self.entidad = entidad
        else:
            self.status = Entity_manager.CTE_CAMBIOS_PENDIENTES
        return self.entidad

    def getFirst(self):
        if not self.hay_cambios_pendientes():
            self.offset = 0
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            self.entidad = self._get_consulta().first()
            print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBb")
        else:
            self.status = Entity_manager.CTE_CAMBIOS_PENDIENTES
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


