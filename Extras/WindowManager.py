from tkinter import Tk, ttk
from tkinter import *
from Gui.VolumeGui import VolumeGui

diccionarioVentanas = {}


def openWindow(Titulo=None, session = None):
    if Titulo not in ['Volumen']:
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
        volumenGui = VolumeGui(window, session=session)
        volumenGui.grid(sticky=(N, S, E, W))
        diccionarioVentanas[Titulo]=window