#!/usr/bin/env python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

import urllib.request
import re
from zipfile import ZipFile
from zipfile import ZIP_STORED
import os
import threading
import time

class ReadAcomicParser():
    listaUrlNombreArchivo = None
    html=''
    nombreComic = ''
    itemActualProcesando = None
    porcentajeDescargado = 0.0
    porcentajeCompreso = 0.0

    stopFlag = False

    def __init__(self, html, cnf={}, **kw):
        self.html = html
        self.parserHtml()
        # self.listaUrlNombreArchivo = listaUrlNombreArchivo

    def parserHtml(self):
        listaCaracteresInvalidos=["/", "\\", ":"]
        #Obtenemos el nombre del comic que vamos a crear
        t = re.findall('<meta name\="keywords" content\=(.*)\"', self.html)
        self.nombreComic = t[0][(t[0].rfind(","))+1:] + ".cbz"
        self.nombreComic = str.strip(self.nombreComic)
        for caracter in listaCaracteresInvalidos:
            self.nombreComic = self.nombreComic.replace(caracter, "-")
        #parseamos el html para sacar las imagenes que hay que bajar
        self.listaUrlNombreArchivo=[]
        # self.listaUrlNombreArchivo.clear()
        m = re.findall('lstImages.push\("(.*)\);', self.html)
        index = 1
        for match in m:
            pos = match.rfind("/")
            nombreArchivo = match[pos + 1:-1]
            # si no es punto asumo
            if nombreArchivo[-4:-3] != '.':
                nombreArchivo = "pagina" + str(index).zfill(3) + ".jpg"
            url = match[:-1]
            self.listaUrlNombreArchivo.append((url, nombreArchivo, index))
            index += 1

    def downloadImages(self):
        self.porcentajeDescargado = 0
        for item in self.listaUrlNombreArchivo:
            while True:
                try:
                    self.itemActualProcesando = item
                    jpg = urllib.request.urlopen(item[0])
                    imagen = jpg.read()
                    f = open(item[1], "wb")
                    f.write(imagen)
                    f.close()
                    self.porcentajeDescargado = item[2]/len(self.listaUrlNombreArchivo)
                    print("porcentaje descarga {}".format(self.porcentajeDescargado))
                    if self.stopFlag:
                        break
                except ConnectionResetError:
                    print("Cortaron la conexion")
                    continue
                break
        self.porcentajeProcesado=100.0
        self.stopFlag=False

    def stop(self):
        self.stopFlag=True

    def createCbzFile(self):
        zip = ZipFile(self.nombreComic, "w", ZIP_STORED)
        self.porcentajeCompreso = 0
        for item in self.listaUrlNombreArchivo:
            zip.write(item[1])
            self.porcentajeCompreso = item[2] / len(self.listaUrlNombreArchivo)
            print("porcentaje comprimido {}".format(self.porcentajeCompreso))
        zip.close()
        self.porcentajeCompreso = 100.0
        for item in self.listaUrlNombreArchivo:
            os.remove(item[1])


class DownloaderWindow(Gtk.Window):

    lista_comics = Gtk.ListStore(str, int, float)
    lista_item_for_parsing= []

    stopFlag= False
    itemActualProcesando= None
    parserActualProcesando= None

    def __init__(self, **kw):
        Gtk.Window.__init__(self, **kw)
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)
        self.listViewComics = Gtk.TreeView(self.lista_comics)
        renderer_text = Gtk.CellRendererText()
        renderer_progress = Gtk.CellRendererProgress()
        column = Gtk.TreeViewColumn('Nombre Archivo', renderer_text, text=0)
        column.set_min_width(200)
        self.listViewComics.append_column(column)
        column = Gtk.TreeViewColumn('Total Páginas', renderer_text, text=1)
        column.set_min_width(30)
        self.listViewComics.append_column(column)
        column = Gtk.TreeViewColumn('Porcentaje_Descargado', renderer_progress, value=2)
        column.set_min_width(150)
        self.listViewComics.append_column(column)
        self.grid.attach(self.listViewComics, 0, 0, 5, 15)
        self.botonProcesar = Gtk.Button.new_with_label("Procesar")
        self.botonProcesar.connect("clicked", self.procesar)
        self.grid.attach_next_to(self.botonProcesar, self.listViewComics, 3, 1, 1)
        self.botonAgregar = Gtk.Button.new_with_label("Agregar")
        self.botonAgregar.connect("clicked", self.agregar)
        self.grid.attach_next_to(self.botonAgregar, self.botonProcesar, 1, 1, 1)
        self.botonDetener = Gtk.Button.new_with_label("Detener")
        self.grid.attach_next_to(self.botonDetener, self.botonAgregar, 1, 1, 1)
        self.botonDetener.connect("clicked", self.detener)
        self.botonLimpiarTodo = Gtk.Button.new_with_label("Limpiar Todo")
        self.botonLimpiarTodo.connect("clicked", self.limpiar_todo)
        self.grid.attach_next_to(self.botonLimpiarTodo, self.botonDetener, 1, 1, 1)
        self.botonBorrar = Gtk.Button.new_with_label("Borra")
        self.grid.attach_next_to(self.botonBorrar, self.botonLimpiarTodo, 1, 1, 1)

    def limpiar_todo(self, boton):
        self.lista_comics.clear()
        self.lista_item_for_parsing.clear()

    def detener(self, boton):
        self.currentParser.stop()

    def agregar(self, boton):
        text = self.clipboard.wait_for_text()
        if text is not None:
            parser = ReadAcomicParser(text)
            self. lista_comics.append([parser.nombreComic, len(parser.listaUrlNombreArchivo), 0.0])
            self.lista_item_for_parsing.append(parser)

    def proceso_Creacion(self):
        for i, parser in enumerate(self.lista_item_for_parsing):
            self.parserActualProcesando = parser
            self.itemActualProcesando = i
            parser.downloadImages()
            parser.createCbzFile()
            if self.stopFlag:
                break

    def updateGui(self):
        while self.hiloProceso.is_alive():
            ip = self.itemActualProcesando
            time.sleep(5)
            if ip!=self.itemActualProcesando:
                self.lista_comics[ip][2] = 100.0
            else:
                self.lista_comics[ip][2] = 100.0*self.parserActualProcesando.porcentajeDescargado

    def procesar(self, boton):
        self.hiloProceso = threading.Thread(target=self.proceso_Creacion)
        self.hiloUpdateGui = threading.Thread(target=self.updateGui)
        self.hiloProceso.start()
        self.hiloUpdateGui.start()

if __name__=='__main__':
    win = DownloaderWindow(title="Descargador de comics ReadAComic")
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
