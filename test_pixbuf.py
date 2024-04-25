import re
linea = ""
with open("input.txt","r") as archivo:
    linea = archivo.readline()
    salida = ""
    ids_comic = set()
    expresion = "(\d+)\s(.*)"
    while linea:
        linea = archivo.readline()
        # print(linea)
        match = re.findall(expresion, linea)

        if match:
            ids_comic.add((match[0][0], match[0][1]))

    lista = list(ids_comic)
    lista_cadena = "{}".format(lista)
    # print(lista_cadena)
    lista_cadena = lista_cadena.replace("[", "")
    lista_cadena = lista_cadena.replace("]", "")
    lista_cadena = lista_cadena.replace("), (", "),\n (")
    # print(lista_cadena)
    # salida = salida+"delete  FROM comicbooks_info_cover_url where id_comicbook_info in ({})".format(lista_cadena)
    salida = "INSERT INTO comicbooks_info_cover_url(\"id_comicbook_info\", \"thumb_url\") VALUES {};".format(lista_cadena)
    with open("salida.txt", "w") as salida_f:
        salida_f.write(salida)
    # print(salida)


