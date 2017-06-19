from pexpect.expect import searcher_re
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///../BabelComic.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind = engine)

def recreateTables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
