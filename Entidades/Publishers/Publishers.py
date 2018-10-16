
from Entidades.Publishers.Publisher import Publisher
from Entidades import Init

import Extras.Config as BC
import Extras.ComicVineSearcher as CV
import shutil
import os


class Publishers:

    def __init__(self, session = None):
        if session is not None:
            self.session = session
        else:
            self.session = Init.Session()

        self.status = 1
        self.listaComicVineSearch = []
        self.currentKeyName='id'
        self.currentKeyValue=''
        self.publisher=Publisher()
        self.filtro = None
        self.order = None

    def save(self):
        if self.publisher is not None:
            print(self.publisher)
            self.session.add(self.publisher)
            self.session.commit()
            self.publisher = Publisher()
        '''copiamos el logo desde el dir temp al de logos. el temp tiene mas logos
        de lo que he guardados'''
        # if self.publisher.localLogoImagePath is None:
        #     return
        # file_name = self.publisher.logoImagePath.split('/')[-1]
        # file_name_no_ext = (file_name[:-4])
        # if os.path.exists(BC.BabelComicBookManagerConfig().getPublisherTempLogoPath() + file_name_no_ext + ".jpg"):
        #     shutil.copyfile(BC.BabelComicBookManagerConfig().getPublisherTempLogoPath() + file_name_no_ext + ".jpg",
        #                     BC.BabelComicBookManagerConfig().getPublisherLogoPath() + file_name_no_ext + ".jpg")
    #
    def rm(self):
        if self.publisher is not None:
            self.session.delete(self.publisher)
        self.session.commit()

    def rmAll(self):
        self.session.query(Publisher).delete()
        self.session.commit()

    def get(self,Id):
        if len(self.session.dirty):
            return "cambios pendientes."
        else:
            self.publisher = self.session(Publisher).query(Publisher).get(Id)
        return self.publisher

    def tiene_cambio(self):
        if len(self.session.dirty()) > 0:
            return True
        else:
            return False

    def new_record(self):
        if len(self.session.dirty())>0:
            return "hay cambios pendientes. No se puede crear un nuevo registro."
        self.publisher=Publisher()

    def getSize(self):
        return(self.session.query(Publisher).count())

    def set_order(self,campo):
        self.order = campo
        param = str(campo)
        self.campo_str = getattr(self.publisher, param[param.index(".")+1:])

    def set_filtro(self,filtro):
        self.filtro = filtro

    def getList(self):
        consulta = self.session.query(Publisher)
        if self.filtro is not None:
            consulta=consulta.filter(self.filtro)
        if self.order is not None:
            consulta=consulta.order_by(self.order)
        return consulta.all()

    def getNext(self):
        publisher = None
        if self.publisher is None:
            self.publisher = self.getLast()
        else:
            # last=Init.Session().query(Publisher).get(self.currentKeyValue)
            self.publisher = self.session.query(Publisher).filter(self.order>getattr(self.publisher,self.campo_str)).order_by(self.order).first()

            # .filter(self.order)> getattr(self.publisher,str(self.order))) .order_by(Publisher.id_publisher.asc()).first()
            # print(publisher)
            # if publisher == None:
            #     self.publisher = last
            # else:
            #     self.currentKeyValue = publisher.id_publisher
        return self.publisher

    def getPrev(self):
        publisher = None
        if self.currentKeyValue == '':
            publisher = self.getFirst()
        else:
            first = Init.Session().query(Publisher).get(self.currentKeyValue)
            publisher = Init.Session().query(Publisher).filter(Publisher.id_publisher < self.currentKeyValue).order_by(Publisher.id_publisher.desc()).first()
            print(publisher)
            if publisher == None:
                publisher = first
            else:
                self.currentKeyValue = publisher.id_publisher
        return publisher

    def getFirst(self):
        publisher = self.session.query(Publisher).order_by(self.order).first()
        if publisher is not None:
            self.publisher = publisher
        return self.publisher

    def getLast(self):
        publisher = self.session.query(Publisher).order_by(self.order.desc()).first()
        if publisher is not None:
            self.publisher = publisher
        return self.publisher


# if __name__ == "__main__":
#     cadena = str(Publisher.name)
#     print(cadena)

    # publishers.searchInComicVine("Marvel")
    # publishers.rmAll()
    # publisher = Publisher()


    # for publisher in publishers.listaComicVineSearch:
    #     print(publisher.name,publisher.id, publisher.siteDetailUrl)
