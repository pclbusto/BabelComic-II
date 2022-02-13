import asyncio
import time
import random

class Test ():
    CANT_MAX_TAREAS = 10
    CANT_MAX_TAREAS_SIMULTANEAS = 15

    def __init__(self):
        self.variable = 0
        self.lock_cantidad_tareas_en_ejecucion = asyncio.Condition()

        self.cantidad_tareas_ejecutadas = 0
        self.cantidad_tareas_en_ejecucion = 0

    def puede_ejectuar(self):
        # print("preguntando {}".format(self.cantidad_tareas_en_ejecucion))
        return (self.cantidad_tareas_en_ejecucion < Test.CANT_MAX_TAREAS_SIMULTANEAS)

    async def say_after(self, delay, what):
        print("ejectuando {} duracion {}".format(what, delay))
        #Esto deberia bloquear hasta que se cumpla la condiion y luego ejectur y liberar la cerradura al terminar
        async with self.lock_cantidad_tareas_en_ejecucion:
            await self.lock_cantidad_tareas_en_ejecucion.wait_for(self.puede_ejectuar)
            self.cantidad_tareas_en_ejecucion = self.cantidad_tareas_en_ejecucion + 1
        await asyncio.sleep(delay)
        async with self.lock_cantidad_tareas_en_ejecucion:
            self.cantidad_tareas_en_ejecucion = self.cantidad_tareas_en_ejecucion - 1
            self.lock_cantidad_tareas_en_ejecucion.notify(1)
            self.cantidad_tareas_ejecutadas = self.cantidad_tareas_ejecutadas + 1

    async def main(self):
        lista_tiempos = [15, 10, 13, 6, 12, 14, 14, 9, 15]
        lista_tareas = []
        for i in range(0, Test.CANT_MAX_TAREAS-1):
            # tarea = asyncio.create_task(self.say_after(random.randint(1, 15), 'tarea {}'.format(i)))
            tarea = asyncio.create_task(self.say_after(lista_tiempos[i], 'tarea {}'.format(i)))
            lista_tareas.append(tarea)

        print(f"started at {time.strftime('%X')}")

        await asyncio.gather(*lista_tareas)

        print(f"finished at {time.strftime('%X')}")

test = Test()

asyncio.run(test.main())
# print(test.variable)
#
# print()
#
# for i in range(1, 10000):
#     print()