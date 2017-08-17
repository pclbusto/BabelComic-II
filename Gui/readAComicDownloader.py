import urllib.request
from tkinter import *
from tkinter import Tk, ttk
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
        listaCaracteresInvalidos=["/","\\",":"]
        #Obtenemos el nombre del comic que vamos a crear
        t = re.findall('<meta name\="keywords" content\=(.*)\"', self.html)
        self.nombreComic = t[0][(t[0].rfind(","))+1:] + ".cbz"
        self.nombreComic = str.strip(self.nombreComic)
        for caracter in listaCaracteresInvalidos:
            self.nombreComic = self.nombreComic.replace(caracter,"-")

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
            self.listaUrlNombreArchivo.append((url,nombreArchivo,index))
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
        index = 1
        self.porcentajeCompreso = 0
        for item in self.listaUrlNombreArchivo:
            zip.write(item[1])
            self.porcentajeCompreso = item[2] / len(self.listaUrlNombreArchivo)
            print("porcentaje comprimido {}".format(self.porcentajeCompreso))
        zip.close()
        self.porcentajeCompreso = 100.0
        index = 1
        for item in self.listaUrlNombreArchivo:
            os.remove(item[1])




class readAcomicParserGui(Frame):
    listaReadAComicParsers=[]

    stopFlag = False
    itemActualProcesando=None
    parserActualProcesando=None

    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)

        # self.texto = Text(self)
        # self.texto.grid(column=1, row=0, sticky=(N,W,S,N),columnspan=2)
        self.listViewParsers = ttk.Treeview(self)
        self.listViewParsers['columns']=['Nombre_Archivo','Total_Paginas','Porcentaje_Descargado']
        self.listViewParsers.heading('#0', text='Nro')
        self.listViewParsers.column('#0', width=30)
        self.listViewParsers.heading('Nombre_Archivo', text='Nombre Archivo')
        self.listViewParsers.column('Nombre_Archivo',width=190)
        self.listViewParsers.heading('Total_Paginas', text='Total Paginas')
        self.listViewParsers.column('Total_Paginas', width=150)
        self.listViewParsers.heading('Porcentaje_Descargado', text='Porcentaje Descargado')
        self.listViewParsers.column('Porcentaje_Descargado', width=150)
        self.listViewParsers.grid(column=0, row=0, sticky=(N,W,S,N),columnspan=4)

        self.botonProcesar = Button(self, text='Procesar', command=self.procesar)
        self.botonProcesar.grid(column=1, row=1)
        self.botonProcesar = Button(self, text='Agregar', command=self.agregar)
        self.botonProcesar.grid(column=0, row=1)
        self.botonProcesar = Button(self, text='Detener', command=self.detener)
        self.botonProcesar.grid(column=2, row=1)
        self.botonProcesar = Button(self, text='Limpiar', command=self.limpiar)
        self.botonProcesar.grid(column=3, row=1)

    def limpiar(self):
        self.listaReadAComicParsers.clear()
        self.listViewParsers.delete(self.listViewParsers.get_children())

    def detener(self):
        self.currentParser.stop()


    def agregar(self):
        parser = ReadAcomicParser(Tk.clipboard_get(self))
        item = self.listViewParsers.insert('', 'end', text=len(self.listaReadAComicParsers),
        values=(parser.nombreComic, str(len(parser.listaUrlNombreArchivo)), "0"))
        self.listaReadAComicParsers.append((parser,item))

        # self.texto.delete(1.0,END)

    def proceso_Creacion(self):
        for (parser,item) in self.listaReadAComicParsers:
            self.parserActualProcesando = parser
            self.itemActualProcesando = item
            parser.downloadImages()
            parser.createCbzFile()
            if self.stopFlag:
                break
        # self.listaReadAComicParsers.remove(parser)
        # self.listViewParsers.delete(item)

    def updateGui(self):
        while self.hiloProceso.is_alive():
            ip = self.itemActualProcesando
            time.sleep(5)
            if ip!=self.itemActualProcesando:
                self.listViewParsers.set(ip,'Porcentaje_Descargado','100%')
            else:
                self.listViewParsers.set(self.itemActualProcesando,'Porcentaje_Descargado','{}%'.format(int(100*self.parserActualProcesando.porcentajeDescargado)))

    def procesar(self):
        self.hiloProceso = threading.Thread(target=self.proceso_Creacion)
        self.hiloUpdateGui = threading.Thread(target=self.updateGui)
        self.hiloProceso.start()
        self.hiloUpdateGui.start()




if __name__=='__main__':
    # url = "http://readcomiconline.to/Comic/Green-Lantern-1990/Issue-34?id=4189&readType=1"
    # request = urllib.request.Request(url,None)
    # page =  urllib.request.urlopen(request)
    # print(page)
    root = Tk()
    publisher = readAcomicParserGui(root, width=400, height=600)
    publisher.pack(fill=BOTH)
    root.mainloop()
