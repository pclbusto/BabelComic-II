from enum import Enum
from Entidades.Agrupado_Entidades import Publisher, Volume, Arco_Argumental
from Entidades import Init
from sqlalchemy import and_

class BabelComics_Manager():
    """
    Esta clase tiene que representar todo lo que la gui de babelComics_main permite hacer. La ideas es que todo pase
    por esta clase ahora para trabajar con la interfaz.
    """
    EDITORIAL = 0
    VOLUMEN = 1
    ARCO_ARGUMENTAL = 2

    def __init__(self):

        self.filtro = [Publisher.name.like("%{}%".format('')), Volume.nombre.like("%{}%".format('')), Arco_Argumental.nombre.like("%{}%".format(''))]

        self.lista_editoriales = []
        self.lista_volumenes = []
        self.lista_arcos_argumentales = []
        self.session = Init.Session()

        self.lista_paneles = [self.lista_editoriales, self.lista_volumenes, self.lista_arcos_argumentales]
        """Se usa esto porque no tenemos el mismo atributo en las tres entidad"""
        self.lista_campo_fitro = [Publisher.name, Volume.nombre, Arco_Argumental.nombre]
        self.titulos = ["Editorial", "Volumen", "Arco argumental"]
        """
        seccion activa me permite saber en pagina estamos parados
        """
        self.seccion_activa = 0
        self.cargar_arcos_argumentales()
        self.cargar_editoriales()
        self.cargar_volumenes()


    def get_titulo_actual(self):
        return self.titulos[self.seccion_activa]

    def next_seccion(self):
        self.seccion_activa = (self.seccion_activa+1) % len(self.titulos)

    def prev_seccion(self):
        self.seccion_activa = (self.seccion_activa-1) % len(self.titulos)

    def cargar_editoriales(self):
        self.lista_editoriales.clear()
        #print(self.filtro[self.seccion_activa])
        for elemento in self.session.query(Publisher).filter(self.filtro[self.seccion_activa]).order_by(Publisher.name).all():
        #for elemento in self.session.query(Publisher).filter(filtro).all():
            self.lista_editoriales.append([elemento.name, 0, elemento.id_publisher])

    def cargar_volumenes(self):
        self.lista_volumenes.clear()
        filtro0 = [elem for elem in self.lista_editoriales]
        print(filtro0)
        filtro  = [elem[2] for elem in self.lista_editoriales if elem[1] == 1]
        print(filtro)
        for elemento in self.session.query(Volume).filter(and_(self.filtro[self.seccion_activa])).order_by(Volume.nombre).all():
            self.lista_volumenes.append([elemento.nombre, 0, elemento.id_volume])

    def cargar_arcos_argumentales(self):
        self.lista_arcos_argumentales.clear()
        for elemento in self.session.query(Arco_Argumental).filter(self.filtro[self.seccion_activa]).order_by(Arco_Argumental.nombre).all():
            self.lista_arcos_argumentales.append([elemento.nombre, 0, elemento.id_arco_argumental])

    def get_lista_actual(self):
        return self.lista_paneles[self.seccion_activa]

    def marcar_para_filtrar(self, clave):
        for idx, elemento in enumerate(self.lista_paneles[self.seccion_activa]):
            if elemento[2] == clave:
                self.lista_paneles[self.seccion_activa][idx][1] = (self.lista_paneles[self.seccion_activa][idx][1]+1) % 2
        #self.recargar_seccion()

    def recargar_seccion(self):
        if self.seccion_activa == BabelComics_Manager.EDITORIAL:
            self.cargar_editoriales()
            self.cargar_volumenes()
        elif self.seccion_activa == BabelComics_Manager.VOLUMEN:
            self.cargar_volumenes()
        elif self.seccion_activa == BabelComics_Manager.ARCO_ARGUMENTAL:
            self.cargar_arcos_argumentales()

    def set_filtro(self, filtro):
        if filtro is None:
            print("ACA")
            self.filtro[self.seccion_activa] = None
            return
        if self.seccion_activa == BabelComics_Manager.EDITORIAL:
            print("EDITO")
            self.filtro[self.seccion_activa] = Publisher.name.like("%{}%".format(filtro))
        elif self.seccion_activa == BabelComics_Manager.VOLUMEN:
            self.filtro[self.seccion_activa] = Volume.nombre.like("%{}%".format(filtro))
        elif self.seccion_activa == BabelComics_Manager.ARCO_ARGUMENTAL:
            self.filtro[self.seccion_activa] = Arco_Argumental.nombre.like("%{}%".format(filtro))
        self.recargar_seccion()

if (__name__=='__main__'):
    manager = BabelComics_Manager()
    #manager.next_seccion()
    #manager.set_filtro("Bat")
    print(manager.get_lista_actual())
