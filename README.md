```mermaid
  erDiagram
      volumens }o--|| publishers : "es editado por"
      volumens{
               integer id_volume PK
               string nombre
               string deck
               string descripcion
               string url
               string image_url
               string id_publisher FK "Deberìa ser entero pero esta como string"
               string publisher_name
               integer anio_inicio
               integer cantidad_numeros
      }
publishers{
 integer id_publisher PK
		string name
		string deck
		string description
		string logoImagePath
		string localLogoImagePath
		string siteDetailUrl
}
comicbooks ||--|| comicbooks_info : "obtiene info de" 

comicbooks{
	string	path
	integer	id_comicbook PK
	string	id_comicbook_info
	integer	calidad
	integer	en_papelera
}

comicbooks_info }|..|| volumens : "pertenece a (id_volume)"
comicbooks_info {
integer id_comicbook_info PK
string titulo	
integer id_volume
string nombre_volumen	
string numero	
integer fecha_tapa
string resumen	
string nota	
float rating
string api_detail_url	
string url	
float orden
boolean actualizado_externamente  "Se verifica que sea un valor entre 0 y 1"
}

comicbooks_info }|..|| comicbooks_info_cover_url : "tiene (id_comicbook_info)"

comicbooks_info_cover_url {
 integer id_comicbook_info PK "restrincción que exista el id_comicbook_info en la tabla comicbook_info"
 string thumb_url PK
}
comicbooks_info }o..|{ arcos_argumentales_comics_reference: " (id_comicbook_info)"
arcos_argumentales }o..|{ arcos_argumentales_comics_reference: " (id_arco_argumental)"

arcos_argumentales_comics_reference{
	integer id_comicbook_info FK "REFERENCES comicbooks_info(id_comicbook_info"
	integer id_arco_argumental FK "REFERENCES arcos_argumentales(id_arco_argumental)"	
	integer orden
}


arcos_argumentales  {
	integer id_arco_argumental PK
	string nombre
	string deck
	string descripcion
	integer ultimaFechaActualizacion
	integer cantidad_comicbooks
}

comicbooks }o..|{ comicbooks_detail: "detalla (comicbook_id)"

comicbooks_detail {
	integer comicbook_id FK
	integer indicePagina PK
	integer ordenPagina
	integer tipoPagina
	string nombre_pagina
}


```

# BabelComic-II
Es un catalogador de comics. Este proyecto arranca por no tener una herramienta en linux como una muy conocida en el SO de la ventana. El autor de ese software dijo que no tenía intenciones de portarlo a linux asi que arranque con el propio. No intenta ser ni de cerca un clon de ese software el cual anda muy bien y es gratuito. 
Basicamente quiero tener una base de catalogo para mis comics y el que quierar usarlo que lo use. No tengo ni idea sobre como es el tema de licencias para su publicacion y esas cosas por lo cual es bastante amateur este proyecto y le voy metiendo horas cuando puedo. 
Actualmente BabelComics no tiene versión 1.0 porque considero que falta mucho por terminar.

# Funcionalidades deseadas para liberar versión 1.0
-------------------------------------
* ABM
  * Editoriales (falta implementar eliminación)
  * Serie o volumen tiene eliminacion pero no funciona de forma correcta
  * Comic (falta implementar completamente)
  * Arcos Argumentales (falta implementar completamente)
* Búqueda 
  * Las entidades implementadas lo tienen 
  * Las no implementadas no lo tienen
* visor o lector de comics (falta implementar completamente).
  * Hay mucho software que ya hace esto pero quiero agregar algo que no he visto en otros y dio orignen al nombre del programa.

# Funcionalidades deseadas a futuro
* Proceso de catalogación
  * implementado pero pendiente proceso de refactoring para no hacerlo dependiente de una GUI
* Ventana de estadisticas para poder ver cuanto tengo completo de arcos argumentales y volumenes. También poder ver los comics que se tienen repetidos y ese tipo de cosas.
* armado de procesos de formateo o normalización de nombres para poder organizar los comics a nivel de archivo.

# capturas
pepep



  
