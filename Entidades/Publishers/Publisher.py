from sqlalchemy import Column, Integer, String
import Entidades.Init


class Publisher(Entidades.Init.Base):
    __tablename__='Publishers'
    id_publisher = Column(String, primary_key=True)
    name = Column(String)
    deck = Column(String)
    description = Column(String)
    logoImagePath  = Column(String)
    localLogoImagePath = Column(String)
    siteDetailUrl = Column(String)

    def __repr__(self):
        return "<Publisher(id_publisher='%s',name='%s')>" %(self.id_publisher, self.name)

