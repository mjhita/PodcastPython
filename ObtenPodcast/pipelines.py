# -*- coding: utf-8 -*-

############################################################################
#
# Curso Tratamiento de datos, juegos y programación gráfica en Python
#
#  PROYECTO.
#
# Define un pipeline para almacenar los datos de cada Podcast en la tabla
# "Podcasts" de la base de datos MySQL "DBPodcasts"
#
#  El archivo DBPodcasts.sql define la estructura de la tabla de la
#  base de datos y permite crearla desde MySQL
#
#
# Implementado por: Manuel Jesús Hita Jiménez - 2017
#
############################################################################

import sys
import datetime
import MySQLdb
import hashlib
from scrapy.exceptions import DropItem


class MySQLPodcastPipeline(object):
    def __init__(self):
        try:
            self.conexion = MySQLdb.connect(host='localhost', user='manuel',passwd='hita', db='DBPodcasts',
                                            charset='utf8', use_unicode=True)
            self.cursor = self.conexion.cursor()
        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)   
 
    def close_spider(self, spider):
        self.cursor.close()
        self.conexion.close()
        
    def process_item(self, item, spider):
        try:
            titulo = item['titulo'][0]
            titulo = titulo[titulo.find("-")+2:titulo.rfind("-")-1]
            agno = int(item['fecha'][0][:4])
            mes = int(item['fecha'][0][5:7])
            dia = int(item['fecha'][0][8:10])
            fecha = datetime.date(agno, mes, dia)
            strFecha = fecha.isoformat()
            query = 'SELECT fecha FROM Podcasts WHERE fecha="{:s}";'.format(strFecha)
            self.cursor.execute(query)
            # Controla que no exista ya ese podcast en la base de datos
            if self.cursor.fetchone() is None:
                query = 'INSERT INTO Podcasts (fecha,titulo,descripcion,duracion,link) VALUES'    
                query += '("{:s}","{:s}","{:s}","{:s}","{:s}");'.format(strFecha, titulo.encode('utf-8'),
                                                                    item['descripcion'][0].encode('utf-8'),
                                                                    item['duracion'][0].encode('utf-8'),
                                                                    item['link'][0].encode('utf-8'))
                self.cursor.execute(query)
                self.conexion.commit()   
        except MySQLdb.Error, e:
            raise DropItem("Error %d: %s" % (e.args[0], e.args[1]))  
        return item
  
