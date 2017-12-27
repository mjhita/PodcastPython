# -*- coding: utf-8 -*-
############################################################################
#
# Curso Tratamiento de datos, juegos y programación gráfica en Python
#
#  PROYECTO.
#
# Definición del Spider para la extracción de los post en dos direcciones,
# obtiene todos los post, ya que va volcando los de las páginas siguientes.
# Es recomendable para probar usar CLOSESPIDER_ITEMCOUNT al hacer scrapy crawl,
# para limitar el número de post cargados (hay mas de 2000).
#
# Por ejemplo:
#       scrapy crawl Podcast -s CLOSESPIDER_ITEMCOUNT=20
#
# Implementado por: Manuel Jesús Hita Jiménez - 2017
#
############################################################################

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from  ObtenPodcast.items import ObtenPodcastItem

class PodcastSpider(CrawlSpider): 
    name = 'Podcast'
    allowed_domains = ['rtve.es']
    start_urls = ['http://www.rtve.es/alacarta/audios/cuando-los-elefantes-suenan-con-la-musica/']
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[@class="siguiente"]')),
        Rule(LinkExtractor(restrict_xpaths='//*[@name="progname"]'),callback='parse_item')
    )
    
    def parse_item(self, response):
        item = ObtenPodcastItem()
        
        item['titulo'] = response.xpath('//*[@class="header"]/h2/span/text()').extract()
        item['descripcion'] =response.xpath('//*[@class="header"]/div/div/p/text()').extract() 
        item['fecha'] = response.xpath('//*[@name="DC.date"]/@content').extract()
        item['duracion'] = response.xpath('//*[@class="ico play audio"]/span/text()').extract()
        item['link'] = response.xpath('//*[@rel="audio_src"]/@href').extract()

        return item

