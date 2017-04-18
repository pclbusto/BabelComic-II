import sqlite3
from Entidades.ArcosArgumentales import ArcoArgumental

class ArcosArgumentales():
    def __init__(self):
        self.conexion = sqlite3.connect('BabelComic.db')
        self.conexion.row_factory = sqlite3.Row
    def get(self,Id):
        print('recuperando arcooooooooooooooooo: '+str(Id))
        cursor = self.conexion.cursor()
        cursor.execute('''select id, nombre, descripcion, ultimaFechaActualizacion from ArcosArgumentales where id = ?''',(Id,))
        row = cursor.fetchone()
        if(row):
            print('cargando arco: ' + str(Id))
            arco = ArcoArgumental(row['id'],row['nombre'])
            arco.descricion = row['descripcion']
            arco.ultimaFechaActualizacion = row['ultimaFechaActualizacion']
            cursor.execute('''select idArco, idComic, orden from ArcosArgumentalesComics where idArco = ?''',(Id,))
            rows = cursor.fetchall()
            print('recuperando comics del arco: ' + str(Id))
            for row in rows:
                print(row['idComic'])
                arco.comics.append((row['idComic'],row['orden']))
            return arco
        else:
            return  None


    def add(self, arco):
        cursor = self.conexion.cursor()
        cursor.execute('''INSERT INTO ArcosArgumentales (id, nombre, descripcion, ultimaFechaActualizacion) values (?,?,?,?)''',(arco.id,arco.nombre,arco.descripcion,datetime.date.today().toordinal(),))
        if len(arco.comics)>0:
            #hay que guardar que comics contiene y el orden
            for (idComic,numeroDentroArco) in arco.comics:
                cursor.execute('''INSERT INTO ArcosArgumentalesComics (idArco, idComic, orden) values (?,?,?)''',(arco.id,idComic,numeroDentroArco,))
        self.conexion.commit()

    def rm(self, Id):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE FROM ArcosArgumentales WHERE id=?''',(Id,))
        cursor.execute('''DELETE FROM ArcosArgumentalesComics WHERE idArco = ?''',(Id,))
        self.conexion.commit()


if (__name__=='__main__'):
    ArcosArgumentales().rm(55691)

    #print(arco.getCantidadTitulos())
