from PIL import Image, ImageTk
from tkinter import ALL, NW
from tkinter import Tk, Canvas

import Entidades.Init
from Entidades.Setups.Setup import Setup
from iconos.Iconos import Iconos

from rarfile import NotRarFile, BadRarFile
import os.path
import threading
from Entidades.ComicBooks.ComicBookDetail import ComicBookDetails



class PanelThumbnailComics(Canvas):
    def __init__(self, master, listaComics=None, session = None, cnf={}, **kw):
        Canvas.__init__(self, master, cnf, **kw)
        self.size = self.size = (int(320 / 2), int(496 / 2))
        self.space = 58
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.pahThumnails = self.session.query(Setup).first().directorioBase+ os.path.sep +"images"+os.path.sep +"coverIssuesThumbnails"+os.path.sep

        print(self.pahThumnails)

        print(self.size[0])
        self.listaComics = listaComics
        self.thumbnail = []
        self.comicsSelected=[]
        self.tagAndComic = []
        self.halfSize = (int(self.size[0] / 2), int(self.size[1] / 2))
        self.bind("<Button-1>", self.comicClicked)
        self.bind('<Shift-Button-1>', self.multipleComicsClicked)
        self.bind('<Control-Button-1>', self.addComicClicked)

        self.paginaDoblada = Iconos().pilImagePaginaDoblada
        self.cantidadColumnas = 6

    def __insertThumnail(self, X, Y, thumbnail, comic):
        self.create_rectangle(X + 3,
                              Y + 3,
                              X + self.size[0] + 3,
                              Y + self.size[1] + 3,
                              width=3)

        tag = self.create_image(X, Y, image=thumbnail, anchor=NW)
        self.create_text(X, Y + self.size[1] + 10, text=comic.getNombreArchivo(), fill='black', width=self.size[0],
                         anchor=NW)

        tagRect = self.create_rectangle(X,
                                        Y,
                                        X + self.size[0],
                                        Y + self.size[1],
                                        width=3)
        self.tagAndComic.append((tag, comic, X, Y, tagRect))

    def loadAndCreateThumbnails(self):
        x = 0
        y = 0
        print("cantidad de comics: ", len(self.listaComics))
        self.cantidadThumnailsAGenerar = len(self.listaComics)
        self.cantidadThumnailsGenerados = 0
        for comic in self.listaComics:
            self.cantidadThumnailsGenerados += 1
            try:
                comic.openCbFile()
                print(comic.path)
                nombreThumnail = self.pahThumnails + str(comic.comicId) + comic.getPageExtension()
                cover = None
                if (not os.path.isfile(nombreThumnail)):
                    cover = comic.getImagePage().resize(self.size, Image.BICUBIC)
                    cover.save(nombreThumnail)
                else:
                    cover = Image.open(nombreThumnail)
                    #print(nombreThumnail)
                iconos = Iconos()
                if (comic.comicVineId != ''):
                    comicvineLogo = Iconos().pilImageCataloged
                    cover.paste(comicvineLogo, (cover.size[0] - 64, cover.size[1] - 64, cover.size[0], cover.size[1]),
                                comicvineLogo)
                calidadIcon = None
                if (comic.calidad == 0):
                    calidadIcon = iconos.pilCalidadSinCalificacion
                if (comic.calidad == 1):
                    calidadIcon = iconos.pilCalidadMala
                if (comic.calidad == 2):
                    calidadIcon = iconos.pilCalidadMedia
                if (comic.calidad == 3):
                    calidadIcon = iconos.pilCalidadBuena
                if (comic.calidad == 4):
                    calidadIcon = iconos.pilCalidadDigital
                cover.paste(calidadIcon,(0,cover.size[1]-64),calidadIcon)

                tkimage = ImageTk.PhotoImage(cover)
                # self.thumbnail.append(ImageTk.PhotoImage(cover))
                self.thumbnail.append(tkimage)

                X = int(x * (self.size[0] + self.space))
                Y = int(y * (self.size[1] + self.space))
                self.__insertThumnail(X, Y, self.thumbnail[len(self.thumbnail) - 1], comic)
                x += 1
                if x % self.cantidadColumnas == 0:
                    y += 1
                    x = 0

            except NotRarFile:
                print('error en el archivo ' + comic.path)
            except BadRarFile:
                print('error en el archivo ' + comic.path)

        self.config(scrollregion=self.bbox(ALL))
        self.comicActual = 0

    def getComicActual(self):
        return self.tagAndComic[self.comicActual][1]

    def getComicAt(self, index):
        return self.tagAndComic[index][1]


    def thumbnailTurned(self):
        x = 0
        y = 0
        #self.config(scrollregion=panel.bbox(ALL))

    def nextComic(self):
        if (self.comicActual < len(self.tagAndComic) - 1):
            print('avanza')
            self.itemconfig(self.tagAndComic[self.comicActual][4], outline='black')
            self.comicActual += 1
            # recuperamos el rectangulos finito
            self.itemconfig(self.tagAndComic[self.comicActual][4], outline='blue')

    def prevComic(self):
        if (self.comicActual > 0):
            print('atras')
            self.itemconfig(self.tagAndComic[self.comicActual][4], outline='black')
            self.comicActual -= 1
            self.itemconfig(self.tagAndComic[self.comicActual][4], outline='blue')

    def deleteLista(self):
        del self.listaComics

    def loadComics(self, lista):
        print('loadComics: '+str(len(lista)))
        self.deleteLista()
        '''borramos todas las imagenes puestas en el canvas'''
        self.delete(ALL)
        self.listaComics = lista
        self.threadLoadAndCreateThumbnails = threading.Thread(target=self.loadAndCreateThumbnails)
        self.threadLoadAndCreateThumbnails.start()

    def __comicClicked__(self,event, multipleSelection):
        print("clicked at", event.x, event.y)
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        tagClicked = self.find_closest(x, y)[0]
        print(tagClicked)
        X = 0
        Y = 0
        for indice in range(0, len(self.tagAndComic)):
            tagComic = self.tagAndComic[indice]
            # for tagComic in self.tagAndComic:
            if tagClicked == tagComic[0]:
                if not multipleSelection:
                    for i in self.comicsSelected:
                        print("limpiando: " + str(i))
                        self.itemconfig(self.tagAndComic[i][4], outline='black')
                    self.comicsSelected.clear()
                    self.comicsSelected.append(indice)
                    self.comicActual = indice
                    self.itemconfig(tagComic[4], outline='blue')
                else:
                    if indice in self.comicsSelected:
                        self.comicsSelected.remove(indice)
                        self.comicActual = self.comicsSelected[len(self.comicsSelected)-1]
                        self.itemconfig(tagComic[4], outline='black')
                    else:
                        self.comicsSelected.append(indice)
                        self.comicActual = indice
                        self.itemconfig(tagComic[4], outline='blue')

        print("comic Actual: " + str(self.getComicActual()))

    def addComicClicked(self, event):
        self.__comicClicked__(event,True)

    def comicClicked(self, event):
        self.__comicClicked__(event=event, multipleSelection=False)
        # print("clicked at", event.x, event.y)
        # x = self.canvasx(event.x)
        # y = self.canvasy(event.y)
        # tagClicked = self.find_closest(x, y)[0]
        # print(tagClicked)
        # X = 0
        # Y = 0
        # for indice in range(0, len(self.tagAndComic)):
        #     tagComic = self.tagAndComic[indice]
        #     # for tagComic in self.tagAndComic:
        #     if tagClicked == tagComic[0]:
        #         for i in self.comicsSelected:
        #             print("limpiando: "+str(i))
        #             self.itemconfig(self.tagAndComic[i][4], outline='black')
        #         self.comicsSelected.clear()
        #         self.comicsSelected.append(indice)
        #         self.comicActual = indice
        #         self.itemconfig(tagComic[4], outline='blue')
        # print("comic Actual: "+str(self.getComicActual()))

    def multipleComicsClicked(self, event):
        print("multiple clicked at", event.x, event.y)
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        tagClicked = self.find_closest(x, y)[0]
        print(tagClicked)
        X = 0
        Y = 0
        for indice in range(0, len(self.tagAndComic)):
            tagComic = self.tagAndComic[indice]
            # for tagComic in self.tagAndComic:
            if tagClicked == tagComic[0]:
                # self.itemconfig(self.tagAndComic[self.comicActual][4], outline='black')
                self.comicsSelected.clear()
                '''vemos si el seleccionado es menor o mayor al seleccioando previamente para saber como marcar en azul'''
                if self.comicActual>indice:
                    print("Por aca")
                    for i in range(indice,self.comicActual+1):
                        self.comicsSelected.append(i)
                    for tag in self.tagAndComic[indice:self.comicActual]:
                        print("TAG: "+str(tag))
                        self.itemconfig(tag[4], outline='blue')
                else:
                    for i in range(self.comicActual,indice+1):
                        self.comicsSelected.append(i)
                    for tag in self.tagAndComic[self.comicActual:indice+1]:
                        print("TAG: "+str(tag))
                        self.itemconfig(tag[4], outline='blue')
        print(self.getComicActual())

    def recreateThumbnails(self):
        if self.comicActual is not None:
            comic = self.tagAndComic[self.comicActual][1]
            nombreThumnail = self.pahThumnails + str(comic.comicId) +comic.getPageExtension()
            print("Buscamos el archivo:{}".format(nombreThumnail))
            if (os.path.isfile(nombreThumnail)):
                print("encontramos el archivo")
                os.remove(nombreThumnail)
                '''revisamos si tiene cover configurada en la tabla de detalle comic'''
                cover = self.session.query(ComicBookDetails).filter(ComicBookDetails.comicId == comic.comicId).filter(
                    ComicBookDetails.tipoPagina == ComicBookDetails.COVER).first()
                if cover is not None:
                    comic.goto(cover.indicePagina)
                pagina = comic.getImagePage().resize(self.size, Image.BICUBIC)
                pagina.save(nombreThumnail)
                self.thumbnail.append(ImageTk.PhotoImage(pagina))
                self.delete(self.tagAndComic[self.comicActual][0])
                self.delete(self.tagAndComic[self.comicActual][4])
            X = int(self.tagAndComic[self.comicActual][2])
            Y = int(self.tagAndComic[self.comicActual][3])
            self.__insertThumnail(X, Y, self.thumbnail[len(self.thumbnail) - 1], comic)
            print('hay que borrar: ' + 'coversThumbnails' + os.path.sep + str(comic.comicId) + comic.getPageExtension())


def scrollupMouse(event):
    print("Hola")#panel.yview_scroll(-1 * (int)(event.delta / 120), "units")


def scrollupKeyboard(event):
    print(event.keycode)
    if (event.keycode == 116) | (event.keycode == 117) | (event.keycode == 34) | (event.keycode == 40):
        #panel.yview_scroll(1, "units")
        print('para abajo')
    if (event.keycode == 112) | (event.keycode == 111) | (event.keycode == 33) | (event.keycode == 38):
        #panel.yview_scroll(-1, "units")
        print('para abajo')
    # el 114 es en linux y el 39 en windows
    if (event.keycode == 114) | (event.keycode == 39):  # derecha
        print('para derecha')
        #panel.nextComic()
    # el 113 es en linux y el 37 en windows
    if (event.keycode == 113) | (event.keycode == 37):  # izquierda
        print('para izquierda')
        #panel.prevComic()


if (__name__ == '__main__'):
    #lista = ComicBooks().list(('%flash%',), 'path like ?', )
    root = Tk()
    # for comic in lista:
    #    print(comic.rowId)

    '''scrollbarY = ttk.Scrollbar(root)
    panel = PanelThumbnailComics(root,lista,yscrollcommand=scrollbarY.set)
    #panel.loadComics(lista)
    #panel.thumbnailTurned()
    panel.loadAndCreateThumbnails()
    scrollbarY.config(command=panel.yview)
    scrollbarY.grid(column=1,row=0,sticky=(N,S))
    panel.grid(column=0,row=0,sticky=(N,S,W,E))
    panel.bind('<MouseWheel>', scrollupMouse)
    root.bind('<Down>', scrollupKeyboard)
    root.bind('<Key>', scrollupKeyboard)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0,weight=1)
    root.mainloop()'''
