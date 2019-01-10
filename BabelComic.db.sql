insert into comicbooks_info_new(
actualizado_externamente,
api_detail_url,
fecha_tapa,
id_comicbook_info,
id_volume,
nombre_volumen,
nota,
numero,
orden,
rating,
resumen,
titulo,
url)
select actualizado_externamente,
api_detail_url,
fecha_tapa,
id_comicbook_info,
id_volume,
nombre_volumen,
nota,
numero,
orden,
rating,
resumen,
titulo,
''
from comicbooks_info

CREATE TABLE "comicbooks_info_new" (
	"id_comicbook_info" INTEGER NOT NULL,
	titulo VARCHAR NOT NULL,
	id_volume VARCHAR NOT NULL,
	nombre_volumen VARCHAR NOT NULL,
	numero VARCHAR NOT NULL,
	fecha_tapa INTEGER NOT NULL,
	resumen VARCHAR NOT NULL,
	nota VARCHAR NOT NULL,
	rating FLOAT NOT NULL,
	api_detail_url VARCHAR NOT NULL,
	url VARCHAR NOT NULL,
	orden FLOAT NOT NULL,
	actualizado_externamente BOOLEAN NOT NULL,
	PRIMARY KEY ("id_comicbook_Info"),
	CHECK (actualizado_externamente IN (0, 1))
);

CREATE TABLE `volumens_aux` (
	`id_volume`	INTEGER NOT NULL,
	`nombre`	VARCHAR NOT NULL,
	`deck`	VARCHAR NOT NULL,
	`descripcion`	VARCHAR NOT NULL,
	`url`	VARCHAR NOT NULL,
	`image_url`	VARCHAR NOT NULL,
	`id_publisher`	VARCHAR NOT NULL,
	`publisher_name`	VARCHAR NOT NULL,
	`anio_inicio`	INTEGER NOT NULL,
	`cantidad_numeros`	INTEGER NOT NULL,
	PRIMARY KEY(`id_volume`)
);


INSERT INTO volumens_aux
(id_volume, nombre, deck, descripcion, url, image_url, id_publisher, publisher_name, anio_inicio, cantidad_numeros)

SELECT id_volume, nombre, deck, descripcion, '',image_url, id_publisher, publisher_name, anio_inicio, cantidad_numeros
FROM volumens;


