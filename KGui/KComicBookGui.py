import Entidades.Init
from Entidades.ComicBooks import ComicBook

from kivy.app import App
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.uix.image import Image
from kivy.uix.widget import Widget
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

class ComicManager(Carousel):
    CANTIDAD_SLIDES = 2
    def __init__(self, session=None, **kwargs):
        super(ComicManager, self).__init__(**kwargs)
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()
        self.comics = self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()).limit(ComicManager.CANTIDAD_SLIDES*2).all()
        for comic in self.comics:
            self.add_widget(Comic(comic))
        print(self.comics)
    def on_current_slide(self, *args):
        print(self.index)
        print(self.slides[self.index].comic.comicId)
        if self.index == (ComicManager.CANTIDAD_SLIDES*2)-1:
            self.clear_widgets()
            self.comics.clear()

            print(self.index)
            print(self.comics)
            comic_path = self.comics[self.index].path
            print(comic_path)
            for i in range(int(ComicManager.CANTIDAD_SLIDES)):
                self.remove_widget(self.slides[0])
                self.comics.pop(0)
            self.comics.extend(self.session.query(ComicBook.ComicBook).order_by(ComicBook.ComicBook.path.asc()).\
               filter(ComicBook.ComicBook.path > comic_path).limit(int(ComicManager.CANTIDAD_SLIDES)).all())
            for comic in self.comics:
               self.add_widget(Comic(comic))
            self.index=CANTIDAD_SLIDES-1
            print(self.index)
            print(self.comics)




class KComicBookGuiapp(App):
    def build(self):
        return ComicManager()


if __name__ == '__main__':
    session = Entidades.Init.Session()
    comic =ComicBook.ComicBook()
    KComicBookGuiapp().run()


