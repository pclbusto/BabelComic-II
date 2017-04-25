from tkinter import *
from tkinter import Tk, ttk
from PIL import Image, ImageTk



class PublisherGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        #self.title("Editorial")
        self.labelId = Label(self, text="ID")
        self.labelId.grid(row=0, sticky=W)
        self.labelNombre = Label(self, text="Nombre")
        self.labelNombre.grid(row=1, sticky=W)
        self.labelDeck = Label(self, text="deck")
        self.labelDeck.grid(row=2, sticky=W)
        self.labelDescripcion = Label(self, text="Descripción")
        self.labelDescripcion.grid(row=3, sticky=W)

        self.entryId = Entry(self)
        self.entryId.grid(row=0, column=1, sticky=W+E, padx=2, pady=2)
        self.entryNombre = Entry(self)
        self.entryNombre.grid(row=1, column=1, sticky=W+E, padx=2, pady=2)
        self.entryDeck = Entry(self)
        self.entryDeck.grid(row=2, column=1, sticky=W+E, padx=2, pady=2)
        self.entryDescription = Text(self)
        self.entryDescription.grid(row=4, column=0, sticky=N,columnspan=4, padx=2, pady=2)
        self.columnconfigure(1,weight=1)

        image = Image.open("C:\\Users\\pclbu\\PycharmProjects\\BabelComic-II\\Imagenes\\publishers\\logos\\5213245-dc_logo_blue_final.jpg")
        image = image.resize((100,100),Image.LANCZOS)

        iconSearch = Image.open("..\\iconos\\Magnifying-Glass-icon.png")
        iconSearchPhoto = ImageTk.PhotoImage(iconSearch)
        self.botonLookupId = Button(image=iconSearchPhoto)
        self.botonLookupId.grid(column=2, row=0)
        photo = ImageTk.PhotoImage(image)
        self.labelLogo = Label(self, image=photo)
        self.labelLogo.image = photo
        self.labelLogo.grid(column=2, row=0, columnspan=2, rowspan=2,padx=2, pady=2)
        self.geometrioa = "500x500+0+0"
if __name__ == '__main__':
    root = Tk()
    #root.wm_geometry("500x500+0+0")
    publisher = PublisherGui(root)
    publisher.pack()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
