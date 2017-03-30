#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Archivo: SensorAcelerometro.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Perla Velasco & Yonathan Mtz & Alan Mercado.
# Version: 1.5.2 Marzo 2017
# Descripción:
#
#   Ésta clase define el rol de un publicador que envia mensajes a una cola
#   específica.
#   Las características de ésta clase son las siguientes:
#
#                                      SensorAcelerometro.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |  - Enviar mensajes      |  - Se conecta a la cola|
#           |      Publicador       |                         |   'direct acceleration'|
#           |                       |                         |  - Envia datos de ace- |
#           |                       |                         |    leración a la cola. |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                             Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Inicializa los va- |
#           |       __init__()       |      String: nombre      |    lores de nombre e  |
#           |                        |                          |    id.                |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Genera de manera a-|
#           |        set_id()        |           None           |    leatoria el id del |
#           |                        |                          |    usuario.           |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Devuelve el nombre |
#           |       get_name()       |           None           |    del usuario al cual|
#           |                        |                          |    fue asignado el    |
#           |                        |                          |    sensor.            |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Realiza la conexión|
#           |                        |                          |    con el servidor    |
#           |                        |                          |    de RabbitMQ local. |
#           |                        |                          |  - Define a que cola  |
#           |     start_service()    |           None           |    enviará los mensa- |
#           |                        |                          |    jes.               |
#           |                        |                          |  - Define que tipo de |
#           |                        |                          |    publicación se uti-|
#           |                        |                          |    lizará.            |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Genera un número   |
#           |     simulate_data()    |           None           |    aleatorio entre 0  |
#           |                        |                          |    y 100.             |
#           +------------------------+--------------------------+-----------------------+
#
#           Nota: "propio de Rabbit" implica que se utilizan de manera interna para realizar
#            de manera correcta la recepcion de datos, para éste ejemplo no shubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#            
#
#--------------------------------------------------------------------------------------------------

import random
import pika


class SensorAcelerometro():
    nombre = None
    id = 0

    def __init__(self, nombre):
        self.nombre = nombre
        self.id = int(self.set_id())

    def set_id(self):
        return random.randint(1000, 5000)

    def get_name(self):
        return self.nombre

    def start_service(self):
        #   +--------------------------------------------------------------------------------------+
        #   | La siguiente linea permite realizar la conexión con el servidor que aloja a RabbitMQ |
        #   +--------------------------------------------------------------------------------------+
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        #   +----------------------------------------------------------------------------------------+
        #   | La siguiente linea permite definir el tipo de intercambio y de que cola recibirá datos |
        #   +----------------------------------------------------------------------------------------+
        channel.exchange_declare(exchange='direct_acceleration', type='direct')
        severity = 'aceleracion'
        #   +----------------------------------------------------------------------------------------+
        #   | La siguientes 3 líneas generan las 3 velocidades en los ejes X, Y y Z y la 4ta las pone|
        #   | en una misma línea                                                                     |
        #   +----------------------------------------------------------------------------------------+
        aceleracion_generadaX = str(("{0:.2f}".format(round(self.simulate_data(), 2))))
        aceleracion_generadaY = str(("{0:.2f}".format(round(self.simulate_data(), 2))))
        aceleracion_generadaZ = str(("{0:.2f}".format(round(self.simulate_data(), 2))))
        aceleracion_generada = aceleracion_generadaX + 'gX  ' + aceleracion_generadaY + 'gY  ' + aceleracion_generadaZ + 'gZ'
        mensaje = 'AC:' + str(self.id) + ':' + self.nombre + \
            ':' + aceleracion_generada
        #   +----------------------------------------------------------------------------+
        #   | La siguiente linea permite enviar datos a la cola seleccionada.            |
        #   +----------------------------------------------------------------------------+
        channel.basic_publish(exchange='direct_acceleration',
                              routing_key=severity, body=mensaje)
        print('+---------------+--------------------+-------------------------------+-------------------------+')
        print('|      ' + str(self.id) +'     |     ' + self.nombre +'     |      ACELERACIÓN ENVIADA      |    ' + str(aceleracion_generada) + '    |')
        print('+---------------+--------------------+-------------------------------+-------------------------+')
        print('')
        connection.close()

    def simulate_data(self):
        return random.uniform(-3.0, 3.0)
