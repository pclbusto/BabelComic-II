from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos
from  Extras.ComicVineSearcher import ComicVineSearcher
from Extras.Config import Config
from PIL import Image, ImageTk
import Entidades.Init
from Entidades.Volumes.Volume import Volume
from Entidades.Publishers.Publisher import Publisher
from Gui.PublisherLookupGui import PublisherLookupGui
from Entidades.Volumes.ComicsInVolume import ComicInVolumes

class VolumeVineGui(Frame):
    def __init__(self, parent, session=None, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)

        config = Config()
        iconos = Iconos.Iconos()
        self.pilImagenLookup = iconos.pilImagenLookup
        self.imageLookup = PIL.ImageTk.PhotoImage(self.pilImagenLookup)
        self.offset=0
        self.frameParametros = Frame(self)
        self.frameParametros.grid(row=0,column=0, sticky=(W,E,N,S))
        self.listaFiltrada=[]
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session
        self.comicVineSearcher = ComicVineSearcher(config.getClave('volumes'))
        self.comicVineSearcher.setEntidad("volumes")

        self.labelId = Label(self.frameParametros, text="Nombre Volumen: ")
        self.labelId.grid(row=0, column=0, sticky=(W, E), padx=5, pady=5)
        self.entradaNombreVolume = Entry(self.frameParametros, width=70)
        self.entradaNombreVolume.grid(column=1, row=0)
        Label(self.frameParametros, text="Editorial: ").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.varID=StringVar()
        self.entradaNombreEditorial = Entry(self.frameParametros, width=30)
        self.entradaNombreEditorial.grid(row=1, column=1, sticky=W + E, padx=5,pady=5 )
        self.botonBuscar=Button(self.frameParametros, text = 'buscar', command=self.buscar)
        self.botonBuscar.grid(row=0,column=3)
        self.botonBuscar = Button(self.frameParametros, text='buscar mas', command=self.buscarMas)
        self.botonBuscar.grid(row=0, column=4)

        self.botonLookupPublisher = Button(self.frameParametros, image=self.imageLookup,command=self.openLookupPublisher)
        self.botonLookupPublisher.grid(row=1,column=3)
        self.labelImagen = Label(self, text="cover volumen")
        self.coverSize = (150,150)
        self.labelImagen.grid(column=4,row=1)

        self.volume = None
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

        self.grillaVolumes.heading('Id', text='Id',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'Id', False))
        self.grillaVolumes.heading('name', text='Nombre',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'name', False))
        self.grillaVolumes.heading('count_of_issues', text='Numeros',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'count_of_issues', False))
        self.grillaVolumes.heading('publisher', text='Editorial',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'publisher', False))
        self.grillaVolumes.heading('start_year', text='Año',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'start_year', False))
        self.grillaVolumes.config(show='headings')  # tree, headings

        self.botonLookupPublisher = Button(self,text="agregar",command = self.agregarVolumen)
        self.botonLookupPublisher.grid(row=0, column=4, pady=3, sticky=(E,W))
        self.statusBar = Label(self, text='status', relief=GROOVE, anchor=E)
        self.statusBar.grid(column=0, row=4, sticky=(E,W),columnspan=5)

    def int(self,t):
        if t[0].isdigit():
            return(int(t[0]))
        return 0

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        if col in['count_of_issues','start_year']:
            l.sort(reverse=reverse,key=self.int)
        else:
            l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        # reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def agregarVolumen(self):
        cnf = Config(self.session)
        cv = ComicVineSearcher(cnf.getClave('volume'))
        cv.entidad = 'volume'
        volumenAndIssues = cv.getVineEntity(self.volume.id)

        self.session.query(ComicInVolumes).filter(ComicInVolumes.volumenId == self.volume.id).delete()
        for numeroComic in volumenAndIssues[1]:
            self.session.add(numeroComic)
        self.session.add(volumenAndIssues[0])
        self.session.commit()

    def openLookupPublisher(self):
        window = Toplevel()
        self.publisher = Publisher()
        lk = PublisherLookupGui(window, self.publisher)
        lk.grid(sticky=(E, W, S, N))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.geometry("+0+0")
        window.wm_title(string="Editoriales")
        self.wait_window(window)
        self.publisher = lk.getPublisher()
        self.entradaNombreEditorial.insert(0,self.publisher.name)

    def buscarMas(self):
        self.comicVineSearcher.vineSearchMore()
        self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)

    def __buscar__(self):
        print("buscando....")
        if (self.entradaNombreVolume.get() != ''):
            print("BUSCANDO....")
            self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)
    def buscar(self):
        self.offset = 0
        self.comicVineSearcher.clearFilter()
        self.comicVineSearcher.addFilter("name:" + self.entradaNombreVolume.get())
        self.comicVineSearcher.vineSearch(self.offset)
        self.cargarResultado(self.comicVineSearcher.listaBusquedaVine)

    def itemClicked(self, event):
        if (self.grillaVolumes.selection()):
            seleccion = self.grillaVolumes.selection()
            id = self.grillaVolumes.item(seleccion, 'values')[3]
            for volume in self.comicVineSearcher.listaBusquedaVine:
                if volume.id == id:
                    self.volume = volume
                    break

            #self.volume = self.comicVineSearcher.listaBusquedaVine[self.grillaVolumes.index(seleccion[0])]
            self.grillaVolumes.index(seleccion[0])
            imagen = self.volume.getImageCover()
            self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            self.labelImagen['image'] = self.cover

    def cargarResultado(self,listavolumes):
        for item in self.grillaVolumes.get_children():
            self.grillaVolumes.delete(item)
        self.listaFiltrada.clear()
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
        self.statusBar.config(text = "Cantidad Resultados: %d - Cantidad Resultados sin filtro: %d- Cantidad Total de Resultados en ComicVine: %d"%(len(self.listaFiltrada),
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

