from tkinter import *
from tkinter import Tk, ttk
from tkinter import filedialog
import Extras.Config



class ConfigGui(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.babelComicConfig = Extras.Config.Config()

        # agregado directorios
        self.frameDirectorios = ttk.LabelFrame(self)
        self.frameDirectorios.columnconfigure(0, weight=1)
        self.frameDirectorios.rowconfigure(1, weight=1)
        self.frameDirectorios.grid(sticky=(N, S, W, E), column=0, row=0)

        ttk.Label(self.frameDirectorios, text='Lista de Directorios').grid(column=0, row=0, sticky=(W, E))
        ttk.Button(self.frameDirectorios, text='+', width=1, command=self.openDirectoryChooser).grid(column=1, row=1,
                                                                                                     sticky=N)
        ttk.Button(self.frameDirectorios, width=1, text='-', command=self.delDirectorio).grid(column=1, row=2, sticky=N)
        self.listaDirectorios = Listbox(self.frameDirectorios, width = 45)
        self.listaDirectorios.grid(column=0, row=1, rowspan=2, sticky=(N, S, W, E))
        # agregado vinekeys
        self.frameClaves = ttk.LabelFrame(self)
        self.frameClaves.columnconfigure(0, weight=1)
        self.frameClaves.rowconfigure(1, weight=1)
        ttk.Label(self.frameClaves, text='Lista de Claves').grid(column=0, row=0, sticky=(W))
        ttk.Button(self.frameClaves, text='+', width=1, command=self.openClaveEntry).grid(column=1, row=1, sticky=N)
        ttk.Button(self.frameClaves, width=1, text='-', command=self.delClave).grid(column=1, row=2, sticky=N)
        self.listaClaves = Listbox(self.frameClaves,width = 45)
        # campo extensiones para usar en la ventana
        self.clave = StringVar()
        self.claveEntry = None

        self.extensionVar = StringVar()
        # Panel para que los campos de texto no se vayan a la derecha
        self.panelinferior = ttk.Frame(self)
        self.columnconfigure(1,weight=4)
        self.panelinferior.grid(column=0,row=1,sticky=W+E+S+N,columnspan=2)
        Label(self.panelinferior, text='Lista de extensiones soportadas').grid(column=0, row=0, sticky=(W))
        self.listaExtensiones = ttk.Entry(self.panelinferior, textvariable=self.extensionVar)
        self.listaExtensiones.grid(column=1, row=0, sticky=W+E,columnspan=2)

        #directorios base
        ttk.Label(self.panelinferior, text='Directorio Base').grid(column=0, row=1, sticky=(W))
        self.directorioVar = StringVar()
        self.entradaDirectorioBase = ttk.Entry(self.panelinferior, textvariable=self.directorioVar)
        self.entradaDirectorioBase.grid(column=1,row=1, sticky=(E),columnspan=2)
        self.botonDirecotrioBase = ttk.Button(self.panelinferior, text='...', command=self.openBaseDirectoryChooser)
        self.botonDirecotrioBase.grid(column=6, row=1, sticky=(W))

        for directorio in self.babelComicConfig.listaDirectorios:
            self.listaDirectorios.insert(END, directorio)

        for claves in self.babelComicConfig.listaClaves:
            self.listaClaves.insert(END, claves)

        for extension in self.babelComicConfig.listaTipos:
            self.extensionVar.set(self.extensionVar.get() + ',' + extension)
        self.extensionVar.set(self.extensionVar.get()[1:])

        if self.babelComicConfig.setup is not None:
            self.entradaDirectorioBase.insert(0, self.babelComicConfig.setup.directorioBase)
            print("NADA")
        ttk.Button(self, text='Guardar', command=self.save).grid(column=1, row=4, sticky=E)
        self.statusText = StringVar()
        self.statusbar = ttk.Label(self, text='Status:', textvariable=self.statusText).grid(column=0, row=4,
                                                                                            columnspan=2, sticky=W)

        self.listaClaves.grid(column=0, row=1, rowspan=2, sticky=(N, S, W, E))
        #self.listaClaves.config(width = 45)
        self.frameClaves.grid(sticky=(N, S, W, E), column=1, row=0)

    def openDirectoryChooser(self):
        salida = filedialog.askdirectory(title='Selección de Directorios de Comics')
        if salida:
            self.listaDirectorios.insert(END, salida)

    def openBaseDirectoryChooser(self):
        salida = filedialog.askdirectory(title='Selección de Directorios de Imagenes')
        if salida:
            self.entradaDirectorioBase.delete(0,END)
            self.entradaDirectorioBase.insert(0, salida)
    def delDirectorio(self):
        if (self.listaDirectorios.curselection()):
            self.listaDirectorios.delete(self.listaDirectorios.curselection())

    def save(self):
        directorios = [item for item in self.listaDirectorios.get(0, self.listaDirectorios.size())]
        claves = [item for item in self.listaClaves.get(0, END)]
        self.babelComicConfig.setListaDirectorios(directorios)
        self.babelComicConfig.setListaTipos(self.extensionVar.get().split(','))
        self.babelComicConfig.setListaClaves(claves)
        self.babelComicConfig.setConfig(self.entradaDirectorioBase.get())
        self.statusText.set('Status: Gurdado exitosamente')

    def openClaveEntry(self):
        self.claveEntry = Toplevel()
        ttk.Label(self.claveEntry, text='Clave: ').grid(column=0, row=0, sticky=(W, E))
        ttk.Entry(self.claveEntry, textvariable=self.clave).grid(row=0, column=1, sticky=(W, E))
        ttk.Button(self.claveEntry, text='Guardar', command=self.addClave).grid(column=2, row=0, sticky=E)

    def addClave(self):
        self.listaClaves.insert(END, self.clave.get())
        self.claveEntry.destroy()
        self.clave.set('')

    def delClave(self):
        if (self.listaClaves.curselection()):
            self.listaClaves.delete(self.listaClaves.curselection())


if (__name__ == '__main__'):
    root = Tk()
    config = ConfigGui(root)
    config.grid(sticky=(N, S, W, E))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.grid()
    root.mainloop()
    ##frame = ttk.LabelFrame(root)
    ##keyEntry =  Toplevel()
    ##keyEntry.destroy()

