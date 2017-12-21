# -*- coding: utf-8 -*-
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
    """
    def __init__(self, *args, **kwargs):
        super(PodcastSpider, self).__init__(*args, **kwargs)
        for i in range(1,3):
            self.start_urls.append("http://www.rtve.es/alacarta/interno/contenttable.shtml?pbq=%i&orderCriteria=DESC&modl=TOC&locale=es&pageSize=15&ctx=1919" % i)
    """
    
    def parse_item(self, response):
        item = ObtenPodcastItem()
        """
        print " ======================================================="
        print " ===============        ENTRA     ======================"
        print " ======================================================="

        """
        item['titulo'] = response.xpath('//*[@class="header"]/h2/span/text()').extract()
        item['descripcion'] =response.xpath('//*[@class="header"]/div/div/p/text()').extract() 
        item['fecha'] = response.xpath('//*[@name="DC.date"]/@content').extract()
        #fecha = item['titulo'][0]
        #item['fecha'][0] = fecha[-9:]
        print "===========  LONGITUD DESCRIPCION =================="
        print len(item['descripcion'][0])
        item['duracion'] = response.xpath('//*[@class="ico play audio"]/span/text()').extract()
        item['link'] = response.xpath('//*[@rel="audio_src"]/@href').extract()

        print item['titulo']
        print "======================================================="
        print item['descripcion']
        print "======================================================="
        print item['fecha']
        print "======================================================="
        print item['link']

        return item

