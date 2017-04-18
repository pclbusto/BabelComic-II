import sqlite3
import datetime

class ArcoArgumental():
    def __init__(self, Id, nombre):
        self.id = Id
        self.nombre = nombre
        self.deck = ''
        self.descricion = ''
        self.comics=[]
        self.ultimaFechaActualizacion=1
    def getIssueOrder(self,comicId):
        for (Id,orden) in self.comics:
            if (int(Id)==int(comicId)):
                return orden
        return -1

    def getCantidadTitulos(self):
        return (len(self.comics))

