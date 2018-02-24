import Entidades.Init
from Entidades.ComicBooks import ComicBook

from kivy.app import App
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.uix.image import Image
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.carousel import Carousel
from kivy.uix.button import Button

import os

class Comic(Screen):

    def __init__(self, comic=None, **kwargs):
        super(Comic, self).__init__(**kwargs)
        self.layout = FloatLayout()
        self.image_cover = Image(allow_stretch=True)
        #self.loadImageCover('Sin Caratula.jpg')
        self.image_cover.size_hint = (0.2, 0.5)
        #self.image_cover.size = (160,248)
        self.image_cover.pos_hint = {'top': 1, 'left': 1}

        self.layout.add_widget(self.image_cover)
        self.labelDescripcion = TextInput()
        self.labelDescripcion.size_hint = (.8, 0.5)
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

class ComicManager(Carousel):
    CANTIDAD_SLIDES = 2
    def __init__(self, session=None, **kwargs):

        super(ComicManager, self).__init__(**kwargs)
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.comics = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()).\
            limit(ComicManager.CANTIDAD_SLIDES*2).all()
        self.indice = 0
        self.more_left = True
        self.more_right = True
        self.procesing = False
        for comic in self.comics:
            screen_comic = Comic(comic)
            self.add_widget(screen_comic)
        print(self.procesing)

    # def on_index(self, *args):
    #     a = 1

    def on_next_slide(self, *args):
        if not self.procesing:
            self.procesing = True
        else:
            return

        if self.next_slide is None and self.previous_slide is not None and self.index == (2*ComicManager.CANTIDAD_SLIDES) - 1:
            print("Cargar Proximos")
            comic_path = self.comics[self.index].path
            lista = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()). \
                filter(ComicBook.ComicBook.path > comic_path).limit(int(ComicManager.CANTIDAD_SLIDES)).all()
            if len(lista) > 0:
                self.clear_widgets()
                print("COMICS Proximos  Antes{}".format(self.comics))
                for comic in lista:
                    comic_screen = Comic(comic)
                    self.comics.pop(0)
                    self.comics.append(comic)
                print("COMICS Proximos despues{}".format(self.comics))
                for comic in self.comics:
                    self.add_widget(Comic(comic))
                self.index = ComicManager.CANTIDAD_SLIDES - 1
        self.procesing = False

    def on_previous_slide(self, *args):
        if not self.procesing:
            self.procesing = True
        else:
            return

        if self.previous_slide is None and self.next_slide is not None and self.index == 0:
            print("Cargar Anteriores")
            comic_path = self.comics[self.index].path
            lista = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.desc()). \
                filter(ComicBook.ComicBook.path < comic_path).limit(int(ComicManager.CANTIDAD_SLIDES)).all()
            if len(lista) > 0:
                self.clear_widgets()
                print("COMICS Anteriores Antes{}".format(self.comics))
                for comic in lista:
                    comic_screen = Comic(comic)
                    self.comics.pop()
                    self.comics.insert(0, comic)
                print("COMICS Anteriores despues{}".format(self.comics))
                for comic in self.comics:
                    self.add_widget(Comic(comic))
                self.index = ComicManager.CANTIDAD_SLIDES
        self.procesing = False
    #     if self.previous_slide is None:
    #         print("on_previous_slide")
    # def on_index(self, *args):
    #     print(self.index)
    #     if (self.index == (2 * ComicManager.CANTIDAD_SLIDES) - 1) or (self.index == 0):
    #         print("Hacer algo")

    # def on_touch_up(self, args):
    #      print("Indce {}".format(self.index))
    #     print("COMICS {}".format(self.screens))
    #     sl = SlideTransition()
    #     if args.dpos[0] < 0:
    #         if self.indice == (2 * ComicManager.CANTIDAD_SLIDES) - 1 or self.indice == len(self.comics) - 1:
    #             print("AGREGANDO NUEVOS CMICS")
    #             print(self.comics)
    #             comic_path = self.comics[self.indice].path
    #             lista = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()). \
    #                 filter(ComicBook.ComicBook.path >= comic_path).limit(int(2*ComicManager.CANTIDAD_SLIDES)).all()
    #             if len(lista) > 1:
    #                 print("COMICS {}".format(self.screens))
    #                 self.comics.clear()
    #                 self.comic_screens.clear()
    #                 print("****LISTAS******")
    #                 self.comics = lista
    #                 print(self.comics)
    #                 for comic in self.comics:
    #                     self.comic_screens.append(Comic(comic))
    #                 self.indice = 1
    #             else:
    #                 self.more_right = False
    #         if self.more_right:
    #             print("POR ACAAAAAAAAAAAAAAAA")
    #             sl.direction = 'left'
    #             self.transition = sl
    #             self.indice += 1
    #             self.switch_to(self.comic_screens[self.indice], direction='left')
    #     if args.dpos[0] > 0:
    #         if self.indice == 0:
    #             print("AGREGANDO Comics izquieda")
    #             print(self.comics)
    #             comic_path = self.comics[self.indice].path
    #             lista = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()). \
    #                 filter(ComicBook.ComicBook.path <= comic_path).limit(int(2*ComicManager.CANTIDAD_SLIDES)).all()
    #             if len(lista) > 1:
    #                 print("COMICS {}".format(self.screens))
    #                 self.comics.clear()
    #                 self.comic_screens.clear()
    #                 print("****LISTAS******")
    #                 self.comics = lista
    #                 print(self.comics)
    #                 for comic in self.comics.reverse():
    #                     self.comic_screens.append(Comic(comic))
    #                 self.indice = 3
    #             else:
    #                 self.more_left = False
    #         if self.more_left:
    #             self.transition = sl
    #             self.indice -= 1
    #             self.switch_to(self.comic_screens[self.indice], direction='right')
class KComicBookGuiapp(App):
    def build(self):
        return ComicManager()


if __name__ == '__main__':
    session = Entidades.Init.Session()
    comic =ComicBook.ComicBook()
    KComicBookGuiapp().run()


