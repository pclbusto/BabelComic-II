from tkinter import *
from tkinter import Tk, ttk
from tkinter import filedialog
from Entidades.Volumes.Volume import Volume
from PIL import Image, ImageTk
from iconos.Iconos import Iconos
import Entidades.Init

class VolumesLookupData():
    ATRIBUTO_ID = 'id'
    ATRIBUTO_NOMBRE = 'nombre'
    ATRIBUTO_DESCRIPCION = 'descripcion'
    ATRIBUTO_ANIO = 'AnioInicio'

    def __init__(self):
        self.atributoBusqueda = VolumesLookupData.ATRIBUTO_NOMBRE


class VolumesLookupGui(Frame):
    def __init__(self, parent, serie, cnf={}, **kw):
        Frame.__init__(self, parent, cnf={}, **kw)
        self.columnconfigure(0, weight=1)
        self.serie = serie

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

        ttk.Label(self.panelBusqueda, text="Cantidad Números: ").grid(column=0, row=1, sticky=W)
        self.entradaBuscarPorCantidadNumeros = ttk.Entry(self.panelBusqueda)
        self.entradaBuscarPorCantidadNumeros.grid(column=1, row=1, sticky=(W, E),padx=5)

        ttk.Label(self.panelBusqueda, text="Año Inicio: ").grid(column=2, row=0, sticky=W)
        self.entradaBuscarPorAñoInicio = ttk.Entry(self.panelBusqueda)
        self.entradaBuscarPorAñoInicio.grid(column=3, row=0, sticky=(W, E),padx=5)

        ttk.Label(self.panelBusqueda, text="Editorial: ").grid(column=2, row=1, sticky=W)
        self.entradaBuscarPorEditorial = ttk.Entry(self.panelBusqueda)
        self.entradaBuscarPorEditorial.grid(column=3, row=1, sticky=(W, E),padx=5)


        # self.comboOpcionBusqueda = StringVar()
        # self.opcionesBusqueda = ttk.Combobox(self.panelBusqueda, textvariable=self.comboOpcionBusqueda)
        # self.comboOpcionBusqueda.trace(mode='w', callback=self.__ChangedComboboxFilter__)
        # self.opcionesBusqueda['values'] = (
        # 'Buscar por Nombre', 'Buscar por Número', 'Buscar por Editorial', 'Buscar por Año')
        # self.filtros = {'nombre': [''], 'name': [], 'cantidadNumeros': [], 'AnioInicio': []}
        # self.opcionesBusqueda.grid(sticky=(W))
        # self.varaiblePatronBusqueda = StringVar()
        # self.entryFiltro = ttk.Entry(self.panelBusqueda, textvariable=self.varaiblePatronBusqueda)
        # self.varaiblePatronBusqueda.trace(mode='w', callback=self.__ChangedFilter__)
        # self.entryFiltro.grid(column=1, row=0, sticky=(W, E))

        ttk.Button(self.panelBusqueda, text='Buscar', command=self.buscarVolume).grid(sticky=(E), column=4, row=0)
        # self.opcionesBusqueda.current(1)


        # panel de grilla y previsualizacion primer cover de serie
        self.framePrincipal = LabelFrame(self)
        self.framePrincipal.grid(sticky=(E, W, S, N), column=0, row=1)
        self.framePrincipal.columnconfigure(0, weight=1)
        self.framePrincipal.rowconfigure(0, weight=1)
        self.coverSize = (240, 372)
        # self.frame.columnconfigure(1,weight=1)
        # self.frame.rowconfigure(0,weight=1)


        # lo necesitamos para agruparla con la scroll
        self.frameGrilla = Frame(self.framePrincipal)
        self.frameGrilla.grid(sticky=(N, W, E, S))
        self.frameGrilla.rowconfigure(0, weight=1)
        self.frameGrilla.columnconfigure(0, weight=1)
        ##config grilla series
        self.grillaSeries = ttk.Treeview(self.frameGrilla, columns=(
            'name', 'count_of_issues', 'description', 'Id', 'image', 'publisher', 'start_year'),
                                         displaycolumns=('Id', 'name', 'count_of_issues', 'publisher', 'start_year'))
        self.grillaSeries.grid(column=0, row=0, rowspan=1, sticky=(N, S, E, W))

        scrollGrid = ttk.Scrollbar(self.frameGrilla, orient=VERTICAL, command=self.grillaSeries.yview)
        scrollGrid.grid(column=1, row=0, rowspan=1, sticky=(N, S))

        self.grillaSeries.configure(yscrollcommand=scrollGrid.set)

        self.grillaSeries.heading('Id', text='Id')
        self.grillaSeries.heading('name', text='Nombre')
        self.grillaSeries.heading('count_of_issues', text='Numeros')
        self.grillaSeries.heading('publisher', text='Editorial')
        self.grillaSeries.heading('start_year', text='Año')
        self.grillaSeries.config(show='headings')  # tree, headings

        self.grillaSeries.heading('start_year', command=lambda col='AnioInicio': self.sortby(col))
        self.grillaSeries.heading('name', command=lambda col='nombre': self.sortby(col))
        self.grillaSeries.heading('count_of_issues', command=lambda col='cantidadNumeros': self.sortby(col))
        self.grillaSeries.heading('publisher', command=lambda col='name': self.sortby(col))

        ''' no ordena bien con 70000 registros es lento es mas facil tirar una nueva consutla contra el SQL
        self.grillaSeries.heading('start_year', command=lambda col='start_year': self.sortby(self.grillaSeries, 'start_year', int(True)))
        self.grillaSeries.heading('name', command=lambda col='name': self.sortby(self.grillaSeries, 'name', int(True)))
        self.grillaSeries.heading('count_of_issues', command=lambda col='count_of_issues': self.sortby(self.grillaSeries, 'count_of_issues', int(True)))
        self.grillaSeries.heading('publisher', command=lambda col='publisher': self.sortby(self.grillaSeries, 'publisher', int(True)))
        '''

        self.grillaSeries.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()

        self.labelImagen = Label(self.frameGrilla)
        self.labelImagen.grid(column=3, row=0)

        # boton parte inferior formulario
        ttk.Button(self, text='seleccionar', command=self.seleccionarVolume).grid(column=0, row=2, sticky=(E))
        self.desc = True

        self.pilImageCoverGenerica = Iconos.pilImageCoverGenerica
        self.cover = ImageTk.PhotoImage(self.pilImageCoverGenerica.resize(self.coverSize))
        self.labelImagen['image'] = self.cover
    #
    # def __ChangedFilter__(self, *args):  # recordar siempre que son 4 paramentros sino da errores raros
    #     print('__ChangedFilter__ current: ', str(self.opcionesBusqueda.current()))
    #     if (self.opcionesBusqueda.current() == 0):
    #         print('limpiando filtro nombre')
    #         del self.filtros['nombre']
    #         cadena = self.varaiblePatronBusqueda.get()
    #         self.filtros['nombre'] = [cadena]
    #         print('filtro cargado: ' + str(self.filtros['nombre']))
    #     if (self.opcionesBusqueda.current() == 1):
    #         del self.filtros['cantidadNumeros']
    #         cadena = self.varaiblePatronBusqueda.get()
    #         print('cantidadNumeros: ' + str(self.filtros))
    #         print(len(cadena))
    #         if len(cadena) > 0:
    #             self.filtros['cantidadNumeros'] = [self.varaiblePatronBusqueda.get()]
    #
    #     if (self.opcionesBusqueda.current() == 2):
    #         del self.filtros['name']
    #         self.filtros['name'] = [self.varaiblePatronBusqueda.get()]
    #     if (self.opcionesBusqueda.current() == 3):
    #         del self.filtros['AnioInicio']
    #         print('AnioInicio: ' + str(self.filtros))
    #         cadena = self.varaiblePatronBusqueda.get()
    #         if len(cadena) > 0:
    #             self.filtros['AnioInicio'] = [self.varaiblePatronBusqueda.get()]
    #
    # def __ChangedComboboxFilter__(self, *args):
    #     lista = []
    #     if (self.opcionesBusqueda.current() == 0):
    #         if ('nombre' in self.filtros):
    #             lista = self.filtros['nombre']
    #     elif (self.opcionesBusqueda.current() == 1):
    #         if ('cantidadNumeros' in self.filtros):
    #             lista = self.filtros['cantidadNumeros']
    #     elif (self.opcionesBusqueda.current() == 2):
    #         if ('name' in self.filtros):
    #             lista = self.filtros['name']
    #     elif (self.opcionesBusqueda.current() == 3):
    #         if ('AnioInicio' in self.filtros):
    #             lista = self.filtros['AnioInicio']
    #
    #     self.entryFiltro.delete(0, END)
    #     cadena = ''
    #     if lista:
    #         print('lista de palabras: ' + str(lista))
    #     for palabra in lista:
    #         print('palabra: ' + palabra)
    #         cadena += palabra + " "
    #     self.entryFiltro.insert(END, cadena[:-1])
    #

    def getSerie(self):
        print('retornando serie: ' + self.serie.nombre)
        return self.serie

    def itemClicked(self, event):
        if (self.grillaSeries.selection()):
            seleccion = self.grillaSeries.selection()
            self.serie = self.volumes[self.grillaSeries.index(seleccion[0])]
            self.grillaSeries.index(seleccion[0])
            imagen = self.serie.getImageCover()
            self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            self.labelImagen['image'] = self.cover

    def seleccionarVolume(self):
        print(self.serie.id)

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
    def buscarVolume(self, orderBy=None):

        for item in self.grillaSeries.get_children():
            self.grillaSeries.delete(item)
        session = Entidades.Init.Session()
        self.volumes = session.query(Volume)
        for volume in self.volumes:
            self.grillaSeries.insert('', 'end', '', text='', values=(volume.nombre,
                                                                 volume.cantidadNumeros,
                                                                 volume.descripcion,
                                                                 volume.id,
                                                                 volume.image_url,
                                                                 "volume.publisherName",
                                                                 volume.AnioInicio))


if (__name__ == '__main__'):
    root = Tk()
    volume = Volume()
    lk = VolumesLookupGui(root, volume)
    ##  C:\Users\bustoped\Pictures\comics\1963 - Crisis en Tierras Múltiples Vol 2-3\Cr1515_3n_7i3rr@5_Mul71pl35_#3.howtoarsenio.blogspot.com.cbz
    ##    data = SeriesLookupData()
    ##    print(data.atributoBusqueda)
    ##
    lk.grid(sticky=(E, W, S, N))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
