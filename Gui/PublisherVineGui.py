from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos
from Entidades.Publishers import Publishers
from  Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
from PIL import Image, ImageTk
import Entidades.Init
from Entidades.Publishers.Publisher import Publisher

class PublisherVineGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)

        config = Config()

        self.comicVineSearcher = ComicVineSearcher(config.getClave('publishers'))
        self.comicVineSearcher.setEntidad("publishers")

        self.labelId = Label(self, text="Nombre Editorial: ")
        self.labelId.grid(row=0,column=0, sticky=W ,padx=5,pady=5)
        self.entradaNombreEditorial = Entry(self, width=50)

        self.varID=StringVar()
        self.entradaNombreEditorial.grid(row=0,column=1, sticky=W + E,padx=5,pady=5,columnspan=2 )
        self.botonLookupPublisher=Button(self, command=self.buscar)
        self.botonLookupPublisher.grid(row=0,column=3)
        self.pilImagenLookup=Iconos.Iconos.pilImagenLookup
        self.imageLookup = PIL.ImageTk.PhotoImage(self.pilImagenLookup)
        self.botonLookupPublisher.config(image=self.imageLookup)
        self.labelImagen = Label(self, text="logo edtorial")
        self.coverSize = (150,150)
        self.labelImagen.grid(column=4,row=1)


        ##config grilla series
        self.panelGrilla = Frame(self)
        self.panelGrilla.grid(column=0, row=1,  columnspan=3, sticky=(N, S, E, W), padx=5)

        self.grillaPublishers = ttk.Treeview(self.panelGrilla, columns=('Id', 'Nombre'),displaycolumns=('Id', 'Nombre'))
        self.grillaPublishers.grid(column=0, row=0,  columnspan=3, sticky=(N, S, E, W))
        self.grillaPublishers.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()

        scrollGrid = ttk.Scrollbar(self.panelGrilla, orient=VERTICAL, command=self.grillaPublishers.yview)
        scrollGrid.grid(column=3, row=0, sticky=(N, S))

        self.grillaPublishers.configure(yscrollcommand=scrollGrid.set)

        self.grillaPublishers.heading('Id', text='Id')
        self.grillaPublishers.heading('Nombre', text='Nombre')
        self.grillaPublishers.config(show='headings')  # tree, headings

        self.botonLookupPublisher = Button(self,text="agregar",command = self.agregarEditorial)
        self.botonLookupPublisher.grid(row=2, column=3, pady=3, sticky=(E))

    def agregarEditorial(self):
        session = Entidades.Init.Session()
        session.add(self.publisher)
        session.commit()

    def buscar(self):
        if (self.entradaNombreEditorial.get()!=''):
            self.comicVineSearcher.clearFilter()
            self.comicVineSearcher.addFilter("name:"+self.entradaNombreEditorial.get())
            self.comicVineSearcher.vineSearch(0)
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)

    def itemClicked(self, event):
        if (self.grillaPublishers.selection()):
            seleccion = self.grillaPublishers.selection()
            self.publisher = self.comicVineSearcher.listaBusquedaVine[self.grillaPublishers.index(seleccion[0])]
            self.grillaPublishers.index(seleccion[0])
            imagen = self.publisher.getImageCover()
            self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            self.labelImagen['image'] = self.cover

    def cargarResultado(self,listaPublishers):
        for item in self.grillaPublishers.get_children():
            self.grillaPublishers.delete(item)
        for publisher in listaPublishers:
            self.grillaPublishers.insert('', 'end', '', text='', values=(publisher.id_publisher,
                                                                     publisher.name
                                                                        ))







if __name__ == '__main__':
    root = Tk()
    publisher = PublisherVineGui(root, width=507, height=358)
    publisher.grid(sticky=(N, S, E, W))
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.mainloop()

