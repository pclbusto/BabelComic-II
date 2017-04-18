from Entidades.ComicBooks import ComicBook
import sqlite3


class ComicBooks():
    def __init__(self):
        self.conexion = sqlite3.connect('BabelComic.db')
        self.conexion.row_factory = sqlite3.Row
        self.cantidadRegistrosConsulta = 0
        self.listaConsulta = []
        self.vistaConsultas = 'biblioteca'
        self.indiceColumnaOrdenamiento = 1
        self.listaCamposTabla = ['comicRowId', 'path', 'titulo', 'serieId',
                                 'numero', 'fechaTapa', 'AnioInicio',
                                 'volumen', 'idExterno', 'resumen',
                                 'notas', 'anio', 'mes', 'dia',
                                 'direccionWeb', 'cantidadPaginas', 'rating',
                                 'ratingExterno', 'tipo', 'fechaIngresoSistema',
                                 'fechaultimaActualizacion', 'fechaultimaActualizacionSistemaExterno']
        self.cantidadComicsPorPagina = 300
        # self.valorLimite=''
        self.paginaActual = 0
        # self.cantdadPaginas=0

    def goto(self, pageIndex):
        cantidadPaginas = int(self.cantidadRegistrosConsulta / self.cantidadComicsPorPagina)
        if pageIndex < cantidadPaginas and pageIndex >= 0:
            self.paginaActual = pageIndex
            self.list(self.valores, self.filtros)

    def getCantidadPaginas(self):
        return int(self.cantidadRegistrosConsulta / self.cantidadComicsPorPagina) - 1

    def __getCantidadRegistros__(self, valores, filtro=None):
        cursor = self.conexion.cursor()
        if not (
                    (self.indiceColumnaOrdenamiento >= 0) and (
                    self.indiceColumnaOrdenamiento < len(self.listaCamposTabla))):
            print('el indice de ordenmiento no esta seteado revisar valor indiceColumnaOrdenamiento')

        if filtro:
            cursor.execute(
                '''SELECT count(1) as cantidad From ''' + self.vistaConsultas + ''' where ''' + filtro, valores)

        else:
            cursor.execute('''SELECT count(1) as cantidad From ''' + self.vistaConsultas)
        row = cursor.fetchone()

        self.cantidadRegistrosConsulta = row['cantidad']
        return self.cantidadRegistrosConsulta

    def __listaCamposToStr__(self):
        lista = ''
        for columna in self.listaCamposTabla:
            lista += columna + ', '
        return lista[:-2]

    def add(self, comic, autocomit=True):
        """

        :type autocomit: boolean
        """
        cursor = self.conexion.cursor()

        cursor.execute('''INSERT INTO comics (
path,titulo,serieId,
numero,fechaTapa,
volumen,idExterno,resumen,
notas,
direccionWeb,cantidadPaginas,rating,
ratingExterno,tipo,fechaIngresoSistema,fechaultimaActualizacion
,fechaultimaActualizacionSistemaExterno)
Values(
:path,:titulo,:serieId,
:numero,:fechaTapa,
:volumen,:idExterno,:resumen,
:notas,
:direccionWeb,:cantidadPaginas,:rating,
:ratingExterno,:tipo,:fechaIngresoSistema,:fechaultimaActualizacion,
:fechaultimaActualizacionSistemaExterno)'''
                       , {'path': comic.path, 'titulo': comic.titulo, 'serieId': comic.serieId,
                          'numero': comic.numero, 'fechaTapa': comic.fechaTapa,
                          'volumen': comic.volumen, 'idExterno': comic.idExterno, 'resumen': comic.resumen,
                          'notas': comic.notas,
                          'direccionWeb': comic.direccionWeb, 'cantidadPaginas': comic.cantidadPaginas,
                          'rating': comic.rating,
                          'ratingExterno': comic.ratingExterno, 'tipo': comic.tipo,
                          'fechaIngresoSistema': comic.fechaIngresoSistema,
                          'fechaultimaActualizacion': comic.fechaultimaActualizacion
                           , 'fechaultimaActualizacionSistemaExterno': comic.fechaultimaActualizacionSistemaExterno})
        if autocomit:
            self.conexion.commit()

    def commit(self):
        self.conexion.commit()

    def rm(self, path):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE From comics where path=?''', (path,))
        self.conexion.commit()

    def rmAll(self):
        cursor = self.conexion.cursor()
        cursor.execute('''DELETE From comics''')
        self.conexion.commit()

    def get(self, path):
        cursor = self.conexion.cursor()
        cursor.execute(
            '''SELECT ''' + self.__listaCamposToStr__() + ''' From ''' + self.vistaConsultas + ''' where path=?''',
            (path,))
        r = cursor.fetchone()
        comic = ComicBook(path, r['titulo'], r['serieId'], r['numero'])
        comic.rowId = r['comicRowId']
        comic.fechaTapa = r['fechaTapa']
        comic.AnioInicio = r['AnioInicio']
        comic.volumen = r['volumen']
        comic.AnioInicio = r['AnioInicio']
        comic.idExterno = r['idExterno']
        comic.resumen = r['resumen']
        comic.notas = r['notas']
        comic.anio = r['anio']
        comic.mes = r['mes']
        comic.dia = r['dia']
        comic.direccionWeb = r['direccionWeb']
        comic.cantidadPaginas = r['cantidadPaginas']
        comic.rating = r['rating']
        comic.ratingExterno = r['ratingExterno']
        comic.tipo = r['tipo']
        comic.fechaIngresoSistema = r['fechaIngresoSistema']
        comic.fechaultimaActualizacion = r['fechaultimaActualizacion']
        comic.fechaultimaActualizacionSistemaExterno = r['fechaultimaActualizacionSistemaExterno']
        cursor.execute('''SELECT idArco, orden from ArcosArgumentalesComics where idComic = ?''', (comic.idExterno,))
        rows = cursor.fetchall()
        for row in rows:
            comic.seriesAlternasNumero.append((row['idArco'], row['orden']))
        return comic

    def update(self, comic):
        print('updating comicbook....')
        cursor = self.conexion.cursor()
        cursor.execute('''update comics set
titulo=?,
serieId=?,
numero=?,
fechaTapa=?,
volumen=?,idExterno=?,resumen=?,
notas=?,
direccionWeb=?,cantidadPaginas=?,rating=?,
ratingExterno=?,tipo=?,fechaIngresoSistema=?,
fechaultimaActualizacion=?,fechaultimaActualizacionSistemaExterno=?
where path=?
''', (comic.titulo,
      comic.serieId,
      comic.numero, comic.fechaTapa,
      comic.volumen, comic.idExterno, comic.resumen,
      comic.notas,
      comic.direccionWeb, comic.cantidadPaginas, comic.rating,
      comic.ratingExterno, comic.tipo, comic.fechaIngresoSistema,
      comic.fechaultimaActualizacion, comic.fechaultimaActualizacionSistemaExterno, comic.path
      ))
        self.conexion.commit()

    def list(self, valores, filtro=None):
        cursor = self.conexion.cursor()
        if not (
            (self.indiceColumnaOrdenamiento >= 0) and (self.indiceColumnaOrdenamiento < len(self.listaCamposTabla))):
            print('el indice de ordenmiento no esta seteado revisar valor indiceColumnaOrdenamiento')

        if filtro:
            print('campos: ' + self.__listaCamposToStr__())
            cursor.execute(
                '''SELECT ''' + self.__listaCamposToStr__() + ''' From ''' + self.vistaConsultas + ''' where '''
                + filtro + ''' order by ''' + self.listaCamposTabla[self.indiceColumnaOrdenamiento] +
                ''' LIMIT {:d} OFFSET {:d}'''.format(self.cantidadComicsPorPagina, self.paginaActual *
                                                     self.cantidadComicsPorPagina), valores)

        else:
            cursor.execute('''SELECT ''' + self.__listaCamposToStr__() + ''' From ''' + self.vistaConsultas +
                           ''' LIMIT {:d} OFFSET {:d}'''.format(self.cantidadComicsPorPagina, self.paginaActual *
                                                                self.cantidadComicsPorPagina))
        self.valores = valores
        self.filtros = filtro

        rows = cursor.fetchall()
        self.listaConsulta = []
        self.cantidadRegistrosConsulta = self.__getCantidadRegistros__(valores, filtro)
        for row in rows:
            comic = ComicBook(row['path'], row['titulo'], row['serieId'], row['numero'])
            # print(row['rowid'])
            comic.rowId = row['comicRowId']
            comic.fechaTapa = row['fechaTapa']
            comic.AnioInicio = row['AnioInicio']
            comic.volumen = row['volumen']
            comic.AnioInicio = row['AnioInicio']
            comic.idExterno = row['idExterno']
            comic.resumen = row['resumen']
            comic.notas = row['notas']
            comic.anio = row['anio']
            comic.mes = row['mes']
            comic.dia = row['dia']
            comic.direccionWeb = row['direccionWeb']
            comic.cantidadPaginas = row['cantidadPaginas']
            comic.rating = row['rating']
            comic.ratingExterno = row['ratingExterno']
            comic.tipo = row['tipo']
            comic.fechaIngresoSistema = row['fechaIngresoSistema']
            comic.fechaultimaActualizacion = row['fechaultimaActualizacion']
            comic.fechaultimaActualizacionSistemaExterno = row['fechaultimaActualizacionSistemaExterno']
            self.listaConsulta.append(comic)
        return self.listaConsulta

    def close(self):
        self.conexion.close()


if __name__ == "__main__":
    comics = ComicBooks()
    comics.__getCantidadPaginas__(('%%',), 'path like ?')
    print(comics.__getCantidadPaginas__(('%%',), 'path like ?'))
    ##    for r in cursor.fetchall():
    # print(comic.resumen)
    comics.close()




