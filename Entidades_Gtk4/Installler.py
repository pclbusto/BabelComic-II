import os
from Entidades import Init
from Extras.Config import Config
import Entidades.Agrupado_Entidades

if __name__ == '__main__':
    Init.recreateTables()
    setup = Entidades.Agrupado_Entidades.Setup()
    setup.directorioBase=os.getcwd()[:-10]
    session = Init.Session()
    session.add(setup)
    session.commit()
    Init.recreateTablesAll()






