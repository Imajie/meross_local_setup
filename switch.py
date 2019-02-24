#!/usr/bin/env python
import base64
import requests
import json
import time
import argparse

def _post(key, method='GET', payload={}):
    getData = {
        'header': {
            'from': '',
            'messageId': '',
            'method': method,
            'namespace': key,
            'payloadVersion': 0,
            'sign': '',
            'timestamp':0
        },
        'payload': payload
    }

    req = requests.post('http://10.10.10.1/config', json=getData)

    # return the json response if present
    try:
        ret = req.json()
    except:
        ret = {}
    return ret

def main():
    '''
    Configure the switch to connect to the local MQTT broker
    '''

    parser = argparse.ArgumentParser(description='Meross Switch Configuration')
    parser.add_argument('-b', '--broker', required=True, help='MQTT broker hostname or IP')
    parser.add_argument('-p', '--port', required=True, help='MQTT broker port')
    parser.add_argument('--timezone', default='America/New_York', help='Timezone for the switch')
    parser.add_argument('--ssid', help='SSID to connect to')
    parser.add_argument('--password', help='Wifi password')

    args = parser.parse_args()

    deviceInfo = _post('Appliance.System.All')

    mac = deviceInfo['payload']['all']['system']['hardware']['macAddress']
    uuid = deviceInfo['payload']['all']['system']['hardware']['uuid']
    print('Configuring MAC=%s, UUID=%s' % (mac, uuid))

    _post('Appliance.Config.Trace', payload={'trace':{}})

    # setup MQTT settings
    _post('Appliance.Config.Key', method='SET', payload={
               'key': {
                   'gateway': {
                       'host': args.broker,
                       'port': args.port,
                       'secondHost': args.broker,
                       'secondPort': args.port
                   },
                   'key': uuid,
                   'userId': uuid
               }
           })

    # Get wifi list
    wifiList = _post('Appliance.Config.WifiList')['payload']['wifiList']
    if args.ssid is None:
        for i, entry in enumerate(wifiList):
            print('[%d]: %s [%d%%]' % (i,
                base64.b64decode(entry['ssid']).decode('utf-8'),
                entry['signal']
                ))

        wifiId = int(input('Enter wifi number: '))
        wifi = wifiList[wifiId]
        print('Selected %i: %s' % (wifiId, str(wifiList[wifiId])))
    else:
        for entry in wifiList:
            if args.ssid == base64.b64decode(entry['ssid']).decode('utf-8'):
                wifi = entry
                break
        else:
            print('Error: SSID %s not found' % args.ssid)
            sys.exit(1)

    del wifi['signal']

    if wifi['encryption'] != 0:
        if args.password is None:
            wifiPass = input('Wifi password: ')
        else:
            wifiPass = args.password
        # Base64 encode the password
        wifi['password'] = base64.b64encode(wifiPass.encode('ASCII')).decode('utf-8')

    _post('Appliance.System.All')

    # set time, time rules don't seem to change with different configurations
    _post('Appliance.System.Time', method='SET', payload={ 'time': {
                'timeRule': [
                    [ 1541311200, -18000, 0],
                    [ 1552201200, -14400, 1],
                    [ 1572760800, -18000, 0],
                    [ 1583650800, -14400, 1],
                    [ 1604210400, -18000, 0],
                    [ 1615705200, -14400, 1],
                    [ 1636264800, -18000, 0],
                    [ 1647154800, -14400, 1],
                    [ 1667154400, -18000, 0],
                    [ 1678604400, -14400, 1],
                    [ 1699164000, -18000, 0],
                    [ 1710054000, -14400, 1],
                    [ 1730613600, -18000, 0],
                    [ 1741503600, -14400, 1],
                    [ 1762063200, -18000, 0],
                    [ 1772953200, -14400, 1],
                    [ 1793512800, -18000, 0],
                    [ 1805007600, -14400, 1],
                    [ 1825567200, -18000, 0],
                    [ 1836457200, -14400, 1]
                ],
                'timestamp': round(time.time()),
                'timezone': args.timezone
            }
        })

    # Setup wifi
    _post('Appliance.Config.Wifi', method='SET', payload={ 'wifi': wifi })

    print('Configuration complete, switch will now reboot')

if __name__ == '__main__':
    main()
