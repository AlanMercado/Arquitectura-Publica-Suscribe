#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Archivo: AcelerometroManager.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Jorge España.
# Version: 1.0 Marzo 2017
# Descripción:
#
#   Ésta clase define el rol de un subscriptor que consume los mensajes de una cola
#   específica.
#   Las características de ésta clase son las siguientes:
#
#                                        AcelerometroManager.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |  - Recibir mensajes     |  - Se subscribe a la   |
#           |      Subscriptor      |  - Notificar al         |    cola de 'direct     |
#           |                       |    monitor.             |    acceleration'.      |
#           |                       |  - Filtrar valores      |  - Define un rango en  |
#           |                       |    extremos de acelera- |    el que la acelera-  |
#           |                       |    ción.                |    ción tiene valores  |
#           |                       |                         |    válidos.            |
#           |                       |                         |  - Notifica al monitor |
#           |                       |                         |    un segundo después  |
#           |                       |                         |    de recibir el       |
#           |                       |                         |    mensaje.            |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                             Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Establece el valor |
#           |     setUpManager()     |      int: max            |    máximo permitido   |
#           |                        |                          |    de la aceleración. |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Lee los argumentos |
#           |                        |                          |    con los que se e-  |
#           |                        |                          |    jecuta el programa |
#           |                        |                          |    para establecer el |
#           |                        |                          |    valor máximo que   |
#           |                        |                          |    puede tomar la     |
#           |                        |                          |    aceleración.       |
#           |   start_consuming()    |          None            |  - Realiza la conexi- |
#           |                        |                          |    ón con el servidor |
#           |                        |                          |    de RabbitMQ local. |
#           |                        |                          |  - Declara el tipo de |
#           |                        |                          |    tipo de intercam-  |
#           |                        |                          |    bio y a que cola   |
#           |                        |                          |    se va a subscribir.|
#           |                        |                          |  - Comienza a esperar |
#           |                        |                          |    los eventos.       |
#           +------------------------+--------------------------+-----------------------+
#           |                        |   ch: propio de Rabbit   |  - Contiene la lógica |
#           |                        | method: propio de Rabbit |    de negocio.        |
#           |       callback()       |   properties: propio de  |  - Se manda llamar    |
#           |                        |         RabbitMQ         |    cuando un evento   |
#           |                        |       String: body       |    ocurre.            |
#           +------------------------+--------------------------+-----------------------+
#
#           Nota: "propio de Rabbit" implica que se utilizan de manera interna para realizar
#            de manera correcta la recepcion de datos, para éste ejemplo no hubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#            
#
#--------------------------------------------------------------------------------------------------

import pika
import sys
from SignosVitales import SignosVitales


class AcelerometroManager:
    aceleracion_maxima = 20.0
    status = ""
    values_parameters = 0

    def setUpManager(self, max):
        self.aceleracion_maxima = max

    def start_consuming(self):
        self.values_parameters = sys.argv[1]
        self.setUpManager(self.values_parameters)
        #   +--------------------------------------------------------------------------------------+
        #   | La siguiente linea permite realizar la conexión con el servidor que aloja a RabbitMQ |
        #   +--------------------------------------------------------------------------------------+
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
        channel = connection.channel()
        #   +----------------------------------------------------------------------------------------+
        #   | La siguiente linea permite definir el tipo de intercambio y de que cola recibirá datos |
        #   +----------------------------------------------------------------------------------------+
        channel.exchange_declare(exchange='direct_acceleration',
                                 type='direct')
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        print(queue_name)
        severity = 'aceleracion'
        #   +----------------------------------------------------------------------------+
        #   | La siguiente linea permite realizar la conexión con la cola que se definió |
        #   +----------------------------------------------------------------------------+        
        channel.queue_bind(exchange='direct_acceleration',
                            queue=queue_name, routing_key=severity)
        print(' [*] Inicio de monitoreo de aceleración. Presiona CTRL+C para finalizar el monitoreo')
        #   +----------------------------------------------------------------------------------------+
        #   | La siguiente linea permite definir las acciones que se realizarán al ocurrir un método |
        #   +----------------------------------------------------------------------------------------+
        channel.basic_consume(self.callback,
                              queue=queue_name,
                              no_ack=True)
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        values = body.split(':')
        valores = values[3].replace("X  ", "").replace("Y  ", "").replace("Z  ", "").split('g')
        if float(valores[0]) > float(self.aceleracion_maxima) or float(valores[1]) > float(self.aceleracion_maxima) or float(valores[2]) > float(self.aceleracion_maxima) or float(valores[0]) < float(self.aceleracion_maxima) * -1 or float(valores[1]) < float(self.aceleracion_maxima) * -1 or float(valores[2]) < float(self.aceleracion_maxima) * -1:
            monitor = SignosVitales()
            monitor.print_notification('+----------+-----------------------+-------------------------+')
            monitor.print_notification('|   ' + str(values[3]) + '   |  ESTÁ CAYENDO  |   ' + str(values[2]) + '   |')
            monitor.print_notification('+----------+-----------------------+-------------------------+')
            monitor.print_notification('')
            monitor.print_notification('')

test = AcelerometroManager()
test.start_consuming()
