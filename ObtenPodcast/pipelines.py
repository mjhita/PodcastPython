# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
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
        """
        self.cursor.execute(""CHECK DUPLICATE ROW"")
            if self.cursor.fetchone() is None:
                try:
                    self.cursor.execute(""INSERT NEW ROW"")
                    self.conn.commit()
                except MySQLdb.Error, e:
                    print "Error %d: %s" % (e.args[0], e.args[1])

                return item

            else:
                raise DropItem("Duplicate found.")
        """        
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
  
