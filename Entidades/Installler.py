import os
from Entidades import Init

import Entidades.Setups.Setup
import Entidades.Setups.SetupTipoArchivo
import Entidades.Setups.SetupDirctorio
import Entidades.Setups.SetupVineKey
import Entidades.Setups.SetupVinekeysStatus
import Entidades.Publishers.Publisher
import Entidades.ComicBooks.ComicBook
import Entidades.Volumens.Volume
import Entidades.ComicBooks.ComicBookDetail
import Entidades.Volumens.ComicsInVolume
import Entidades.ComicBooks.ComicBookInfo

if __name__ == '__main__':
    Init.recreateTables()
    setup = Entidades.Setups.Setup.Setup()
    setup.directorioBase=os.getcwd()[:-10]
    session = Init.Session()
    session.add(setup)
    session.commit()
    Init.recreateTablesAll()



