#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Archivo: TemperaturaManager.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Perla Velasco & Yonathan Mtz & Alan Mercado.
# Version: 1.5.2 Marzo 2017
# Descripción:
#
#   Esta clase define el rol de un subscriptor que consume los mensajes de una cola
#   específica.
#   Las características de esta clase son las siguientes:
#
#                                        TemporizadorManager.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |  - Recibir mensajes     |  - Se subscribe a la   |
#           |      Subscriptor      |  - Notificar al         |    cola de 'direct     |
#           |                       |    monitor.             |    timer'.             |
#           |                       |                         |                        |
#           |                       |                         |                        |
#           |                       |                         |  - Notifica al monitor |
#           |                       |                         |    un segundo despues  |
#           |                       |                         |    de recibir el       |
#           |                       |                         |    mensaje.            |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en esta clase:
#
#                                             Metodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parametros        |        Funcion        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Establece el valor |
#           |     setUpManager()     |      int: max            |    máximo permitido   |
#           |                        |                          |    de tiempo para to- | 
#           |                        |                          |    mar medicinas.     |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Lee los argumentos |
#           |                        |                          |    con los que se e-  |
#           |                        |                          |    jecuta el programa |
#           |                        |                          |    para establecer el |
#           |                        |                          |    valor máximo que   |
#           |                        |                          |    puede tomar  el    |
#           |                        |                          |    tiempo que pasa
#           |                        |                          |    en tomar la medicina|
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
#            de manera correcta la recepcion de datos, para este ejemplo no hubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#            
#
#--------------------------------------------------------------------------------------------------

import pika
import sys
from SignosVitales import SignosVitales
import random


class TemporizadorManager:
    tiempo_maximo = 0
    status = ""

    def start_consuming(self):
        #   +--------------------------------------------------------------------------------------+
        #   | La siguiente línea permite realizar la conexión con el servidor que aloja a RabbitMQ |
        #   +--------------------------------------------------------------------------------------+
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
        channel = connection.channel()
        #   +----------------------------------------------------------------------------------------+
        #   | La siguiente línea permite definir el tipo de intercambio y de que cola recibirá datos |
        #   +----------------------------------------------------------------------------------------+
        channel.exchange_declare(exchange='direct_timer',
                                 type='direct')
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        severity = 'temp'
        #   +----------------------------------------------------------------------------+
        #   | La siguiente lánea permite realizar la conexión con la cola que se definió |
        #   +----------------------------------------------------------------------------+        
        channel.queue_bind(exchange='direct_timer',
                            queue=queue_name, routing_key=severity)
        print(' [*] Inicio de monitoreo de temporizador. Presiona CTRL+C para finalizar el monitoreo')
        #   +----------------------------------------------------------------------------------------+
        #   | La siguiente línea permite definir las acciones que se realizarán al ocurrir un metodo |
        #   +----------------------------------------------------------------------------------------+
        channel.basic_consume(self.callback,
                              queue=queue_name,
                              no_ack=True)
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        values = body.split(':')
        event = int(values[3])
        simul_dos = self.simulate_dosis()
        simul_med = self.simulate_data()
        if event == 10 or event == 15 or event == 20 or event == 23 or event == 21 or event == 5 or event == 2:
            monitor = SignosVitales()
            monitor.print_notification('+----------+---------------------------------------------+')
            monitor.print_notification('|   ' + str(values[3]) + ' hr  |   ' + str(values[2]) + ' debe tomar ' + str(simul_dos) + '  de ' + str(simul_med) + '       |')
            monitor.print_notification('+----------+---------------------------------------------+')
            monitor.print_notification('')
            monitor.print_notification('')
    

    def simulate_dosis(self):
        #x es el valor de la dosis que va a tener dependiendo del usuario que sea
        x = ""
        y = random.randint(int(0), int(4))
        if y == 0:
            x = "3gr"
        elif y == 1:
            x = "5gr"
        elif y == 2:
            x = "2gr"
        elif y == 3:
            x = "7gr"
        else:
            x = "1gr"                    
        return x

    def simulate_data(self):
        #i es un valor incrementable que hará variar la medicina
        i=0
        #x es el valor de la medicina que va a tener dependiendo del usuario que sea 
        x=""
        #y es una variable temporal que va a sacar el resto para clasificarlo en grupos
        y=0
        i=random.randint(int(0), int(4))
        if y == 0:
            if i==0:
                x="paracetamol"
            elif i==1:
                x="ibuprofeno"
            elif i==2:
                x="furosemida"
            elif i==3:
                x="piroxicam"
            else:
                x="tolbutamina"
        else:
            x="insulina"
                
        return x

test = TemporizadorManager()
test.start_consuming()
