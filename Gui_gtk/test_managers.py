from Entidades.Entity_manager import Entity_manager
from Extras.ComicVineSearcher import ComicVineSearcher
from Entidades.Volumens.Volumens import Volumens,Volume
from Entidades.Publishers.Publisher import Publisher


def retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

if __name__ == "__main__":

    # cadena = 'June 2018'
    # print(cadena[-4:])
    #
    #
    searcher = ComicVineSearcher(vinekey='7e4368b71c5a66d710a62e996a660024f6a868d4', session=None)
    searcher.entidad='volume'
    searcher.getVineEntity('86343')

    # http://comicvine.gamespot.com/api/volume/4050-7300/?api_key=7e4368b71c5a66d710a62e996a660024f6a868d4
    # publisher_manager = Entity_manager(clase=Publisher)
    #
    # publisher_manager.entidad.name='dc comics'
    # # publisher_manager.entidad.id_publisher = 123456
    # # publisher_manager.entidad.id_publisher_externo = 123456
    # publisher_manager.save()
    # # valor = getattr(volumens_manager.publisher, param[param.index(".")+1:])
    # # print(valor)
    # # print(getattr(volumens_manager, retrieve_name(volumens_manager.publisher)))
    # # volumens_manager.order = Publisher.Publisher.name
    # # for i in range(10):
    # #     volumens_manager.entidad.nombre = str(10 - i)
    # #     volumens_manager.save()
    #
    # # volumens_manager.set_order(Volume.id_volumen)
    # # volumens_manager.set_filtro(Publisher.Publisher.name.like("M%"))
    # # for pub in volumens_manager.getList():
    # #      print(pub.nombre)
    # #
    # # print("OBTENEMOS PRIMERO Y ULTIMO")
    # # print(volumens_manager.getFirst().nombre)
    # # print(volumens_manager.getNext().nombre)
    # # print(volumens_manager.getLast().nombre)
    # # volumens_manager.set_filtro(Volume.nombre.like("M%"))
    # # print(volumens_manager.getFirst().nombre)
    # # print(volumens_manager.getLast().nombre)
