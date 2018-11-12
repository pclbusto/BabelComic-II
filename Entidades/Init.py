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
# print(pathdb )
engine = create_engine('sqlite:///'+pathdb, echo=False, connect_args={'check_same_thread':False})
Base = declarative_base()
Session = sessionmaker(bind = engine)

def recreateTables():

    Base.metadata.drop_all(engine)
    lista = []
    for k,value in Base.metadata.tables.items():
        if value.name == 'setups':
            lista.append(value)
    Base.metadata.create_all(engine, tables=lista)

def recreateTables2():
    lista = []
    for k,value in Base.metadata.tables.items():
        lista.append(value)
    Base.metadata.create_all(engine, tables=lista[1:])


def recreateTablesAll():
    Base.metadata.create_all(engine)

