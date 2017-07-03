from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos
from  Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
from PIL import Image, ImageTk
import Entidades.Init
from Entidades.Volumes.Volume import Volume

class VolumeVineGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)

        config = Config()

        self.comicVineSearcher = ComicVineSearcher(config.getClave('publishers'))
        self.comicVineSearcher.setEntidad("volumes")

        self.labelId = Label(self, text="Nombre Volumen: ")
        self.labelId.grid(row=0,column=0, sticky=W ,padx=5,pady=5)
        self.entradaNombreEditorial = Entry(self, width=150)
        self.labelId = Label(self, text="Id Volumen: ")
        self.labelId.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.entradaNombreEditorial = Entry(self, width=150)

        self.varID=StringVar()
        self.entradaNombreEditorial.grid(row=0,column=1, sticky=W + E,padx=5,pady=5,columnspan=2 )
        self.botonLookupPublisher=Button(self, command=self.buscar)
        self.botonLookupPublisher.grid(row=0,column=3)
        self.pilImagenLookup=Iconos.Iconos.pilImagenLookup
        self.imageLookup = PIL.ImageTk.PhotoImage(self.pilImagenLookup)
        self.botonLookupPublisher.config(image=self.imageLookup)
        self.labelImagen = Label(self, text="cover volumen")
        self.coverSize = (150,150)
        self.labelImagen.grid(column=4,row=1)


        ##config grilla series
        self.panelGrilla = Frame(self)
        self.panelGrilla.grid(column=0, row=2,  columnspan=3, sticky=(N, S, E, W), padx=5)

        self.grillaVolumes = ttk.Treeview(self.panelGrilla, columns=(
            'name', 'count_of_issues', 'description', 'Id', 'image', 'publisher', 'start_year'),
                                         displaycolumns=('Id', 'name', 'count_of_issues', 'publisher', 'start_year'))
        
        self.grillaVolumes.grid(column=0, row=0,  columnspan=3, sticky=(N, S, E, W))
        self.grillaVolumes.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()

        scrollGrid = ttk.Scrollbar(self.panelGrilla, orient=VERTICAL, command=self.grillaVolumes.yview)
        scrollGrid.grid(column=3, row=0, sticky=(N, S))

        self.grillaVolumes.configure(yscrollcommand=scrollGrid.set)

        self.grillaVolumes.heading('Id', text='Id')
        self.grillaVolumes.heading('name', text='Nombre')
        self.grillaVolumes.heading('count_of_issues', text='Numeros')
        self.grillaVolumes.heading('publisher', text='Editorial')
        self.grillaVolumes.heading('start_year', text='Año')
        self.grillaVolumes.config(show='headings')  # tree, headings

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
        if (self.grillaVolumes.selection()):
            seleccion = self.grillaVolumes.selection()
            self.publisher = self.comicVineSearcher.listaBusquedaVine[self.grillaVolumes.index(seleccion[0])]
            self.grillaVolumes.index(seleccion[0])
            imagen = self.publisher.getImageCover()
            self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            self.labelImagen['image'] = self.cover

    def cargarResultado(self,listavolumes):
        for item in self.grillaVolumes.get_children():
            self.grillaVolumes.delete(item)
        for volume in listavolumes:
            self.grillaVolumes.insert('', 'end', '', text='', values=(volume.nombre,
                                                                      volume.cantidadNumeros,
                                                                      volume.descripcion,
                                                                      volume.id,
                                                                      volume.image_url,
                                                                      "volume.publisherName",
                                                                      volume.AnioInicio)
                                                                        )







if __name__ == '__main__':
    root = Tk()
    publisher = VolumeVineGui(root, width=507, height=358)
    publisher.grid(sticky=(N, S, E, W))
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.mainloop()

