from tkinter import *
from tkinter import Tk, ttk


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
        self.entryId.grid(row=0, column=1, sticky=W+E)
        self.entryNombre = Entry(self)
        self.entryNombre.grid(row=1, column=1, sticky=W+E)
        self.entryDeck = Entry(self)
        self.entryDeck.grid(row=2, column=1, sticky=W+E)
        self.entryDescription = Text(self)
        self.entryDescription.grid(row=4, column=0, sticky=N,columnspan=2)
        self.columnconfigure(1,weight=1)
        self.geometrioa = "500x500+0+0"
if __name__ == '__main__':
    root = Tk()
    #root.wm_geometry("500x500+0+0")
    publisher = PublisherGui(root)
    publisher.pack()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
