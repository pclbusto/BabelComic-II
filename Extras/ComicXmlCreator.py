from Entidades.ComicBooks.ComicBook import ComicBook
from Entidades.Publishers.Publisher import Publisher
from Entidades.ArcosArgumentales.ArcoArgumental import ArcoArgumental
from Entidades.Volumes.Volume import Volume
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import ElementTree
import Entidades.Init
import os


class XmlManager:
    session = None

    def __init__(self, session=None):
        if not session:
            self.session = session
        else:
            self.session = Entidades.Init.Session()

    def crear_xml(self, comic):
        comic_root = Element('ComicRoot')
        comic_node = SubElement(comic_root, "Comic")
        SubElement(comic_node, "comicId").text = str(comic.comicId)
        SubElement(comic_node, "comicVineId").text = comic.comicVineId
        SubElement(comic_node, "titulo").text = comic.titulo
        SubElement(comic_node, "volumeId").text = comic.volumeId
        SubElement(comic_node, "volumeNombre").text = comic.volumeNombre
        SubElement(comic_node, "numero").text = comic.numero
        SubElement(comic_node, "fechaTapa").text = str(comic.fechaTapa)
        SubElement(comic_node, "arcoArgumentalId").text = comic.arcoArgumentalId
        SubElement(comic_node, "arcoArgumentalNumero").text = str(comic.arcoArgumentalNumero)
        SubElement(comic_node, "resumen").text = comic.resumen
        SubElement(comic_node, "nota").text = comic.nota
        SubElement(comic_node, "rating").text = comic.rating
        SubElement(comic_node, "ratingExterno").text = comic.ratingExterno
        SubElement(comic_node, "publisherId").text = comic.publisherId
        SubElement(comic_node, "api_detail_url").text = comic.api_detail_url
        SubElement(comic_node, "thumb_url").text = comic.thumb_url
        SubElement(comic_node, "calidad").text = comic.calidad

        if comic.volumeId != '':
            volume_node = SubElement(comic_root, "Volumen")
            volume = self.session.query(Volume).get(comic.volumeId)
            SubElement(volume_node, "id").text = volume.id
            SubElement(volume_node, "nombre").text = volume.nombre
            SubElement(volume_node, "deck").text = volume.deck
            SubElement(volume_node, "descripcion").text = volume.descripcion
            SubElement(volume_node, "image_url").text = volume.image_url
            SubElement(volume_node, "publisherId").text = volume.publisherId
            SubElement(volume_node, "publisher_name").text = volume.publisher_name
            SubElement(volume_node, "AnioInicio").text = str(volume.AnioInicio)
            SubElement(volume_node, "cantidadNumeros").text = str(volume.cantidadNumeros)

        if comic.arcoArgumentalId != '0':
            print("ARCO ARGUMENTAL : {}".format(comic.arcoArgumentalId))
            arco_argumental_node = SubElement(comic_root, "ArcoArgumental")
            arco_argumental = self.session.query(ArcoArgumental).get(comic.arcoArgumentalId)
            SubElement(arco_argumental_node, "id").text = arco_argumental.id
            SubElement(arco_argumental_node, "nombre").text = arco_argumental.nombre
            SubElement(arco_argumental_node, "deck").text = arco_argumental.deck
            SubElement(arco_argumental_node, "descripcion").text = arco_argumental.descripcion
            SubElement(arco_argumental_node, "ultimaFechaActualizacion").text = str(
                arco_argumental.ultimaFechaActualizacion)


        if comic.publisherId != '':
            publisher_node = SubElement(comic_root, "Publisher")
            publisher = self.session.query(Publisher).get(comic.publisherId)
            SubElement(publisher_node, "id_publisher").text = publisher.id_publisher
            SubElement(publisher_node, "name").text = publisher.name
            SubElement(publisher_node, "deck").text = publisher.deck
            SubElement(publisher_node, "description").text = publisher.description
            SubElement(publisher_node, "logoImagePath").text = publisher.logoImagePath
            SubElement(publisher_node, "siteDetailUrl").text = publisher.siteDetailUrl
        return comic_root

    def set_for_all(self):

        lista = self.session.query(ComicBook).all()
        for comic in lista:
            comic_root = self.crear_xml(comic)
            tree = ElementTree(comic_root)
            tree.write("{}.xml".format(comic.comicId))
            self.insertarXmlDentroComic(comic)

    def set_xml_for_comic(self, comic):
        comic_root = self.crear_xml(comic)
        tree = ElementTree(comic_root)
        tree.write("{}.xml".format(comic.comicId))
        self.insertarXmlDentroComic(comic)

    def insertarXmlDentroComic(self, comic):
        comic.editCbFile()
        tempPath = comic.path[:comic.path.find(comic.getNombreArchivo())]+"temp"
        xmlName = "{}.xml".format(comic.comicId)
        if xmlName not in comic.cbFile.namelist():
            comic.cbFile.write(str(comic.comicId) + ".xml")
            os.remove(str(comic.comicId) + ".xml")
            comic.cbFile.close()


if __name__ == '__main__':
    print("")
    # crearXml()