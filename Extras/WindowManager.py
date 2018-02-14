from tkinter import Tk, ttk
from tkinter import *
from Gui.VolumeGui import VolumeGui
from Gui.PublisherGui import PublisherGui

diccionarioVentanas = {}


def on_closing(window):

    del diccionarioVentanas[window.title()]
    window.destroy()
def openVolumen(Titulo=None, session = None):
    if Titulo!='Volumen':
        print("Error no se Window manager no soporta la ventana {}".format(Titulo))
    if session is None:
        print("Error el parametro session no puede ser vacío o nulo")
    ventana =  diccionarioVentanas.get(Titulo)
    if ventana is not None:
        ventana.lift()
    else:
        window = Toplevel()
        window.geometry("+0+0")
        window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
        window.wm_title(string=Titulo)
        volumenGui = VolumeGui(window, session=session)
        volumenGui.grid(sticky=(N, S, E, W))


def openPublisher(Titulo=None, session = None):
    if Titulo!='Editorial':
        print("Error no se Window manager no soporta la ventana {}".format(Titulo))
    if session is None:
        print("Error el parametro session no puede ser vacío o nulo")
    ventana =  diccionarioVentanas.get(Titulo)
    if ventana is not None:
        ventana.lift()
    else:
        window = Toplevel()
        window.geometry("+0+0")
        window.wm_title(string="Editorial")
        window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
        publisherGui = PublisherGui(window, session=session)
        publisherGui.grid(sticky=(N, S, E, W))
        diccionarioVentanas[Titulo] = window


def openWindow(Titulo=None, session = None):
    if Titulo!='Editorial':
        print("Error no se Window manager no soporta la ventana {}".format(Titulo))
    if session is None:
        print("Error el parametro session no puede ser vacío o nulo")
    ventana =  diccionarioVentanas.get(Titulo)
    if ventana is not None:
        ventana.lift()
    else:
        window = Toplevel()
        window.geometry("+0+0")
        window.wm_title(string=Titulo)
        window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
        panel = None
        if Titulo=='Volumen':
            panel = VolumeGui(window, session=session)
        if Titulo=='Editorial':
            panel = PublisherGui(window, session=session)
        panel.grid(sticky=(N, S, E, W))
        diccionarioVentanas[Titulo] = window