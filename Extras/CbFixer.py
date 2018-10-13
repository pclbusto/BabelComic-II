import zipfile
import rarfile
import os
import shutil

class CbFixer():
    # todo convertir de cbr a cbz
    def __init__(self, listaArchivos):
        for nombreArchivo in listaArchivos:
            extension = nombreArchivo[-3:]
            '''asumo que dio errror entonces trato con el opuesto zip a rar y rar a zip'''
            if (extension.lower() == 'cbz'):
                self.cbFile = rarfile.RarFile(nombreArchivo, 'r')
                self.paginas = [x.filename for x in self.cbFile.infolist()]

            elif (extension.lower() == 'cbr'):
                if not os.path.exists("comic"):
                    os.mkdir("comic")
                self.cbFile = zipfile.ZipFile(nombreArchivo, 'r')
                self.cbFile.extractall(path='comic')
                self.cbFile.close()

                shutil.rmtree('comic')
if __name__ == "__main__":
    lista = ["E:\Tmp\Action Comics 420.cbr"]
    cbFixer = CbFixer(listaArchivos=lista)


