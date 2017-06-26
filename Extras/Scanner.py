from Entidades.ComicBooks import ComicBook
from pathlib import Path
import threading
import Entidades.Init
import Extras.Config


class BabelComicBookScanner():
    def __init__(self, listaDirectorios, listaTipos):
        self.listaDirectorios = listaDirectorios
        self.listaTipos = listaTipos
        self.porcentajeCompletado = 0.0
        self.scanerDir = threading.Thread(target=self.scanearDirtorios)
        self.createThumnails = threading.Thread(target=self.crearThumbnails)
        self.comics = []

    def crearThumbnails(self):
        # comics = KivyComicBooks()
        print("iniciando creacion de thumnails")
        # if not os.path.exists("thumnails"):
        #     os.mkdir("thumnails")
        # lista = comics.list(('%Batman%',), 'path like ?')
        # cantidadAProcesar = comics.cantidadRegistrosConsulta
        # print("cantidad a procesasr :{}".format(comics.getCantidadPaginas()))
        # cantidadProcesada = 0
        # # for i in range(0,comics.getCantidadPaginas()+1):
        # comics.goto(0)
        # lista = comics.list(('%Batman%',), 'path like ?')
        # for comicbook in lista:
        #     self.porcentajeCompletado = 100 * (cantidadProcesada / cantidadAProcesar)
        #     if not os.path.exists("thumnails\\" + str(comicbook.idFila) + ".jpg"):
        #         cover = comicbook.getImagePagePIL()
        #         cover.thumbnail((120,240))
        #         cover.save("thumnails\\" + str(comicbook.idFila)+".jpg")
        #     print(comicbook.path)
        #     cantidadProcesada += 1
        # print("finalizando creacion de thumnails")


    def countfilesToProces(self):
        cantidad = 0
        listaDirectotiosLocal = [x for x in self.listaDirectorios]
        while (len(listaDirectotiosLocal) > 0):
            valor = listaDirectotiosLocal[0]
            p = Path(listaDirectotiosLocal[0])
            lst = [x for x in p.iterdir() if (x.is_file() and x.name[-3:] in self.listaTipos)]
            cantidad += len(lst)
            dirs = [x for x in p.iterdir() if (x.is_dir())]
            for dir in dirs:
                listaDirectotiosLocal.append(dir)
            listaDirectotiosLocal.remove(valor)
        return (cantidad)

    def scanearDirtorios(self):
        cantidadAProcesar = self.countfilesToProces() * 2
        cantidadProcesada = 0
        while (len(self.listaDirectorios) > 0):
            valor = self.listaDirectorios[0]
            p = Path(self.listaDirectorios[0])
            lst = [x for x in p.iterdir() if (x.is_file() and x.name[-3:] in self.listaTipos)]
            dirs = [x for x in p.iterdir() if (x.is_dir())]
            for item in lst:
                comic = ComicBook.ComicBook()
                comic.path = str(item)
                print(comic.path)
                self.comics.append(comic)
                cantidadProcesada += 1
            for dir in dirs:
                self.listaDirectorios.append(dir)
            self.listaDirectorios.remove(valor)
            self.porcentajeCompletado = 100 * (cantidadProcesada / cantidadAProcesar)
        session = Entidades.Init.Session()
        for item in self.comics:
            session.add(item)
            cantidadProcesada += 1
            self.porcentajeCompletado = 100 * (cantidadProcesada / cantidadAProcesar)
        session.commit()


    def iniciarScaneo(self):
        self.scanerDir.start()

    def iniciarThumnails(self):
        self.createThumnails.start()

def testScanning():
    while (manager.scanerDir.isAlive()):
        print(manager.porcentajeCompletado)
    print(manager.porcentajeCompletado)


if __name__ == "__main__":
    config = Extras.Config.Config()
    manager = BabelComicBookScanner(config.listaDirectorios, config.listaTipos)
    manager.iniciarScaneo()
    t = threading.Thread(target=testScanning)
    t.start()