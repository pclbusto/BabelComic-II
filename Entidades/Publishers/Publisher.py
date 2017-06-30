from sqlalchemy import Column, Integer, String
import Entidades.Init


class Publisher(Entidades.Init.Base):
    __tablename__='Publishers'
    id_publisher = Column(String, primary_key=True)
    name = Column(String,nullable=False,default='')
    deck = Column(String,nullable=False,default='')
    description = Column(String,nullable=False,default='')
    logoImagePath  = Column(String,nullable=False,default='')
    localLogoImagePath = Column(String,nullable=False,default='')
    siteDetailUrl = Column(String,nullable=False,default='')


    def __repr__(self):
        return "<Publisher(id_publisher='%s',name='%s')>" %(self.id_publisher, self.name)

