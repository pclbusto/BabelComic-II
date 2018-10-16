from Entidades.Publishers import Publishers,Publisher


def retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

if __name__ == "__main__":

    publishers_manager = Publishers.Publishers()
    # publishers_manager.publisher.name='Nombred dsdsa dsa '
    # param = str( Publisher.Publisher.name)
    # valor = getattr(publishers_manager.publisher, param[param.index(".")+1:])
    # print(valor)
    # print(getattr(publishers_manager, retrieve_name(publishers_manager.publisher)))
    # publishers_manager.order = Publisher.Publisher.name
    # for i in range(10):
    #     publishers_manager.publisher.name = str(10 - i)
    #     publishers_manager.save()

    publishers_manager.set_order(Publisher.Publisher.name)
    for pub in publishers_manager.getList():
        print(pub.name)

    print("OBTENEMOS PRIMERO Y ULTIMO")
    print(publishers_manager.getFirst().name)
    print(publishers_manager.getNext().name)

    # publishers_manager.rmAll()
