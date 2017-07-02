import zipfile
from tkinter import *
from PIL import Image, ImageTk
from tkinter import Tk,ttk
from tkinter import filedialog
import Entidades.Init
from Entidades.ComicBooks.ComicBook import ComicBook



class ComicVisorGui(Toplevel):
    def __init__(self,master,comicBook=None,cnf={},**kw):
        Toplevel.__init__(self,master,cnf,**kw)
        if not comicBook:
           self.comicBook =  ComicBook('BabelComics.cbz')
        else:
            self.comicBook = comicBook
        self.idImagen = None
        self.tipoAjuste = IntVar()
        self.tipoAjuste.set(3)
        self.title('Babel Comic Visor')
        self.crearMenu()
        self.mainframe = ttk.Frame(self)
        self.scrollbarY = Scrollbar(self.mainframe)
        self.scrollbarX = Scrollbar(self.mainframe)

        self.canvas = Canvas(self.mainframe, yscrollcommand=self.scrollbarY.set, xscrollcommand=self.scrollbarX.set)

        self.comicBook.openCbFile()
        #self.fImage= self.comicBook.getImagePage()
        self.im = self.comicBook.getImagePage()
        self.myimg = ImageTk.PhotoImage(self.im)
        self.contadorFondo = 0
        self.cargarPagina()
        self.update()
        self.ajustarAncho()
        ##canvas.create_image(0,0,image=myimg)

        self.canvas.bind('<MouseWheel>', self.scrollupMouse)
        self.bind('<Up>', self.scrollupKeyboard)
        self.bind('<Down>', self.scrollupKeyboard)
        self.bind('<Left>', self.scrollupKeyboard)
        self.bind('<Right>', self.scrollupKeyboard)
        self.bind('<Prior>', self.scrollupKeyboard)
        self.bind('<Next>', self.scrollupKeyboard)
        self.bind('<Key>', self.scrollupKeyboard)
        self.bind('<Key>', self.scrollupKeyboard)
        self.bind('<space >', self.scrollupKeyboard)

        self.scrollbarY.config(command=self.canvas.yview)
        self.scrollbarX.config(command=self.canvas.xview)
        self.bind("<Button-1>",self.click)
        self.canvas.pack(side=BOTTOM, expand=YES, fill=BOTH)

        ##Tener cuidado cuando se hace el pack no se puede hacer en cualquier orden
        self.mainframe.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))


    def click(self,event):
        if (event.x>self.winfo_width()/2):
            event.keycode=117
            self.scrollupKeyboard(event)
        else:
            event.keycode=112
            self.scrollupKeyboard(event)

        print(self.winfo_width())
        print("clicked: "+str(event.x))


    def abrirComic(self):
        global comic,indicePaginaActual,paginas
        cbz = filedialog.askopenfile('r',initialdir='/home/pedro/Descargas/ftp/',filetypes = [("comic","*.cbz")])
    ##    cbz = filedialog.askopenfile('r',initialdir='.',filetypes = [("comic","*.cbz")])
        print(cbz)
        if cbz:
            comic = zipfile.ZipFile(cbz.name,'r')
            paginas.clear()
            paginas = [x for x in comic.namelist() if(x[-3:]=='jpg' or x[-3:]=='png')]
            indicePaginaActual=0
            self.cargarPagina()

    def salir(self):
        comic.close()
        root.destroy()

    def ajustarAncho(self):
        #global tipoAjuste
        self.tipoAjuste.set(1)
        self.cargarPagina()
    def ajustarAlto(self):
        #global tipoAjuste
        self.tipoAjuste.set(2)
        self.cargarPagina()
    def ajustarNormal(self):
        #global tipoAjuste
        self.tipoAjuste.set(3)
        self.cargarPagina()

    def crearMenu(self):
        #global tipoAjuste
        self.menu = Menu(self)
        self.submenuArchivo = Menu(self.menu, tearoff=0)
        self.submenuArchivo.add_command(label = 'Abrir Comic', command = self.abrirComic, accelerator = 'o')
        self.submenuArchivo.add_command(label = 'Salir', command = self.salir, accelerator = 'q')
        self.submenuImagen = Menu(self.menu, tearoff=0)
        self.submenuImagen.add('radiobutton',variable=self.tipoAjuste,label='ajustar al ancho',command=self.ajustarAncho,accelerator = 'w',value=1)
        self.submenuImagen.add('radiobutton',variable=self.tipoAjuste,label='ajustar al alto',command=self.ajustarAlto,accelerator = 'h',value=2)
        self.submenuImagen.add('radiobutton',variable=self.tipoAjuste,label='tamaño normal',command=self.ajustarNormal,accelerator = 'n',value=3)
        self.menu.add_cascade(label = 'Archivo',menu=self.submenuArchivo)
        self.menu.add_cascade(label = 'Imagen',menu=self.submenuImagen)
        self.config(menu=self.menu)



    def scrollupMouse(self,event):
        self.canvas.yview_scroll(-1*(int)(event.delta/120), "units")

    def scrollupKeyboard(self,event):
        print(event.keycode)
        #si es spacebar
        print(self.scrollbarY.get()[1])
        if((event.keycode== 65 or event.keycode==116) and self.scrollbarY.get()[1]==1):
            print(self.contadorFondo)
            self.contadorFondo+=1
            if self.contadorFondo>2:
                print('cambiamos el event')
                event.keycode = 117
                print('cambiamos el event')

        if (event.keycode== 111)|(event.keycode== 38):
            self.canvas.yview_scroll(-1, "units")
            self.contadorFondo = 0
        elif (event.keycode== 116)|(event.keycode== 40)|(event.keycode== 65):
            self.canvas.yview_scroll(1, "units")
        elif (event.keycode== 113)|(event.keycode== 37):
            self.canvas.xview_scroll(-1, "units")
            self.contadorFondo = 0
        elif (event.keycode== 114)|(event.keycode== 39):
            self.canvas.xview_scroll(1, "units")
        elif (event.keycode == 117)|(event.keycode == 34):
            #pag down
            self.contadorFondo = 0
            self.comicBook.indicePaginaActual+=1
            self.comicBook.goto(self.comicBook.indicePaginaActual)
            self.cargarPagina()
        elif (event.keycode == 112)|(event.keycode == 33):
            # pag up
            self.comicBook.indicePaginaActual-=1
            self.comicBook.goto(self.comicBook.indicePaginaActual)
            self.cargarPagina()
    ##  q Key normal
        elif (event.keysym == 'q'):
            self.salir()
    ##  w Key ancho
        elif (event.keysym == 'w'):
            self.ajustarAncho()
    ##  h Key altura
        elif (event.keysym == 'h'):
            self.ajustarAlto()
    ##  n Key quit
        elif (event.keysym == 'n'):
            self.ajustarNormal()
    ##  o Key open
        elif (event.keysym == 'o'):
            self.abrirComic()
    ##  g Key open
        elif (event.keycode == 1):
            print(event.keycode)
        print(event.keysym)

    def cargarPagina(self):
        # global canvas,myimg,idImagen,mainframe
        alturaImagen=anchoImagen=0
        self.canvas.update()
        self.alturaFrame=self.winfo_height()
        self.anchoFrame=self.winfo_width()
        print('indice pagina:',self.comicBook.indicePaginaActual)
        fImage = self.comicBook.getImagePage()
        im = self.comicBook.getImagePage()
        tasa = 1
        if (self.tipoAjuste.get()==2):
            tasa= self.alturaFrame/im.height
        elif (self.tipoAjuste.get()==1):
            tasa= self.anchoFrame/im.width
        elif (self.tipoAjuste.get()==3):
            tasa=1

        size = (int)(im.width*tasa),(int)(im.height*tasa)
        im=im.resize(size,Image.BICUBIC)
        self.myimg = ImageTk.PhotoImage(im)
        if self.idImagen:
            self.canvas.delete(self.idImagen)
        self.idImagen = self.canvas.create_image(0,0,image=self.myimg,anchor=CENTER)
    ##cuidado cuando seteamos esto. Si lo ponemodes despues de cargar una imagen,
    ##es como que el box se fija al tamañio de la imagen
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.canvas.yview_moveto(0.0)

if __name__=='__main__':
    root = Tk()
    #comicBook = E
    #comic = ComicBooks().get('C:\\Users\\pclbu\\Documents\\Comics\\Green Lantern 047 (2016) (Digital-Empire).cbr')
    visor = ComicVisorGui(root,comic)
    visor.title = ('Babel Comics Visor')
    root.mainloop()
