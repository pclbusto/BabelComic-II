from tkinter import *
from tkinter import Tk, ttk
from tkinter import filedialog
from Entidades.Publishers.Publisher import Publisher
from PIL import Image, ImageTk
from iconos.Iconos import Iconos
import Entidades.Init

class PublisherLookupData():
    ATRIBUTO_ID = 'id'
    ATRIBUTO_NOMBRE = 'nombre'
    ATRIBUTO_DESCRIPCION = 'descripcion'
    ATRIBUTO_ANIO = 'AnioInicio'

    def __init__(self):
        self.atributoBusqueda = PublisherLookupData.ATRIBUTO_NOMBRE


class PublisherLookupGui(Frame):
    def __init__(self, parent, publisher, cnf={}, **kw):
        Frame.__init__(self, parent, cnf={}, **kw)
        self.columnconfigure(0, weight=1)
        self.publisher = publisher

        self.rowconfigure(1, weight=1)
        # panel busqueda opciones entrada y boton buscar
        self.panelBusqueda = ttk.Frame(self)
        self.panelBusqueda.grid(column=0, row=0, sticky=(E, W, N))

        self.panelBusqueda.columnconfigure(0, weight=1)
        self.panelBusqueda.columnconfigure(1, weight=4)
        self.panelBusqueda.columnconfigure(2, weight=1)
        self.panelBusqueda.columnconfigure(3, weight=4)

        ttk.Label(self.panelBusqueda, text="Nombre: ").grid(column=0, row=0, sticky=W)
        self.entradaBuscarPorNombre = ttk.Entry(self.panelBusqueda)
        self.entradaBuscarPorNombre.grid(column=1, row=0, sticky=(W, E),padx=5)

        ttk.Button(self.panelBusqueda, text='Buscar', command=self.buscarPublisher).grid(sticky=(E), column=4, row=0)
        # self.opcionesBusqueda.current(1)


        # panel de grilla y previsualizacion primer cover de serie
        self.framePrincipal = LabelFrame(self)
        self.framePrincipal.grid(sticky=(E, W, S, N), column=0, row=1)
        self.framePrincipal.columnconfigure(0, weight=1)
        self.framePrincipal.rowconfigure(0, weight=1)
        self.coverSize = (240, 372)

        # lo necesitamos para agruparla con la scroll
        self.frameGrilla = Frame(self.framePrincipal)
        self.frameGrilla.grid(sticky=(N, W, E, S))
        self.frameGrilla.rowconfigure(0, weight=1)
        self.frameGrilla.columnconfigure(0, weight=1)
        ##config grilla series
        self.grillaPublisher = ttk.Treeview(self.frameGrilla, columns=(
            'name', 'Id'),
                                         displaycolumns=('Id', 'name'))
        self.grillaPublisher.grid(column=0, row=0, rowspan=1, sticky=(N, S, E, W))

        scrollGrid = ttk.Scrollbar(self.frameGrilla, orient=VERTICAL, command=self.grillaPublisher.yview)
        scrollGrid.grid(column=1, row=0, rowspan=1, sticky=(N, S))

        self.grillaPublisher.configure(yscrollcommand=scrollGrid.set)

        self.grillaPublisher.heading('Id', text='Id')
        self.grillaPublisher.heading('name', text='Nombre')
        self.grillaPublisher.config(show='headings')  # tree, headings

        self.grillaPublisher.heading('name', command=lambda col='name': self.sortby(col))
        self.grillaPublisher.heading('Id', command=lambda col='Id': self.sortby(col))

        ''' no ordena bien con 70000 registros es lento es mas facil tirar una nueva consutla contra el SQL
        self.grillaPublisher.heading('start_year', command=lambda col='start_year': self.sortby(self.grillaPublisher, 'start_year', int(True)))
        self.grillaPublisher.heading('name', command=lambda col='name': self.sortby(self.grillaPublisher, 'name', int(True)))
        self.grillaPublisher.heading('count_of_issues', command=lambda col='count_of_issues': self.sortby(self.grillaPublisher, 'count_of_issues', int(True)))
        self.grillaPublisher.heading('publisher', command=lambda col='publisher': self.sortby(self.grillaPublisher, 'publisher', int(True)))
        '''

        self.grillaPublisher.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()

        self.labelImagen = Label(self.frameGrilla)
        self.labelImagen.grid(column=3, row=0)

        # boton parte inferior formulario
        ttk.Button(self, text='seleccionar', command=self.seleccionarPublisher).grid(column=0, row=2, sticky=(E))
        self.desc = True

        self.pilImageCoverGenerica = Iconos().pilImageLogo
        self.cover = ImageTk.PhotoImage(self.pilImageCoverGenerica.resize(self.coverSize))
        self.labelImagen['image'] = self.cover


    def getPublisher(self):
        print('retornando serie: ' + self.publisher.name)
        return self.publisher

    def itemClicked(self, event):
        if (self.grillaPublisher.selection()):
            seleccion = self.grillaPublisher.selection()
            self.publisher = self.publishers[self.grillaPublisher.index(seleccion[0])]
            self.grillaPublisher.index(seleccion[0])
            imagen = self.publisher.getImageCover()
            self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            self.labelImagen['image'] = self.cover

    def seleccionarPublisher(self):
        print(self.publisher.id)

    # def sortby(self, col):
    #     print('sort: ' + str(self.opcionesBusqueda.current()))
    #
    #     if col == 'nombre':
    #         self.opcionesBusqueda.current(0)
    #     elif col == 'cantidadNumeros':
    #         self.opcionesBusqueda.current(1)
    #     elif col == 'name':
    #         self.opcionesBusqueda.current(2)
    #     elif col == 'AnioInicio':
    #         print('antes de cambiar sort:')
    #         self.opcionesBusqueda.current(3)
    #         print('despues de cambiar sort: ' + str(self.opcionesBusqueda.current()))
    #
    #     if (not self.desc):
    #         self.buscarVolume('order by ' + col + ' desc')
    #     else:
    #         self.buscarVolume(('order by ' + col + ' asc')
    #
    def buscarPublisher(self, orderBy=None):

        for item in self.grillaPublisher.get_children():
            self.grillaPublisher.delete(item)
        session = Entidades.Init.Session()
        self.publishers = session.query(Publisher)
        for index, publisher in enumerate(self.publishers):
            self.grillaPublisher.insert('', 'end', index, text='', values=(publisher.id_publisher,
                                                                        publisher.name))


if (__name__ == '__main__'):
    root = Tk()
    volume = Publisher()
    lk = PublisherLookupGui(root, volume)
    ##  C:\Users\bustoped\Pictures\comics\1963 - Crisis en Tierras Múltiples Vol 2-3\Cr1515_3n_7i3rr@5_Mul71pl35_#3.howtoarsenio.blogspot.com.cbz
    ##    data = SeriesLookupData()
    ##    print(data.atributoBusqueda)
    ##
    lk.grid(sticky=(E, W, S, N))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
