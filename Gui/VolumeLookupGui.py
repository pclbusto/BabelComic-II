from tkinter import *
from tkinter import Tk, ttk
from tkinter import filedialog
from Entidades.Volumes.Volume import Volume
from PIL import Image, ImageTk
from iconos.Iconos import Iconos
import Entidades.Init
from sqlalchemy import func

class VolumesLookupData():
    ATRIBUTO_ID = 'id'
    ATRIBUTO_NOMBRE = 'nombre'
    ATRIBUTO_DESCRIPCION = 'descripcion'
    ATRIBUTO_ANIO = 'AnioInicio'

    def __init__(self):
        self.atributoBusqueda = VolumesLookupData.ATRIBUTO_NOMBRE


class VolumesLookupGui(Frame):
    def __init__(self, parent, serie, session=None, cnf={}, **kw):
        Frame.__init__(self, parent, cnf={}, **kw)
        self.padre = parent
        self.columnconfigure(0, weight=1)
        self.serie = serie
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

        self.rowconfigure(1, weight=1)
        # panel busqueda opciones entrada y boton buscar
        self.panelBusqueda = ttk.Frame(self)
        self.panelBusqueda.grid(column=0, row=0, sticky=(E, W, N))

        self.panelBusqueda.columnconfigure(0, weight=1)
        self.panelBusqueda.columnconfigure(1, weight=4)
        self.panelBusqueda.columnconfigure(2, weight=1)
        self.panelBusqueda.columnconfigure(3, weight=4)

        ttk.Label(self.panelBusqueda, text="Nombre: ").grid(column=0, row=0, sticky=W)
        self.variableBuscarPorNombre = StringVar()
        self.variableBuscarPorNombre.trace("w", self.callbackVariableBuscarPor)
        self.entradaBuscarPorNombre = ttk.Entry(self.panelBusqueda,textvariable=self.variableBuscarPorNombre)

        self.entradaBuscarPorNombre.grid(column=1, row=0, sticky=(W, E),padx=5)

        ttk.Label(self.panelBusqueda, text="Cantidad Números: ").grid(column=0, row=1, sticky=W)
        self.entradaBuscarPorCantidadNumeros = ttk.Entry(self.panelBusqueda)
        self.entradaBuscarPorCantidadNumeros.grid(column=1, row=1, sticky=(W, E),padx=5)

        ttk.Label(self.panelBusqueda, text="Año Inicio: ").grid(column=2, row=0, sticky=W)
        self.entradaBuscarPorAñoInicio = ttk.Entry(self.panelBusqueda)
        self.entradaBuscarPorAñoInicio.grid(column=3, row=0, sticky=(W, E),padx=5)

        ttk.Label(self.panelBusqueda, text="Editorial: ").grid(column=2, row=1, sticky=W)
        self.variableBuscarPorEditorial = StringVar()
        self.variableBuscarPorEditorial.trace("w", self.callbackVariableBuscarPor)

        self.entradaBuscarPorEditorial = ttk.Entry(self.panelBusqueda,textvariable=self.variableBuscarPorEditorial)
        self.entradaBuscarPorEditorial.grid(column=3, row=1, sticky=(W, E),padx=5)

        self.padre.bind("<Control-s>",lambda x:  self.seleccionarVolume())

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
        self.grillaVolumes = ttk.Treeview(self.frameGrilla, columns=(
            'name', 'count_of_issues', 'description', 'Id', 'image', 'publisher', 'start_year'),
                                         displaycolumns=('Id', 'name', 'count_of_issues', 'publisher', 'start_year'))
        self.grillaVolumes.grid(column=0, row=0, rowspan=1, sticky=(N, S, E, W))

        scrollGrid = ttk.Scrollbar(self.frameGrilla, orient=VERTICAL, command=self.grillaVolumes.yview)
        scrollGrid.grid(column=1, row=0, rowspan=1, sticky=(N, S))

        self.grillaVolumes.configure(yscrollcommand=scrollGrid.set)

        self.grillaVolumes.heading('Id', text='Id')
        self.grillaVolumes.heading('name', text='Nombre')
        self.grillaVolumes.heading('count_of_issues', text='Numeros')
        self.grillaVolumes.heading('publisher', text='Editorial')
        self.grillaVolumes.heading('start_year', text='Año')
        self.grillaVolumes.config(show='headings')  # tree, headings

        self.grillaVolumes.heading('start_year',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'start_year', False))
        self.grillaVolumes.heading('name',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'name', False))
        self.grillaVolumes.heading('count_of_issues',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'count_of_issues', False))
        self.grillaVolumes.heading('publisher',command=lambda: self.treeview_sort_column(self.grillaVolumes, 'publisher', False))

        self.grillaVolumes.bind('<<TreeviewSelect>>', self.itemClicked)  # the item clicked can be found via tree.focus()

        self.labelImagen = Label(self.frameGrilla)
        self.labelImagen.grid(column=3, row=0)

        # boton parte inferior formulario
        ttk.Button(self, text='seleccionar', command=self.seleccionarVolume).grid(column=0, row=2, sticky=(E))
        self.desc = True

        self.pilImageCoverGenerica = Iconos.pilImageCoverGenerica
        self.cover = ImageTk.PhotoImage(self.pilImageCoverGenerica.resize(self.coverSize))
        self.labelImagen['image'] = self.cover

    def callbackVariableBuscarPor(self,*args):
        self.buscarVolume()

    def int(self,t):
        return(int(t[0]))

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        if col in['start_year','count_of_issues']:
            l.sort(reverse=reverse,key=self.int)
        else:
            l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)
        # reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))


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
        if (self.grillaVolumes.selection()):
            seleccion = self.grillaVolumes.selection()
            id = self.grillaVolumes.item(seleccion,'values')[3]
            for volume in self.volumes:
                if volume.id == id:
                    break;
            self.serie = volume
                #self.volumes[self.grillaVolumes.index(seleccion[0])]
            self.grillaVolumes.index(seleccion[0])
            imagen = self.serie.getImageCover()
            self.cover = ImageTk.PhotoImage(imagen.resize(self.coverSize))
            self.labelImagen['image'] = self.cover

    def seleccionarVolume(self):
        self.padre.destroy()

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

    def buscarVolume(self, orderBy=None):

        for item in self.grillaVolumes.get_children():
            self.grillaVolumes.delete(item)
        consulta = None
        if self.entradaBuscarPorNombre.get()!='':
            consulta = self.session.query(Volume).filter(func.lower(Volume.nombre.like("%{}%".format(self.entradaBuscarPorNombre.get()))))
        else:
            consulta = self.session.query(Volume)

        if self.entradaBuscarPorEditorial.get()!='':
            consulta = consulta.filter(func.lower(Volume.publisher_name.like("%{}%".format(self.entradaBuscarPorEditorial.get()))))

        self.volumes = consulta.all()
        for volume in self.volumes:
            self.grillaVolumes.insert('', 'end', '', text='', values=(volume.nombre,
                                                                 volume.cantidadNumeros,
                                                                 volume.descripcion,
                                                                 volume.id,
                                                                 volume.image_url,
                                                                 volume.publisher_name,
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
    lk.buscarVolume()
    lk.treeview_sort_column(lk.grillaVolumes, 'name', False)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
