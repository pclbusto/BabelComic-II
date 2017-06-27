from tkinter import *
from tkinter import Tk, ttk
from Extras.Config import Config
from Extras.Scanner import BabelComicBookScanner
from Entidades.ComicBooks.ComicBook import ComicBook
import Entidades.Init
import threading



class BabelComicScannerGui():
    def __init__(self,master=None):
        ventanaPrincipal = Toplevel(master)
        ventanaPrincipal.title('Babel Comics  Scanner')
        panelPrincipal = ttk.Frame(ventanaPrincfireipal)
        panelBajo = ttk.Frame(ventanaPrincipal)
        panelPrincipal.grid(sticky=(W,E))
        panelBajo.grid()
        panelPrincipal.columnconfigure(0,weight=1)
        self.progresBar = ttk.Progressbar(panelPrincipal)
        self.progresBar.grid(sticky =(W,E),columnspan=2)
        self.progreso = ''
        self.progresBar.setvar(self.progreso)
        ttk.Label(panelPrincipal,text='Procesando archivo: ...').grid()
        ttk.Button(panelBajo,text= 'iniciar',command=self.initScanner).grid(column=1,row=0)
        ttk.Button(panelBajo,text= 'borrar registros de comics',command =  self.borrarComics).grid(column=0,row=0)
    def borrarComics(self):
        session = Entidades.Init.Session()
        session.query(ComicBook).delete()
        session.commit()
    def initScanner(self):
        self.config = Config()
        self.manager = BabelComicBookScanner(self.config.listaDirectorios, self.config.listaTipos)
        self.manager.iniciarScaneo()
        t = threading.Thread(target=self.testScanning)
        t.start()

    def testScanning(self):
        while (self.manager.scanerDir.isAlive()):
            self.progresBar['value']  = self.manager.porcentajeCompletado
if __name__ == "__main__":
    ##    babel = BabelComicMainGui()
    root = Tk()
    scanner = BabelComicScannerGui(root)
    root.mainloop()
