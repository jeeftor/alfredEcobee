# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
from workflow import Workflow3, web, notify
import requests

import urllib2
import urllib
import json

class Ecobee3(object):
    def __init__(self):

        self.wf = Workflow3()
        self.api_key = self.wf.stored_data('APP_KEY')
        self.access_token = self.wf.stored_data('ACCESS_TOKEN')
        self.refresh_token = self.wf.stored_data('REFRESH_TOKEN')
        self.log = self.wf.logger

    def get_headers(self):
        """Autogenerates headers for all requests"""
        return {'authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/json',
                'charset':'UTF-8'
                }


    def __update_tokens(self):
        """Updaets the acess and refresh tokens!!"""

        url = 'https://api.ecobee.com/token?grant_type=refresh_token&code={}&client_id={}'.format(self.refresh_token,self.api_key)

        self.log.info("TOKEN REFRESH: Making update query to {}".format(url))

        response = requests.request("POST", url)

        self.log.info( response.text)

        # Update tokens
        self.access_token = response.json()['access_token']
        self.refresh_token = response.json()['refresh_token']
        self.wf.store_data('ACCESS_TOKEN', response.json()['access_token'])
        self.wf.store_data('REFRESH_TOKEN', response.json()['refresh_token'])




    def get_with_params(self, url, params):
        """Perform a get with a set of paramaters - and if things go awry just try to refresh the tokens"""

        response = requests.request("GET", url, headers=self.get_headers(), params=params)

        if response.json()['status']['code'] == 16:
            raise Exception('Token Error - you must reauthorize this plugin with the "eauth" command')

        if response.json()['status']['code'] == 14:
            self.log.info( "Refreshing authorization tokens")
            self.__update_tokens()
            self.log.info( "Retrying query to {}".format(url))
            response = requests.request("GET", url, headers=self.get_headers(), params=params)

        if response.status_code != 200:
            return response

        else:
            return response


    def get_summary(self):
        """Returs summary data for the system - only will run every 3 minutes, otherwise cached data will be returned"""

        def get_data():
            url = "https://api.ecobee.com/1/thermostatSummary"
            jsonData = {
                "selection": {"selectionType": "registered",
                            "selectionMatch": "",
                            "includeEquipmentStatus": 'true'}
            }

            querystring = {"json": json.dumps(jsonData)}

            response = self.get_with_params(url, querystring)

            self.log.info(response.text)

            return response.json()

        return self.wf.cached_data('summary', get_data, max_age=1)

    def get_thermostats(self):

        def get_data():

            url = 'https://api.ecobee.com/1/thermostat'
            jsonData = { "selection" : {
                "selectionType":"registered",
                "selectionMatch":"",
                "includeSensors":'true'}
            }

            querystring = {"json": json.dumps(jsonData)}
            response = self.get_with_params(url, querystring)
            # self.log.info(response.text)
            return response.json()

        return self.wf.cached_data('getThermostats', get_data, max_age=1)


def extract_capabilities(json):

    ret = dict()
    for c in json:
        ret[c['type']] = c['value']
    return ret

def main(wf):

    e = Ecobee3()
    e.get_summary()
    tdata = e.get_thermostats()

    # print json.dumps(tdata, indent=4, separators=(',', ': '))

    for therm in tdata['thermostatList']:
        for sensor in therm['remoteSensors']:
            name = sensor['name']
            type = sensor['type']
            capabilities = extract_capabilities(sensor['capability'])

            if type == 'ecobee3_remote_sensor':
                img = '../images/sensor.png'
            else:
                img = '../images/main_unit.png'

            title = "{} : {} ℉".format(name, capabilities['temperature'])
            subtitle = 'Occupancy: ' + capabilities['occupancy']
            if capabilities.get('humidity'):
                subtitle += ' Humidity: {}%'.format(capabilities['humidity'])

            wf.add_item(name, subtitle, icon=img, valid=False)

    wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
