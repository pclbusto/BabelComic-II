# Volumen

Ventana de administración de los volúmenes o series. Los comics pertenecen a una serie o volumen, por ejemplo Batman, 
Superman o lox X-men. Cada una de estas series está compuesta por uno o varios ejemplares o números que dentro de
Babelcomics se llaman[información de comic, metadata o comic info](comic_info.md). Las series o volumenes son estos 
contenedores. 


![Volumen.png](..%2Fimagenes%2FVolumen.png)


## Campos

### Id Volumen
Identificador unico. Al usar Comicvine como proveedor de metadata para los comics. Este ID se corresponde con el ID 
de este sitio. Igualmente, Babelcomics permite cargar de forma manual un volumen en este caso el ID que usa es 
negativo. De esta manera se diferencia una serie o volumen externo de una interna
### Nombre
Nombre del Volumen o serie
### Editorial
Id de la editorial que creo este volumen o serie.

### Descripción
Nombre de la Editorial 

### Año inicio
Año en el que se creó el volumen o serie

### Cantidad de números
Cantidad de números que se tiene sobre este volumen. Tener en cuenta que para series que todavía se sigan 
imprimiendo va a ser necesario actualizar cada tanto. [1](volumen.md#1-)

### URL
Dirección web del volumen.

### API URL
Url de la api. Agregando la key de servicio se debería poder ver el Json que este retorna  

### URL Cover
Cada Volumen tiene un cover que por lo general se corresponde con el primer número. Lo que se muestra aca es el 
link a esta imagen.

### Porcentaje completado Volumen
Esto es un cálculo que retorna la cantidad de comics digitales asociados a algún número de este volumen. Se 
entiende que un usuario podría llegar a tener varias copias del mismo comic, probablemente porque no a salida 
todavía la version digitalizada. Este número marca los números distintos asociados y da una idea de cuan completo
está dicho volumen. 

### Cantidad Comics Asociados
Esto es un cálculo que retorna la cantidad de comics digitales que se tienen de este volumen. No se tiene en 
cuenta si están o no repetidos. Esto permite identificar cuando se tienen comics repetidos.

## Solapas

### Resumen
Resumen del volumen. Como lo dice en nombre muestra una sinopsis del volumen.

### Estado Volumen
Contiene una grilla donde se muestran 4 columnas para cada issue o información de comic. En esta grilla se puede
ver el estado para cada una de estas informaciones en conjunto con la cantidad de archivos de comics asociados a cada
número. Las columnas son:
* Número: Se corresponde con la numeración que tiene cada una de las metadata que componen el volumen.
* Titulo: El titulo que tiene cada metadata. En algunos casos estas metadatas suelen tener títulos.
* Catalogado: *deprecado*
* Cantidad: Muestra el número de archivos de comics asociados a esta metadata.

### Números

*Deprecado por el momento. Un posible uso sea la posibilidad de ver las portadas para cada metadata.*

## Menu


---------------------------
### [1] 
Debería de tener un proceso automático que cada X cantidad de tiempo desde su última actualización haga
una consulta a servicio de Comicvine para ver si hay cambios.