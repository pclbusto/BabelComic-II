import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
import Entidades.Init
from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Setups.Setup import Setup
import os.path
from PIL import Image
from rarfile import NotRarFile, BadRarFile

icons = ["edit-cut", "edit-paste", "edit-copy"]

class IconViewWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.maximize()
        self.session = Entidades.Init.Session()
        self.listaComics = self.session.query(ComicBook).all()

        self.pahThumnails = self.session.query(Setup).first().directorioBase + os.path.sep + "images" + os.path.sep + \
                            "coverIssuesThumbnails" + os.path.sep

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.set_default_size(200, 200)

        self.liststore = Gtk.ListStore(Pixbuf, str)
        iconview = self.loadAndCreateThumbnails()
        iconview.set_model(self.liststore)
        iconview.set_pixbuf_column(0)
        iconview.set_text_column(1)

        # for icon in icons:
        #     pixbuf = Gtk.IconTheme.get_default().load_icon(icon, 64, 0)
        #     self.liststore.append([pixbuf, "Label"])

        scrolled.add(iconview)
        self.add(scrolled)
        iconview.set_spacing(1)
        print (iconview.get_spacing())
        header = Gtk.HeaderBar()
        boton = Gtk.Button(label = 'test')
        header.pack_end(boton)
        self.set_titlebar(header)

    def loadAndCreateThumbnails(self):
        iconview = Gtk.IconView.new()
        iconview.set_model(self.liststore)
        iconview.set_pixbuf_column(0)
        iconview.set_text_column(1)


        print("cantidad de comics: ", len(self.listaComics))
        self.cantidadThumnailsAGenerar = len(self.listaComics)
        self.cantidadThumnailsGenerados = 0
        for comic in self.listaComics:
            self.cantidadThumnailsGenerados += 1
            try:
                comic.openCbFile()
                # print(comic.path)
                nombreThumnail = self.pahThumnails + str(comic.comicId) + comic.getPageExtension()
                cover = None
                if (not os.path.isfile(nombreThumnail)):
                    imagen_height_percent = 150/comic.getImagePage().size[1]
                    self.size = self.size = (int(imagen_height_percent*comic.getImagePage().size[0]), int(150))

                    cover = comic.getImagePage().resize(self.size, Image.LANCZOS)
                    cover.save(nombreThumnail)

                    cover = Pixbuf.new_from_file(nombreThumnail)
                    self.liststore.append([cover, comic.getNombreArchivo()])
                else:
                    print(nombreThumnail)
                    cover = Pixbuf.new_from_file(nombreThumnail)
                    self.liststore.append([cover, comic.getNombreArchivo()])

                    #print(nombreThumnail)
            #     iconos = Iconos()
            #     if (comic.comicVineId != ''):
            #         comicvineLogo = Iconos().pilImageCataloged
            #         cover.paste(comicvineLogo, (cover.size[0] - 64, cover.size[1] - 64, cover.size[0], cover.size[1]),
            #                     comicvineLogo)
            #     calidadIcon = None
            #     if (comic.calidad == 0):
            #         calidadIcon = iconos.pilCalidadSinCalificacion
            #     if (comic.calidad == 1):
            #         calidadIcon = iconos.pilCalidadMala
            #     if (comic.calidad == 2):
            #         calidadIcon = iconos.pilCalidadMedia
            #     if (comic.calidad == 3):
            #         calidadIcon = iconos.pilCalidadBuena
            #     if (comic.calidad == 4):
            #         calidadIcon = iconos.pilCalidadDigital
            #     cover.paste(calidadIcon,(0,cover.size[1]-64),calidadIcon)
            #
            #     tkimage = ImageTk.PhotoImage(cover)
            #     # self.thumbnail.append(ImageTk.PhotoImage(cover))
            #     self.thumbnail.append(tkimage)
            #
            #     X = int(x * (self.size[0] + self.space))
            #     Y = int(y * (self.size[1] + self.space))
            #     self.__insertThumnail(X, Y, self.thumbnail[len(self.thumbnail) - 1], comic)
            #     x += 1
            #     if x % self.cantidadColumnas == 0:
            #         y += 1
            #         x = 0
            #
            except NotRarFile:
                print('error en el archivo ' + comic.path)
            except BadRarFile:
                print('error en el archivo ' + comic.path)
        #esto hace que no sean tan ancho los thumnails
        iconview.set_item_width(1)
        return iconview
        # self.config(scrollregion=self.bbox(ALL))
        # self.comicActual = 0

win = IconViewWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
