from Entidades.Entity_manager import Entity_manager
from Extras.ComicVineSearcher import ComicVineSearcher
from Entidades.Agrupado_Entidades import Publisher, Comicbook_Info,Comicbook
from sqlalchemy import func, join
import Entidades.Init


def retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

def is_number(s):
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False

    return True

if __name__ == "__main__":
    # session = Entidades.Init.Session()
    # sq = session.query(Comicbook.id_comicbook_info, func.count(1).label('cantidad')).join(Comicbook_Info, Comicbook_Info.id_comicbook_info==Comicbook.id_comicbook_info).group_by(Comicbook.id_comicbook_info).subquery("sq")
    # comics = session.query(Comicbook_Info.id_comicbook_info, sq.c.cantidad).join(sq, sq.c.id_comicbook_info==Comicbook_Info.id_comicbook_info).all()
    # url = "https://comicvine.gamespot.com/aquaman-11-doom-from-dimension-aqua/4000-6657/"
    #
    # print(url[url.rfind("-")+1:-1])
    numero = '1dsada'

    print(('0000000'+numero)[-7:])
    #
    # session.query(Entidades.Agrupado_Entidades.Arcos_Argumentales_Comics_Reference).delete()
    # session.query(Entidades.Agrupado_Entidades.Arco_Argumental).delete()
    # session.query(Entidades.Agrupado_Entidades.Volume).delete()
    # session.query(Entidades.Agrupado_Entidades.Comics_In_Volume).delete()
    # session.query(Entidades.Agrupado_Entidades.Comicbook_Info).delete()
    #
    # session.commit()
    # arco1 = Entidades.Agrupado_Entidades.Arco_Argumental()
    # arco1.id_arco_argumental=123
    # comicbook = Entidades.Agrupado_Entidades.Comicbook_Info()
    # comicbook.id_comicbook_Info = 999999
    #
    # # session.add(arco1)
    # # session.add(comicbook)
    # # session.commit()
    #
    # # comicbook.ids_arco_argumental.append(arco)
    # rel = Entidades.Agrupado_Entidades.Arcos_Argumentales_Comics_Reference()
    # rel.ids_comicbooks_Info = comicbook
    # rel.ids_arco_argumental = arco1
    # session.add(rel)
    # # session.commit()
    #
    # arco2 = Entidades.Agrupado_Entidades.Arco_Argumental()
    # arco2.id_arco_argumental = 456
    # rel2 = Entidades.Agrupado_Entidades.Arcos_Argumentales_Comics_Reference(orden = 11111)
    # rel2.ids_comicbooks_Info = comicbook
    # rel2.ids_arco_argumental = arco2
    # session.add(rel2)
    # session.commit()
    #
    #
    # # rel.ids_comicbooks_Info.append(comicbook)
    # rel.orden=1234
    # print(rel)
    #
    # # rel.ids_arco_argumental.append(arco)
    # session.add(rel)
    # # arco.ids_comicbooks_Info.append(comicbook)
    # session.commit()
    # #
    # # p1 = Publisher()
    # # p1.id_publisher=1
    # # session.add(p1)
    # # p2 = Publisher()
    # # p2.id_publisher=1
    # # print(session.identity_map.keys())
    # # if p2.id_publisher in session.identity_map.keys():
    # #     print("SI esta")
    # #     session.add(p2)
    # # session.commit()
    # # session.close()
    # conj = [1,2,3,1,5,4,7,8]
    # print(conj)
    #
    # print(conj.index(4))