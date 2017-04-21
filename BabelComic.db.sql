BEGIN TRANSACTION;
CREATE TABLE tiempo (key integer, tiempo real, PRIMARY KEY (key));
CREATE TABLE series (id text PRIMARY KEY, nombre text, descripcion text, image_url text, publisherId text, AnioInicio text, cantidadNumeros int,date_added integer);
CREATE TABLE config_VineKeysStatus (key text, recurso integer, cantidadTotalConsultas integer, fechaHoraInicioConsulta, PRIMARY KEY (key,recurso));
CREATE TABLE config_VineKeys (key text, PRIMARY KEY (key));
CREATE TABLE config_TipoArchivo (tipo text, PRIMARY KEY (tipo));
CREATE TABLE config_Directorios (pathDirectorio text, PRIMARY KEY (pathDirectorio));
CREATE TABLE "comics" (
	`path`	text UNIQUE,
	`titulo`	text,
	`serieId`	text,
	`numero`	int,
	`fechaTapa`	text,
	`AnioInicio`	text,
	`volumen`	text,
	`idExterno`	text,
	`resumen`	text,
	`notas`	text,
	`anio`	int,
	`mes`	int,
	`dia`	int,
	`direccionWeb`	text,
	`cantidadPaginas`	int,
	`rating`	real,
	`ratingExterno`	real,
	`tipo`	text,
	`fechaIngresoSistema`	text,
	`fechaultimaActualizacion`	text,
	`fechaultimaActualizacionSistemaExterno`	text,
	`idFila`	INTEGER PRIMARY KEY AUTOINCREMENT
);
CREATE TABLE "Publishers" (
	`id`	text,
	`name`	text,
	`deck`	text,
	`description`	text,
	`logoImagePath`	TEXT,
	`localLogoImagePath`	TEXT,
	`siteDetailUrl`	TEXT,
	PRIMARY KEY(`id`)
);
CREATE TABLE Listas (nombreLista text, sublistaDe text, descripcion text, nombreVista text, sqlText text, PRIMARY KEY (nombreLista));
CREATE TABLE ArcosArgumentalesComics (idArco integer, idComic integer , orden integer, PRIMARY KEY (idArco,idComic));
CREATE TABLE ArcosArgumentales (id integer, nombre text, descripcion text,  ultimaFechaActualizacion integer, PRIMARY KEY (id));
CREATE VIEW biblioteca as select distinct *,comics.rowid as comicRowId from comics as comics
 left join series as series on serieId = series.id
 left join Publishers on Publishers.id= publisherId
 left join ArcosArgumentalesComics on ArcosArgumentalesComics.idComic = idExterno
 left join ArcosArgumentales on ArcosArgumentales.id = ArcosArgumentalesComics.idArco;
COMMIT;
