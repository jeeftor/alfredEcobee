# -*- coding: utf-8 -*-

import sys
from workflow import Workflow3
import requests
from ecobee import Ecobee3


def extract_capabilities(json):

    ret = dict()
    for c in json:
        ret[c['type']] = c['value']
    return ret


def main(wf):

    e = Ecobee3()
    tdata = e.get_thermostats()

    # print json.dumps(tdata, indent=4, separators=(',', ': '))

    for therm in tdata['thermostatList']:
        for sensor in therm['remoteSensors']:
            name = sensor['name']
            type = sensor['type']
            capabilities = extract_capabilities(sensor['capability'])

            if type == 'ecobee3_remote_sensor':
                img = 'images/sensor.png'
            else:
                img = 'images/main_unit.png'

            title = "{} : {} ℉".format(name, int(capabilities['temperature']) / 10.0)
            subtitle = 'Occupancy: ' + capabilities['occupancy']
            if capabilities.get('humidity'):
                subtitle += ' Humidity: {}%'.format(capabilities['humidity'])

            wf.add_item(title, subtitle, icon=img, valid=False)

    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
