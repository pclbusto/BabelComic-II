# Catalogar
En esta ventana será posible asociar una metadata o información de comic a un archivo que tengamos en nuestra
biblioteca. Hemos dividido esta ventana en tres secciones. 

![catalogar.png](..%2Fimagenes%2Fcatalogar.png)

## Sección 1

En la parte superior de la sección 1 se muestra la información local[1](catalogacion.md#1). Abajo en la 
sección 1 se muestra la lista de comics seleccionados en la [ventanan principal](principal.md). La grilla de esta 
sección tiene 3 columnas:

### Procesado
No tiene sentido de estar. Debe ser eliminado

### Número
Es el número de comic que debería de tener. Este número se puede cargar manualmente o en la parte inferior de la 
sección 1 se puede ingresar una expresión regular que se aplica a cada cadena de la columna Archivo. Recordar que 
si se hace uso de la expresión regular está en la parte donde se parsea el número debe estar rodeada de 
parentesis. Esto es porque el proceso asume que la ER va a tener una sección y será la que se use como número del
comic.
Tener en cuenta que el número que se puede ingresar no es entero sino un string. Esto se implemento de esta manera
porque se encontró que comic vine para algunos comics tienen numeraciones como ##.# o ##.A donde # es un número y 
"A" es una letra. 

### Archivo
Es el Path completo en donde se encuentra el archivo de comic.[2](catalogacion.md#2) En la mayoría de los casos 
este contiene el número del archivo.  

## Sección 2
En esta sección el usuario selecciona el volumen al cual pertenecen los comics seleccionados. Una vez seleccionado
el volumen, si la lista de comics tiene asignado algún número, Babelcomics buscará entre todos los números que 
tiene el volumen encontrar los asignados. 

## Sección 3
Es similar a la sección 1, pero en esta grilla se ven los comics que se encontraron basados en los numeros que se
cargaron en la sección 1 y están dentro del volumen que se seleccionó en la sección dos. Hay unos botones que  
permiten a usuario ver las distintas portadas que ese número puede llegar a tener. La grilla tienen 2 campos:
### Número
Es el número de comic. Esto permite al usuario poder comparar la portada del comic a catalogar con la metadata
encontrada. El usuario tiene que hacer una inspección visual aca para determinar si esta bien lo que esta por
asignar.
### Título
Es el título que tiene este número. 


Una vez configuradas las dos primeras secciones y haciendo una revisión hay que asignar la metadata al archivo. 
En la esquina inferior derecha hay un botón con el icono de los hojitas, como el icono de copiar. Al hacer click 
en este botón se ejecuta el proceso de asignación de metadata. El proceso básicamente busca para cada comic de
la izquierda una metadata que tenga la misma numeración. Cuando encuentra la coicidencia asigna y sigue con el 
siguiente comic de la izquierda hasta revisarlos a todos. Si no puede asignar a almenon 1 comic de la izquierda 
el proceso se revierte, por esto hay que tener en claro que cada comic de la lista hizquierda debe tener un número
y debe existir una metadata en la parte derecha.

------------------------
## Notas
###### [1]
Esto debería de cambiarse o revisarse. No tiene mucho sentido que muestre info cuando en realidad el usuario está
justamente tratando de asociarle información a un comic que no la tiene.
###### [2]
Hay varias ideas respecto a como presentar esta información. Al sistema no le interesa demasiado el path, pero 
del uso ha resultado util tenerlo como parte del nombre, esto permite hacer algunos filtros dentro del sistema
para poder catalogar de forma más rápida si se tiene una gran colección de comics. Pero también es cierto que 
si se tienen path muy largos estos entorpecen la lectura del nombre del archivo Sección
