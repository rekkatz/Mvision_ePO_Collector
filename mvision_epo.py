#!/usr/bin/env/python
# Program: Event Collector MVision ePO
# Author: Cristian Rebollo Castillo

import requests
import configparser
import os
import argparse
from base64 import b64decode
from datetime import datetime, timedelta


class EPO():

    def __init__(self):

        # Ruta para comprobación y ejecución de otras funciones
        self.path = 'ABSOLUTE PATHH TO DIRECTORY SCRIPT' # <------------------------- CHANGE IT !!!!!

        # Definimos los datos que necesitamos justo al iniciar el script para petición requests
        self.auth_url = 'https://iam.mcafee-cloud.com/iam/v1.0/token'
        self.event_url = 'https://arevents.mvision.mcafee.com/eventservice/api/v1/events'
        self.headers = {'Accept' : 'application/json'}

        # Variables para establecer un time de los eventos extraídos antes y después
        now = datetime.utcnow()
        mlsecNow = repr(now).strip('datetime()').split(",")[6][:4].strip()
        self.now = now.strftime("%Y-%m-%dT%H:%M:%S.{}Z").format(mlsecNow)

        past = now - timedelta(minutes=120)
        mlsecPast = repr(past).strip('datetime()').split(",")[6][:4].strip()
        self.past = past.strftime("%Y-%m-%dT%H:%M:%S.{}Z").format(mlsecPast)

        # Creación de argumento para cliente en consola: mvision_epo.py cliente
        argvClient = argparse.ArgumentParser("mvision_epo.py")
        argvClient.add_argument("Client", help="Select client for Mvision ePO Collector", type=str)
        self.args = argvClient.parse_args()
        self.argClient = self.args.Client.upper()

        # Lectura de eventos que NO se quieren recoger
        config = configparser.ConfigParser()
        config.read("{}/general.cfg".format(self.path))

        NotEvents = config.get('MVISION_EVENTS', 'NotEvents').split(',')
        self.NotNumEvents = list(map(int, NotEvents))


    def check(self):
        """La función check comprueba si existe el directorio CONF y el archivo cliente CFG creado con el setup.py"""

        # Comprobamos si existe el directorio CONF creado al ejecutar setup.py
        if not os.path.isdir('{}/conf'.format(self.path)):
            print("\nERROR - Dont exist CONF directory, please run first setup.py")
            print("Exiting...")
            exit()
        # Comprobamos si el cliente existe en el directorio CONF, si no existe el cliente muestra un LS con los clientes disponibles
        elif not os.path.isfile('{0}/conf/{1}.cfg'.format(self.path, self.argClient)):
            print('\n[!] Client file NOT FOUND: {}.cfg'.format(self.argClient))
            print("\nCurrent files:"), os.system(' ls -1 {}/conf'.format(self.path))
            exit()


    def parser(self):
        """La función parser extrae los datos codificados del archivo CFG del cliente, a su vez, hace reversión de base64 y se definen variables self"""

        # Extracción de datos del archivo cliente.cfg y decodificación de base64. Se añaden los datos a dict para key:value
        config = configparser.ConfigParser()
        config.read("{0}/conf/{1}.cfg".format(self.path, self.argClient))

        self.client = config.get('MVISION_DATA', 'client')
        self.client_id = b64decode(config.get('MVISION_DATA', 'client_id')).decode()
        self.user = b64decode(config.get('MVISION_DATA', 'epo_user')).decode()
        self.pw = b64decode(config.get('MVISION_DATA', 'epo_pass')).decode()
        self.scope = config.get('MVISION_DATA', 'epo_scope')
        self.dir = config.get('MVISION_DATA', 'dir_events') + "{}.log".format(self.client)
        self.state = config.getint('MVISION_DATA', 'state')
        self.last_since = config.get('MVISION_DATA', 'last_since')

        self.conf = "{0}/conf/{1}.cfg".format(self.path, self.client)


    def auth(self):
        """La función auth realiza autenticación a través de API con la consola de Mvision ePO"""

        # Autenticación https para API de Mvision ePO
        data = {
            "username": self.user,
            "password": self.pw,
            "client_id": self.client_id,
            "scope": self.scope,
            "grant_type": "password"
        }

        r = requests.post(self.auth_url, headers=self.headers, data=data)

        # Se comprueba los estados de solicitud de credenciales, dependiendo del estado se aplica condicional, si el estado es 200 continua el script
        if r.status_code == 400:
            print("\n[!] - Wrong application. The parameters or format of the request may not be valid.\n")
            exit()
        elif r.status_code == 401:
            print("\nUnauthorized. Please check credentials\n")
            exit()

        self.token = r.json()['access_token']
        self.headers['Authorization'] = 'Bearer ' + self.token

        return r


    def events(self):
        """La función events comprueba la última vez que se ejecutó el recolector y realiza acciones segun la variable last_since"""

        # Se comprueba la ultima ejecución del colector, si no se ha ejecutado anteriormente se envía un since con -60 minutos desde la fecha actual
        if self.last_since == "0":
            r = requests.get(self.event_url + '?since={0}&until={1}&sort=asc'.format(self.past, self.now), headers=self.headers)
        else:
            r = requests.get(self.event_url + '?since={0}&until={1}&sort=asc'.format(self.last_since, self.now), headers=self.headers)

        evts = r.json()

        return(evts)


    def write(self, evts):

        # Extraemos key:value de name y value del diccionario donde se encuentran los eventos , añadimos a lista por cada evento e incrementamos el valor del numevent (state) y los guardamos en el archivo .log del cliente
        file = open(self.dir, 'a+')

        for event in evts['Events']:
            eventlist = []

            if event['threateventid']['value'] in self.NotNumEvents:
                continue

            event['detectedutc']['value'] = datetime.fromtimestamp(event['detectedutc']['value'] / 1000).strftime("%Y-%m-%dT%H:%M:%SZ")

            event['eventtimelocal']['value'] = datetime.fromtimestamp(event['eventtimelocal']['value'] / 1000).strftime("%Y-%m-%dT%H:%M:%SZ")

            for event_log in event.values():
                evt = "{0}: {1}".format(event_log['name'], event_log['value'])
                eventlist.append(evt)

            self.state += 1
            eventlist.insert(0, "numevent: {}".format(self.state))
            file.write(str(eventlist).strip("[]") + '\n')
        file.close()

        # Guardamos el estado del numero de evento para siguiente recolección de eventos y última ejecución para seguir un orden numérico y de estado
        config = configparser.ConfigParser()
        config.read(self.conf)
        config.set('MVISION_DATA', 'state', str(self.state))
        config.set('MVISION_DATA', 'last_since', self.now)

        with open(self.conf, 'w+') as cfgfile:
            config.write(cfgfile)
            cfgfile.close()


if __name__ == '__main__':
    try:
        epo = EPO()
        epo.check()
        epo.parser()
        epo.auth()
        events = epo.events()
        epo.write(events)
        print(epo.now + ': Successfully pulled logs from MVISION ePO.')
    except:
        print("\n[!!!] - Error when running the script. Please check that the data entered is correct. ")