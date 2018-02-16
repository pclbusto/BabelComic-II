import Entidades.Init
from Entidades.ComicBooks import ComicBook

from kivy.app import App
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.uix.image import Image
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.carousel import Carousel

import os

class Comic(Screen):

    def __init__(self, comic=None, **kwargs):
        super(Comic, self).__init__(**kwargs)
        self.layout = FloatLayout()
        self.image_cover = Image(allow_stretch=True)
        #self.loadImageCover('Sin Caratula.jpg')
        self.image_cover.size_hint = (None, None)
        self.image_cover.size = (160,248)
        self.image_cover.pos_hint = {'top': 1, 'left': 1}

        self.layout.add_widget(self.image_cover)
        self.labelDescripcion = TextInput()
        self.labelDescripcion.size_hint = (.7, 0.5)
        self.labelDescripcion.pos_hint = {'top': 1, 'right': 1}
        self.labelDescripcion.readonly = True
        self.layout.add_widget(self.labelDescripcion)
        self.setComic(comic)
        self.loadComic()
        self.add_widget(self.layout)
        self.name = str(comic.comicId)

    def getFirst(self):
        comic = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()).first()
        if comic is not None:
            print(comic)
            self.setComic(comic)
            self.loadComic()

    def loadImageCover(self,imagePath):
        curpath = os.getcwd()
        os.chdir("..")
        path = os.path.join(os.getcwd(), 'images')
        path = os.path.join(path, 'coverIssuesThumbnails')
        path = os.path.join(path, imagePath)
        self.image_cover.source = path
        self.image_cover.reload()
        os.chdir(curpath)

    def setComic(self,comicBook):
        self.comic = comicBook

    def loadComic(self):
        self.loadImageCover(str(self.comic.comicId) + '.jpg')
        self.labelDescripcion.text = self.comic.resumen
        self.name=str(self.comic.comicId)

class ComicManager(ScreenManager):
    CANTIDAD_SLIDES = 2
    def __init__(self, session=None, **kwargs):

        super(ComicManager, self).__init__(**kwargs)
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.comics = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()).limit(ComicManager.CANTIDAD_SLIDES*2).all()
        self.indice = 0
        self.more_left = True
        self.more_right = True
        self.comic_screens =[]
        for comic in self.comics:
            self.comic_screens.append(Comic(comic))
        print(self.comics)
        self.switch_to(self.comic_screens[self.indice])

    def on_touch_up(self, args):
        print(self.indice)
        print("COMICS {}".format(self.screens))
        sl = SlideTransition()
        if args.dpos[0] < 0:
            if self.indice == (2 * ComicManager.CANTIDAD_SLIDES) - 1 or self.indice == len(self.comics) - 1:
                print("AGREGANDO NUEVOS CMICS")
                print(self.comics)
                comic_path = self.comics[self.indice].path
                lista = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()). \
                    filter(ComicBook.ComicBook.path >= comic_path).limit(int(2*ComicManager.CANTIDAD_SLIDES)).all()
                if len(lista) > 1:
                    print("COMICS {}".format(self.screens))
                    self.comics.clear()
                    self.comic_screens.clear()
                    print("****LISTAS******")
                    self.comics = lista
                    print(self.comics)
                    for comic in self.comics:
                        self.comic_screens.append(Comic(comic))
                    self.indice = 1
                else:
                    self.more_right = False
            if self.more_right:
                print("POR ACAAAAAAAAAAAAAAAA")
                sl.direction = 'left'
                self.transition = sl
                self.indice += 1
                self.switch_to(self.comic_screens[self.indice], direction='left')
        if args.dpos[0] > 0:
            if self.indice == 0:
                print("AGREGANDO NUEVOS CMICS")
                print(self.comics)
                comic_path = self.comics[self.indice].path
                lista = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()). \
                    filter(ComicBook.ComicBook.path <= comic_path).limit(int(2*ComicManager.CANTIDAD_SLIDES)).all()
                if len(lista) > 1:
                    print("COMICS {}".format(self.screens))
                    self.comics.clear()
                    self.comic_screens.clear()
                    print("****LISTAS******")
                    self.comics = lista
                    print(self.comics)
                    for comic in self.comics.reverse():
                        self.comic_screens.append(Comic(comic))
                    self.indice = 3
                else:
                    self.more_left = False
            if self.more_left:
                self.transition = sl
                self.indice -= 1
                self.switch_to(self.comic_screens[self.indice], direction='right')
class KComicBookGuiapp(App):
    def build(self):
        return ComicManager()


if __name__ == '__main__':
    session = Entidades.Init.Session()
    comic =ComicBook.ComicBook()
    KComicBookGuiapp().run()


