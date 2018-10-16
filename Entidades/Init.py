from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
'''
el argument connect args check_same_thread en false sirve para poder hacer consultas en threads
y que no de error despues al usuarlo poque no se creo en el mismo thread.
'''
pathdb = os.path.abspath("..")
pathdb = os.path.join(pathdb,"BabelComic.db")
engine = create_engine('sqlite:///'+pathdb, echo=False, connect_args={'check_same_thread':False})
Base = declarative_base()
Session = sessionmaker(bind = engine)

def recreateTables():

    Base.metadata.drop_all(engine)
    lista = []
    for k,value in Base.metadata.tables.items():
        lista.append(value)
    Base.metadata.create_all(engine, tables=lista[0:1])

def recreateTables2():
    lista = []
    for k,value in Base.metadata.tables.items():
        lista.append(value)
    Base.metadata.create_all(engine, tables=lista[1:])


def recreateTablesAll():
    Base.metadata.create_all(engine)



# class Base():
#     def __init__(self):
#         self.engine = create_engine('sqlite:///' + os.path.abspath(".") + 'BabelComic.db', echo=True,
#                                     connect_args={'check_same_thread': False})
#         self.Base = declarative_base()
#         self.Session = sessionmaker(bind=self.engine)
#
#     def recreateTables(self, directorioBase=None):
#         self.Base.metadata.drop_all(self.engine)
#         lista = []
#         for k, value in self.Base.metadata.tables.items():
#             lista.append(value)
#         self.Base.metadata.create_all(self.engine, tables=lista[0:1])
#
#     def recreateTables2(self, directorioBase=None):
#         lista = []
#         for k, value in self.Base.metadata.tables.items():
#             lista.append(value)
#         self.Base.metadata.create_all(self.engine, tables=lista[1:])
#
#     def recreateTablesAll(self, directorioBase=None):
#         self.Base.metadata.create_all(self.engine)
#
