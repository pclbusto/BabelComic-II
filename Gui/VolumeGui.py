from tkinter import *
from tkinter import Tk, ttk, Frame
import PIL.Image, PIL.ImageTk
from iconos import Iconos
from Entidades.Volumes.Volume import Volume
from Gui.FrameMaestro import FrameMaestro



class PublisherGui(FrameMaestro):
    def __init__(self, parent, comicBook, cnf={}, **kw):
        FrameMaestro.__init__(self, parent, cnf, **kw)