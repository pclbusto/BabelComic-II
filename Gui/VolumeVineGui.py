from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos
from  Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
from PIL import Image, ImageTk
import Entidades.Init
from Entidades.Volumes.Volume import Volume
from Gui.VolumeLookupGui import VolumesLookupGui

class VolumeVineGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)

        config = Config()
        self.pilImagenLookup = Iconos.Iconos.pilImagenLookup
        self.imageLookup = PIL.ImageTk.PhotoImage(self.pilImagenLookup)
        self.offset=0
        self.frameParametros = Frame(self)
        self.frameParametros.grid(row=0,column=0)
        self.listaFiltrada=[]
        self.comicVineSearcher = ComicVineSearcher(config.getClave('publishers'))
        self.comicVineSearcher.setEntidad("volumes")

        self.labelId = Label(self.frameParametros, text="Nombre Volumen: ")
        self.labelId.grid(row=0,column=0, sticky=W + E ,padx=5,pady=5)
        self.entradaNombreVolume = Entry(self.frameParametros,width=30)
        self.entradaNombreVolume.grid(column=1,row=0)
        Label(self.frameParametros, text="Publisher: ").grid(row=1, column=0, sticky=W, padx=5, pady=5)

        #self.entradaNombreEditorial =
        #
        #self.botonLookupEditorial = Button(self,image =self.imageLookup)

        self.varID=StringVar()
        self.entradaNombreEditorial = Entry(self.frameParametros,width=30)
        self.entradaNombreEditorial.grid(row=1,column=1, sticky=W + E,padx=5,pady=5 )
        self.botonBuscar=Button(self.frameParametros, text = 'buscar', command=self.buscar)
        self.botonBuscar.grid(row=0,column=3)
        self.botonBuscar = Button(self.frameParametros, text='buscar mas', command=self.buscarMas)
        self.botonBuscar.grid(row=0, column=4)

        self.botonLookupPublisher = Button(self.frameParametros, image=self.imageLookup,command=self.openSerieLookup)
        self.botonLookupPublisher.grid(row=1,column=3)
        self.labelImagen = Label(self, text="cover volumen")
        self.coverSize = (150,150)
        self.labelImagen.grid(column=4,row=2)

        self.publisher = None
        #
        # ##config grilla series
        self.panelGrilla = Frame(self)
        self.panelGrilla.grid(column=0, row=1, sticky=(N, S, E, W), padx=5)

        self.grillaVolumes = ttk.Treeview(self.panelGrilla, columns=(
            'name', 'count_of_issues', 'description', 'Id', 'image', 'publisher', 'start_year'),
                                         displaycolumns=('Id', 'name', 'count_of_issues', 'publisher', 'start_year'))

        self.grillaVolumes.grid(column=0, row=0,  columnspan=3, sticky=(N, S, E, W))
        self.grillaVolumes.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()

        scrollGrid = ttk.Scrollbar(self.panelGrilla, orient=VERTICAL, command=self.grillaVolumes.yview)
        scrollGrid.grid(column=3, row=0, sticky=(N, S,E,W),columnspan=2)

        self.grillaVolumes.configure(yscrollcommand=scrollGrid.set)

        self.grillaVolumes.heading('Id', text='Id')
        self.grillaVolumes.heading('name', text='Nombre')
        self.grillaVolumes.heading('count_of_issues', text='Numeros')
        self.grillaVolumes.heading('publisher', text='Editorial')
        self.grillaVolumes.heading('start_year', text='Año')
        self.grillaVolumes.config(show='headings')  # tree, headings

        self.botonLookupPublisher = Button(self,text="agregar",command = self.agregarEditorial)
        self.botonLookupPublisher.grid(row=0, column=4, pady=3, sticky=(E,W))
        self.statusBar = Label(self, text='status', relief=GROOVE, anchor=E)
        self.statusBar.grid(column=0, row=4, sticky=(E,W),columnspan=5)

    def agregarEditorial(self):
        session = Entidades.Init.Session()
        session.add(self.publisher)
        session.commit()

    def openSerieLookup(self):
        window = Toplevel()
        volumeRetorno = Volume()
        lk = VolumesLookupGui(window, volumeRetorno)
        lk.grid(sticky=(E, W, S, N))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.geometry("+0+0")
        window.wm_title(string="Series")
        self.wait_window(window)
        serieRetorno = lk.getSerie()
        self.entrySerie.set(serieRetorno.id)

    def buscarMas(self):
        self.__buscar__()

    def __buscar__(self):
        print("buscando....")
        if (self.entradaNombreVolume.get() != ''):
            print("BUSCANDO....")
            self.comicVineSearcher.addFilter("name:" + self.entradaNombreVolume.get())
            self.comicVineSearcher.vineSearch(self.offset)
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)
    def buscar(self):
        self.offset = 0
        self.comicVineSearcher.clearFilter()
        for item in self.grillaVolumes.get_children():
            self.grillaVolumes.delete(item)
        self.__buscar__()

    def itemClicked(self, event):
        if (self.grillaVolumes.selection()):
            seleccion = self.grillaVolumes.selection()
            self.publisher = self.comicVineSearcher.listaBusquedaVine[self.grillaVolumes.index(seleccion[0])]
            self.grillaVolumes.index(seleccion[0])
            imagen = self.publisher.getImageCover()
            self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            self.labelImagen['image'] = self.cover

    def cargarResultado(self,listavolumes):
        for volume in listavolumes:
            if self.publisher is not None:
                if self.publisher.id_publisher==Volume.publisherId:
                    self.listaFiltrada.append(volume)
            else:
                self.listaFiltrada.append(volume)
        for volume in self.listaFiltrada:
            self.grillaVolumes.insert('', 'end', '', text='', values=(volume.nombre,
                                                                      volume.cantidadNumeros,
                                                                      volume.descripcion,
                                                                      volume.id,
                                                                      volume.image_url,
                                                                      volume.publisher_name,
                                                                      volume.AnioInicio)
                                      )
        self.statusBar.config(text = "Cantidad Resultados: %d - Cantidad Resultados sin filtro: %d- Cantidad Total de Resultados en ComicVine: %d"%(len(listaFiltrada),
                                                                                                                                                    len(self.comicVineSearcher.listaBusquedaVine),
                                                                                                                                                    self.comicVineSearcher.cantidadResultados)
                              )






if __name__ == '__main__':
    root = Tk()
    publisher = VolumeVineGui(root, width=507, height=358)
    publisher.grid(sticky=(N, S, E, W))
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.mainloop()

