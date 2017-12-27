#!/usr/bin/python
# -*- coding: utf-8 -*-
############################################################################
#
# Curso Tratamiento de datos, juegos y programación gráfica en Python
#
# PROYECTO.
#
#  Implementa una interfaz gráfica que permite visualizar los Podcasts del
#  programa "Cuando los elefantes sueñan con la música" de Radio3 en RNE
#  Estos han sido previamente descargados de la página WEB del programa y
#  almacenados en una base de datos MySQL
#
#  Permite además valorarlos y añadir comentarios a cada podcast.
#  Ofrece un botón de enlace al fichero mp3 para su reproducción o descarga
#  Además se pueden hacer búsquedas de podcasts por fecha, título, contenido
#  o comentarios-
#             
#  La base de datos se carga desde el sudirectorio ObtenPodcast, con scrapy
#  mediante la orden:
#        
#            scrapy crawl Podcast
#
#  Se pueden limitar las descargas a un numero de podcast, ejemplo 50, con:
#         
#            scrapy crawl Podcast -s CLOSESPIDER_ITEMCOUNT=50
#
#  Se incluye la gestión de conexión y desconexión a la base de datos
#
#  Para la creación de la base de datos en MySQL se incluye el archivo:
#
#            DBPodcasts.sql
#
#   
# Como futuras mejoras queda pendiente:
#     - Contemplar más de un programa de radio, con un desplegable para
#       eligirlo y una tabla en base de datos de programas con su 
#       identificador y nombre del programa. 
#     - Opción de descargar los podcasts, por ejemplo seleccionados mediante
#       la selección multiple. Permitiendo elegir destino e incorporar
#       en la interfaz la posibilidad de reproducir directamente los podcasts
#       descargados. Se pueden almacenar en carpetas anidadas por años y meses.
#       Incorporar información en las etiquetas de titulo, artista, album...
#       del archivo mp3, usando por ejemplo la clase EasyID3 de mutagen
#
# Implementado por: Manuel Jesús Hita Jiménez - 2017
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
############################################################################

from gi.repository import Gtk, GObject
import MySQLdb
import datetime
import re
#from datetime import datetime

# Constantes
BUSCAR_POR_FECHA = 0
BUSCAR_EN_TITULO = 1
BUSCAR_EN_DESCRIPCION = 2
BUSCAR_EN_COMENTARIOS = 3
BUSCAR_EN = ["fecha", "titulo", "descripcion", "comentarios"]
PATRON_FECHA = "^[1-9]\\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$"

def mensajeErrorSQL(e):
   try:
        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
   except IndexError:
        print "MySQL Error: %s" % str(e)
        
class PodcastsGUI:
    """
         Clase que implementa la interfaz gráfica que permite consultar la
         base de datos de Podcasts, extraidos de internet, del programa
         "Cuando los elefantes sueñan con la música" de Radio3 en RNE
         
         Visualiza la lista de podcast (treeview) , mostrando en cada fila
         la fecha, el titulo del programa y su duración

         Se puede añadir una valoración a cada podcast así como  comentarios

         Permite buscar por fechas, o contenidos en el Titulo, Descripcion o
         comentarios
       
    """
       
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("PodcastsWindow.glade")
        self.handlers = {
                        "onDeleteWindow": self.onDeleteWindow,    
                        #"onDescargarPodcast": self.onDescargarPodcast,
                        "onAcercaDe": self.onAcercaDe,
			"onCloseAboutDialog": self.onCloseAboutDialog,
                        "onCambiarSeleccion": self.onCambiarSeleccion,
                        "onCambiarValoracion": self.onCambiarValoracion,
                        "onBusquedaChanged": self.onBusquedaChanged, 
                        "onBtBuscarClicked": self.onBtBuscarClicked,
                        "onBtBuscarSiguienteClicked" : self.onBtBuscarSiguienteClicked
                        }
        # Conectamos las señales e iniciamos la aplicación
        self.builder.connect_signals(self.handlers)
        self.btBuscarSiguiente = self.builder.get_object("btBuscarSiguiente") 
        self.window = self.builder.get_object("PodcastWindows")
        self.statusbar = self.builder.get_object("statusbar")
        self.idStatusBar = self.statusbar.get_context_id("statusbar")
        self.about = self.builder.get_object("dialogoAcercaDe")
        
        # Ventana de texto con la descripción del podcast
        self.textDescripcion = self.builder.get_object("textDescripcion")
        self.textBufferDescripcion = self.textDescripcion.get_buffer()
        self.textDescripcion.set_editable(False)
        
        # Botón para acceder al link donde está el podcast, permite oirlo o
        # descargarlo
        self.linkPodcast = self.builder.get_object("linkPodcast")
        self.linkPodcast.set_label("Pinchar para oir o descargar")
 
        # Lista (treeview) de los podcast cargados en la base de datos
        # Contiene la fecha de emisión, titulo y duración
        self.modeloLista = self.builder.get_object('listItems')
        self.lista = self.builder.get_object('treePodcasts')
        self.scrollLista = self.builder.get_object('scrolledTreeView')

        # Combo para seleccionar la valoración que se quiere dar al podcast
        self.comboValoraciones = self.builder.get_object('comboValoraciones')
        self.listaValoraciones = self.builder.get_object('listaValoraciones')
        self.comboValoraciones.set_model(self.listaValoraciones)
        self.cell = Gtk.CellRendererText()
        self.comboValoraciones.pack_start(self.cell, True)
        self.comboValoraciones.add_attribute(self.cell, 'text', 1)
        self.comboValoraciones.set_active(0)

        # Combo para seleccionar el tipo de búsqueda que se quiera realizar:
        # por fecha, buscando texto en el contenido del título, descripcion o
        # comentarios
        self.comboBusqueda = self.builder.get_object('comboBusqueda')
        self.listaBusqueda = self.builder.get_object('listaBusqueda')
        self.comboBusqueda.set_model(self.listaBusqueda)
        self.comboBusqueda.pack_start(self.cell, True)
        self.comboBusqueda.add_attribute(self.cell, 'text', 1)
        self.comboBusqueda.set_active(0)

        # Ventana de texto donde se pueden introducir comentarios referentes
        # al podcast seleccionado
        self.textComentarios = self.builder.get_object("textComentarios")
        self.textBufferComentarios = self.textComentarios.get_buffer()
        self.textBufferComentarios.connect("changed", self.onChangeComentarios, None)

        # Entrada de texto donde se introduce la información a buscar
        self.edBusqueda = self.builder.get_object("edBusqueda")

        # Por defecto la busqueda es por fecha
        self.buscarPor = BUSCAR_POR_FECHA
        
        # Defino las columnas de la lista TreeView 
        column = Gtk.TreeViewColumn('Fecha', Gtk.CellRendererText(), text=0)   
        column.set_clickable(True)   
        column.set_resizable(True)   
        self.lista.append_column(column)

        column = Gtk.TreeViewColumn('Titulo', Gtk.CellRendererText(), text=1)   
        column.set_clickable(True)   
        column.set_resizable(True)   
        self.lista.append_column(column)

        column = Gtk.TreeViewColumn('Duración', Gtk.CellRendererText(), text=2)   
        column.set_clickable(True)   
        column.set_resizable(True)   
        self.lista.append_column(column)
        
        self.window.show_all()
        self.conexion = None
        self.cursor = None
        self.conectarABaseDatos()
        self.cargarLista()
        self.fechaSeleccionada = None
        self.esComentariosModif = False
        self.esValoracionModif = False

    def conectarABaseDatos(self):
        try:
            self.conexion = MySQLdb.connect(host='localhost', user='manuel',passwd='hita', db='DBPodcasts',
                                            charset='utf8', use_unicode=True)
            self.cursor = self.conexion.cursor()
        except MySQLdb.Error, e:
            mensajeErrorSQL(e)

    def cerrarBaseDatos(self):
        if not self.conexion or not self.cursor:
            return
        try:
            self.cursor.close()
            self.conexion.close()
        except MySQLdb.Error, e:
            mensajeErrorSQL(e)  

    def cargarLista(self):
        """
            Carga la lista, el TreeView, con la fecha de emisión, título y duración del
            podcast
        """ 
        self.modeloLista.clear()
        query= "SELECT fecha,titulo,duracion FROM Podcasts ORDER BY fecha DESC;"
        try:
            self.cursor.execute(query)
            registros = self.cursor.fetchall()
            for registro in registros:
                self.modeloLista.append([str(registro[0]),registro[1],registro[2]])
                
        except MySQLdb.Error, e:
            mensajeErrorSQL(e)
        except:
            self.statusbar.push(self.idStatusBar, "ERROR no se ha podido cargar la lista de amigos")
 
    def onDeleteWindow(self, *args):
        # Si hay datos modificado, se salvan antes de salir del programa
        if self.esComentariosModif or self.esValoracionModif:
           self.actualizarPodcast() 
        self.cerrarBaseDatos()
        Gtk.main_quit(*args)
        

    def onCambiarSeleccion(self,reeSelection):
        """
           Evento provocado por el cambio de elemento seleccionado de la lista
         
        """
        if self.esComentariosModif or self.esValoracionModif:
           self.actualizarPodcast()
           
        self.cargarPodcast()
        self.esComentariosModif = False
        self.esValoracionModif = False
        
    def onChangeComentarios(self, textBuffer, userData):
        """
           Controla cuando se producen cambios en el campo comentarios,
           para permitir guardarlos cuando se cambia de selección o al
           salir 
        """ 
        self.esComentariosModif = True
   
    def onCambiarValoracion(self, widget, data=None):
        """
           Análogo al anterior para la valoración que se haga del podcast
        """
        self.esValoracionModif = True 
 
    def ponerDatosEnBlanco(self):
        self.textBufferDescripcion.set_text("")
        self.linkPodcast.set_uri("")
        self.textBufferComentarios.set_text("")
        self.comboValoraciones.set_active(0)
         
    def cargarDatosRegistro(self, registro):
        """
            Vuelca los datos del registro "registro" en los campos de edición de la
            interfaz gráfica (descripcion, valoracion y comentarios)
        """
        self.textBufferDescripcion.set_text(registro[2])
        self.linkPodcast.set_uri(registro[4])
        if registro[6]:
            self.textBufferComentarios.set_text(registro[6])
        else:
            self.textBufferComentarios.set_text("")
        self.comboValoraciones.set_active(registro[5])
        
    def ponerDatosEdicion(self):
        """
           Vuelca los datos del registro que coincida (por su fecha) con el
           seleccionado en la lista
        """
        if not self.fechaSeleccionada:
            self.ponerDatosEnBlanco()
            return

        query= 'SELECT * FROM Podcasts WHERE fecha="{:s}";'.format(self.fechaSeleccionada)
        try:
            if self.cursor.execute(query) > 0:
                registro = self.cursor.fetchone()
                self.cargarDatosRegistro(registro)
            else:
                self.ponerDatosEnBlanco()    
        except MySQLdb.Error, e:
            self.statusbar.push(self.idStatusBar, "ERROR no se ha podido cargar Podcast")
            mensajeErrorSQL(e)
            
            return

    def obtenerFechaSeleccionada(self):
        """
            Obtiene de la lista la fecha del elemento seleccionado y la almacena en
            fechaSeleccionada
        """
        selection = self.lista.get_selection()
        #  Para seleccion simple
        tree_model, tree_iter = selection.get_selected()

        if tree_iter:
            self.fechaSeleccionada = tree_model.get_value(tree_iter, 0)
        else:
            self.fechaSeleccionada = None
            
        """ Para seleccion multiple
        tree_model, tree_iters = selection.get_selected_rows()
        # Carga los datos si hay una sóla fila seleccionada
        if len(tree_iters) == 1 :
            tree_iter = tree_model.get_iter(tree_iters[0])
            if tree_iter:
                self.fechaSeleccionada = tree_model.get_value(tree_iter, 0)
            else:
                self.fechaSeleccionada = None
        else:
            self.fechaSeleccionada = None
        """
        
    def ponerFechaSeleccionada(self, idSel):
        """
           Selecciona de la lista (TreeView) la fila con la columna fecha = idSel

        """
        selection = self.lista.get_selection()
        cont = 0
        for fila in self.modeloLista:
           if fila[0] == idSel:
               break
           cont += 1
         
        selection.select_path(cont)   

    def cargarPodcast(self):
        """
            Obtiene la fecha del Podcast de la lista, lo busca en la tabla y
            lo carga en los campos de edición de datos
        """
        self.obtenerFechaSeleccionada()
        self.ponerDatosEdicion()

    def actualizarPodcast(self):
        """      
           Modifica los datos (valoracion, comentarios) del podcast que esté
           seleccionado
        """
        if not self.fechaSeleccionada:
           return
        startiter, enditer = self.textBufferComentarios.get_bounds()
        comentarios = self.textBufferComentarios.get_text(startiter, enditer, True)
        valoracion = self.comboValoraciones.get_active()
        
        query = 'UPDATE Podcasts SET comentarios="{:s}",valoracion={:d}'.format(comentarios, valoracion)
        query += ' WHERE fecha="{:s}"'.format(self.fechaSeleccionada)
        try:
            self.cursor.execute(query)
            self.conexion.commit()
        except MySQLdb.Error, e:
            self.statusbar.push(self.idStatusBar, "ERROR no se han podido modificar los datos del Podcast")
            mensajeErrorSQL(e)
              

    def onBusquedaChanged(self, widget, data=None):
        """
           Cambia el criterio de busqueda.
           Si es por fecha no hay opción a busqueda siguiente, como nucho hay una
        """
        self.buscarPor = self.comboBusqueda.get_active()
        self.btBuscarSiguiente.set_sensitive(self.buscarPor != BUSCAR_POR_FECHA)
            

    def ponerScrollLista(self):
        """         
           Cuando se hace una selección en una búsqueda, pone a la vista la
           fila encontrada, seleccionada, en la lista de podcast
        """
        selection = self.lista.get_selection()
        tree_model, tree_iter = selection.get_selected()
        self.lista.scroll_to_cell(tree_model.get_path(tree_iter))
        
    def buscarPorFecha(self, aBuscar):
        """
             Busca la fecha introducida. Valida usando expresiones regulares,
             mediante el patrón PATRON_FECHA
             Informa en la barra de estado si se ha encontrado
        """
        if re.search(PATRON_FECHA, aBuscar):
            query= 'SELECT * FROM Podcasts WHERE fecha="{:s}";'.format(aBuscar)
            try:
                nSel = self.cursor.execute(query)
                if nSel > 0:
                    registro = self.cursor.fetchone()
                    self.cargarDatosRegistro(registro)
                    self.ponerFechaSeleccionada(str(registro[0]))
                    self.ponerScrollLista()
                    self.statusbar.push(self.idStatusBar, "Fecha encontrada")
                else:
                    self.ponerDatosEnBlanco()
                    self.statusbar.push(self.idStatusBar, "No se ha encontrado la fecha")
            except MySQLdb.Error, e:
                mensajeErrorSQL(e)
        else:
            self.statusbar.push(self.idStatusBar, "Formato de fecha incorrecto usar AAAA-MM-DD")
        
    def buscarEn(self, aBuscar):
        """
             Busca el contenido introducido, aBuscar, en el Título,
             la Descripción o comentarios, según el criterio de búsqueda
             seleccionado
             Busca la primera ocurrencia mas reciente
             Informa en la barra de estado si se ha encontrado
        """
        query= 'SELECT * FROM Podcasts WHERE {:s} LIKE "%{:s}%" ORDER BY fecha DESC;'.format(BUSCAR_EN[self.buscarPor],aBuscar)
        try:
            nSel = self.cursor.execute(query)
            if nSel > 0:
                registro = self.cursor.fetchone()
                self.cargarDatosRegistro(registro)
                self.ponerFechaSeleccionada(str(registro[0]))
                self.ponerScrollLista()
                self.statusbar.push(self.idStatusBar, "Dato encontrado con fecha: " + str(registro[0]))
            else:
                self.ponerDatosEnBlanco()
                self.statusbar.push(self.idStatusBar, "No se ha encontrado el dato")
        except MySQLdb.Error, e:
            mensajeErrorSQL(e)


    def buscarSiguiente(self, aBuscar):
        """
             Busca la siguiente ocurrencia mas reciente de aBuscar
             siguiendo el patron de búsqueda seleccionado
             Informa en la barra de estado si se ha encontrado
        """
        query =  'SELECT * FROM Podcasts WHERE {:s} LIKE "%{:s}%" AND fecha<"{:s}"'.format(
           BUSCAR_EN[self.buscarPor],aBuscar,self.fechaSeleccionada)
        query += ' ORDER BY fecha DESC;'
        try:
            nSel = self.cursor.execute(query)
            if nSel > 0:
                registro = self.cursor.fetchone()
                self.cargarDatosRegistro(registro)
                self.ponerFechaSeleccionada(str(registro[0]))
                self.ponerScrollLista()
                self.statusbar.push(self.idStatusBar, "Dato encontrado con fecha: " + str(registro[0]))
            else:
                self.ponerDatosEnBlanco()
                self.statusbar.push(self.idStatusBar, "No se ha encontrado el dato")
        except MySQLdb.Error, e:
            mensajeErrorSQL(e)

    def onBtBuscarClicked(self, button):
        aBuscar = self.edBusqueda.get_text()
        if aBuscar == "":
           self.statusbar.push(self.idStatusBar, "No se ha introducido dato para buscar")
           return

        if self.buscarPor == BUSCAR_POR_FECHA:
           self.buscarPorFecha(aBuscar)
        else :
           self.buscarEn(aBuscar)
   

    def onBtBuscarSiguienteClicked(self, button):
        if not self.fechaSeleccionada:
            self.statusbar.push(self.idStatusBar, "No hay dato seleccionado de partida para buscar siguiente") 
            return
        else:
            aBuscar = self.edBusqueda.get_text()
            if aBuscar == "":
                self.statusbar.push(self.idStatusBar, "No se ha introducido dato para buscar")
                return
            self.buscarSiguiente(aBuscar)
 
    def onAcercaDe(self, menuitem):
        self.about.show()
   
    def onCloseAboutDialog(self,window,data=None):
        self.about.hide()

def main():
    window = PodcastsGUI()    
    Gtk.main()
    
    return 0

if __name__ == '__main__':
    main()
