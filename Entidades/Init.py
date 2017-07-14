from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
'''
el argument connect args check_same_thread en false sirve para poder hacer consultas en threads
y que no de error despues al usuarlo poque no se creo en el mismo thread.
'''
engine = create_engine('sqlite:///../BabelComic.db', echo=True, connect_args={'check_same_thread':False})
Base = declarative_base()
Session = sessionmaker(bind = engine)

def recreateTables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
