from Entidades.Entity_manager import Entity_manager
from Extras.ComicVineSearcher import ComicVineSearcher
from Entidades.Agrupado_Entidades import Publisher
import Entidades.Init


def retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

if __name__ == "__main__":
    # session = Entidades.Init.Session()
    #
    # p1 = Publisher()
    # p1.id_publisher=1
    # session.add(p1)
    # p2 = Publisher()
    # p2.id_publisher=1
    # print(session.identity_map.keys())
    # if p2.id_publisher in session.identity_map.keys():
    #     print("SI esta")
    #     session.add(p2)
    # session.commit()
    # session.close()
    conj = {1,2,3,4,5,6,7,8}
    print(conj)
    conj.add(1)
    print(conj)