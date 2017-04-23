from tkinter import *
from tkinter import Tk, ttk


class PublisherGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self.labelId = Label(self, text="ID")
        self.labelId.pack()
        self.labelNombre = Label(self, text="Nombre")
        self.labelNombre.pack()
        self.labelDeck = Label(self, text="deck")
        self.labelDeck.pack()
        self.labelDescripcion = Label(self, text="Descripción")
        self.labelDescripcion.pack()

if __name__ == '__main__':
    root = Tk()
    publisher = PublisherGui(root)
    publisher.pack()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
