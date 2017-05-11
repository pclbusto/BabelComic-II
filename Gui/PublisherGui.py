from tkinter import *
from tkinter import Tk, ttk


class PublisherGui(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self.labelId = Label(self, text="ID")
        self.labelId.grid(row=0,column=0)
        self.entradaId = Entry(self)
        self.entradaId.grid(row=0,column=1, padx=5)
        self.labelDescripcion = Label(self, text="Descripción")
        self.labelDescripcion.grid(row=1,column=0)
        self.entradaDescripcion = Text(self)
        self.entradaDescripcion.grid(row=2, column=0, padx=5,columnspan=2)

        self.width =500
        self.height = 500

if __name__ == '__main__':
    root = Tk()
    publisher = PublisherGui(root, width=768, height=576)
    publisher.pack()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
