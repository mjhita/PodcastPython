# -*- coding: utf-8 -*-
############################################################################
#
# Curso Tratamiento de datos, juegos y programación gráfica en Python
#
#  PROYECTO.
#
# Definición del Item con los campos que se extraen para cada podcast
#
# Implementado por: Manuel Jesús Hita Jiménez - 2017
#
############################################################################


from scrapy.item import Item, Field


class ObtenPodcastItem(Item): 
    titulo = Field()
    descripcion = Field()
    fecha = Field()
    duracion = Field()
    link = Field()
