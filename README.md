# PodcastPython

## CURSO Tratamiento de datos, juegos y programación gráfica en Python, 6ª edición

### Proyecto. 

Carga en una base de datos los podcasts de un programa de radio y permite consultarlos a través de un GUI GTK. 

En primer lugar hay que crear la base de datos MySQL que almacenará la tabla con los Podcasts del programa.

Esta está definida en el fichero:
> DBPodcasts.sql

Si la base de datos ya existe, elimina la tabla de Podcasts y crea una nueva vacia

A continuación para "poblar" la tabla hay que entrar en la carpeta ObtenPodcast y ejecutar:
> $ scrapy crawl Podcast
    
De esta forma se rellena la tabla con los datos de cada Postcad, hay podcast de emisiones hasta 2008 de programas
radiados de Lunes a Viernes, por lo que aparecen mas de 2000 registros. Para probar se puede limitar la carga de datos
por ejemplo con:
> $ scrapy crawl Podcast -s CLOSESPIDER_ITEMCOUNT=50
    
Una vez creada y poblada la base de datos el programa PodcastsWindow.py nos ofrece una interfaz gráfica con una lista de los Podcasts en la que aparece su fecha de emisión, título y duración. Aparte permite valorar cada podcast y añadir comentarios.
Otra funcionalidad ofrecida es la búsqueda de podcasts por fecha o que contengan determinada información en título, contenidos o comentarios.

Como futuras mejoras queda pendiente:

> Contemplar más de un programa de radio, con un desplegable para eligirlo y una tabla en base de datos de programas con su identificador y nombre del programa. 

> Opción de descargar los podcasts, por ejemplo seleccionados mediante la selección multiple. Permitiendo elegir destino e incorporar en la interfaz la posibilidad de reproducir directamente los podcasts descargados. Se pueden almacenar en carpetas anidadas por años y meses. Ademas puede Incorporar información en las etiquetas de titulo, artista, album... del archivo mp3, usando por ejemplo la clase EasyID3 del módulo mutagen

