import Entidades.Init
from Entidades.ComicBooks import ComicBook

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import os

class Comic(Screen):
    # def build(self):
    #     return Builder.load_file('KComicBookGui.kv')
    def __init__(self, session=None, **kwargs):
        super(Comic, self).__init__(**kwargs)
        if session is not None:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

        self.layout = FloatLayout()
        self.image_cover = Image(allow_stretch=True)
        # self.image_cover.size_hint = (None, None)
        self.loadImageCover('Sin Caratula.jpg')
        self.image_cover.size_hint = (None, None)
        self.image_cover.size = (160,248)
        self.image_cover.pos_hint = {'top': 1, 'left': 1}

        self.layout.add_widget(self.image_cover)
        self.labelDescripcion = TextInput()
        self.labelDescripcion.size_hint = (.7, 0.5)
        self.labelDescripcion.pos_hint = {'top': 1, 'right': 1}
        self.labelDescripcion.readonly = True
        self.layout.add_widget(self.labelDescripcion)
        self.add_widget(self.layout)
        self.getFirst()
        print(self.size)

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
        # self.image_cover = Image(source=path)
        self.loadImageCover(str(self.comic.comicId) + '.jpg')
        self.labelDescripcion.text = self.comic.resumen


class KComicBookGuiapp(App):
    def build(self):
        return Comic()


if __name__ == '__main__':
    session = Entidades.Init.Session()
    comic =ComicBook.ComicBook()
    KComicBookGuiapp().run()


