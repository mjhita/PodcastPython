#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
setup(name='PodcastsWindow',
      version='1.0',
      description='Proyecto Curso Tratamiento de datos, juegos y prog. gŕafica en Python',
      author='Manuel Hita',
      author_email='mjhita@telefonica.net',
      url='https://github.com/mjhita/PodcastPython.git',
      license='GPL3',
      scripts=["PodcastsWindow.py"],
      packages=['ObtenPodcast', 'ObtenPodcast.spiders'],
      data_files=[('', ['PodcastsWindow.glade', 'DBPodcasts.sql', 'scrapy.cfg']),
                  ]
      )
