# -*- coding: utf-8 -*-

import os
import requests
from datetime import datetime
# parse 8601 duration
from re import findall

def iso8601_duration_as_seconds( d ):
    if d[0] != 'P':
        raise ValueError('Not an ISO 8601 Duration string')
    seconds = 0
    # split by the 'T'
    for i, item in enumerate(d.split('T')):
        for number, unit in findall( '(?P<number>\d+)(?P<period>S|M|H|D|W|Y)', item ):
            # print '%s -> %s %s' % (d, number, unit )
            number = int(number)
            this = 0
            if unit == 'Y':
                this = number * 31557600 # 365.25
            elif unit == 'W':
                this = number * 604800
            elif unit == 'D':
                this = number * 86400
            elif unit == 'H':
                this = number * 3600
            elif unit == 'M':
                # ambiguity ellivated with index i
                if i == 0:
                    this = number * 2678400 # assume 30 days
                    # print "MONTH!"
                else:
                    this = number * 60
            elif unit == 'S':
                this = number
            seconds = seconds + this
    return seconds

def getMinimumTime (A, B):
    url = f"https://transit.api.here.com/v3/route.json"
    deplocation = A # отправка
    arrlocation = B # прибытие
    app_id = os.getenv('HERE_API_ID')
    app_code = os.getenv('HERE_APP_CODE')

    maybeDriveWay = dict ()

    # https://developer.here.com/api-explorer/rest/public_transit/public-transit-routing
    # Plan a route from A to B using Public Transport
    query = {
                'dep': deplocation,
                'arr': arrlocation,
                'time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'app_id': app_id,
                'app_code': app_code,
                'routing': 'tt',
                'details': '1'
            }

    response = requests.get(url, params=query)
    data = response.json()
    status = data["Res"]
    message = "Message" in status

   # if message:
   #     print(status["Message"])
   #     exit(-1)

    if "Connections" in status:
        # first route from list
        route_dut_time = iso8601_duration_as_seconds( status["Connections"]["Connection"][0]["duration"] )
        print ( "Public Transport route time {} second".format( route_dut_time ) )
        maybeDriveWay [route_dut_time] = 'Public Transport'
    '''
        route = status["Connections"]["Connection"][0]["Sections"]["Sec"]
        for sec in route:
            if sec["mode"] == 20:
                print ("walk mode")
                print ("distance: ", sec["Journey"]["distance"])
                print ("duration: ", sec["Journey"]["duration"])
                if "Stn" in sec["Arr"]:
                    print ( "walk from {} to station: {} ({})".format( sec["Dep"]["Addr"], sec["Arr"]["Stn"]["name"], sec["Arr"]["Stn"]["id"]))
                if "Stn" in sec["Dep"]:
                    print ( "walk from station: {} ({}) to {}".format( sec["Dep"]["Stn"]["name"], sec["Dep"]["Stn"]["id"], sec["Arr"]["Addr"]))
            elif sec["mode"] == 5:
                print ("bus mode")
                print ("bus number: ", sec["Dep"]["Transport"]["name"] )
                print ("distance: ", sec["Journey"]["distance"])
                print ("duration: ", sec["Journey"]["duration"])
                stops = sec["Journey"]["Stop"]
                delta = datetime.strptime(sec["Dep"]["time"], '%Y-%m-%dT%H:%M:%S')
                for stop in stops:
                    if "dep" in stop:
                        print ("bus stop: {} ({}), departure time: {}, delta: {}".format( stop["Stn"]["name"], stop["Stn"]["id"], stop["dep"], datetime.strptime(stop["dep"], '%Y-%m-%dT%H:%M:%S') - delta))
                    elif "arr" in stop:
                        print ("bus stop: {} ({}), arrival time: {}, delta {}".format( stop["Stn"]["name"], stop["Stn"]["id"], stop["arr"], datetime.strptime(stop["arr"], '%Y-%m-%dT%H:%M:%S') - delta))
    '''
    # https://developer.here.com/api-explorer/rest/routing/route-from-a-to-b
    # Car route from A to B

    url = f"https://route.api.here.com/routing/7.2/calculateroute.json"

    query = {
                'waypoint0': deplocation,
                'waypoint1': arrlocation,
                'mode': 'fastest;car;traffic:enabled',
                'app_id': app_id,
                'app_code': app_code,
                'departure': 'now'
            }

    response = requests.get(url, params=query)
    data = response.json()
    #print(data['response']['route'][0]['summary']['distance'])
    #print(data['response']['route'][0]['summary']['trafficTime'])
    try:
        print ( "Car route distance {}".format( data['response']['route'][0]['summary']['distance'] ) )
        print ( "Car route time {} second".format( data['response']['route'][0]['summary']['trafficTime'] ) )
        maybeDriveWay[data['response']['route'][0]['summary']['trafficTime']] = 'Car'
    except:
        print("request error")

    # https://developer.here.com/api-explorer/rest/routing/route-from-a-to-b-pedestrian
    # Pedestrian route from A to B

    url = f"https://route.api.here.com/routing/7.2/calculateroute.json"

    query = {
                'waypoint0': deplocation,
                'waypoint1': arrlocation,
                'mode': 'fastest;pedestrian',
                'app_id': app_id,
                'app_code': app_code
            }

    response = requests.get(url, params=query)
    data = response.json()
    #print(data['response']['route'][0]['summary']['distance'])
    #print(data['response']['route'][0]['summary']['travelTime'])
    try:
        print ( "Pedestrian route distance {}".format( data['response']['route'][0]['summary']['distance'] ) )
        print ( "Pedestrian route time {} second".format( data['response']['route'][0]['summary']['travelTime'] ) )
        maybeDriveWay[data['response']['route'][0]['summary']['travelTime']] = 'Pedestrian'
        keys = sorted(maybeDriveWay.keys())
        print ( "Use '{}' mode for motion".format( maybeDriveWay[keys[0]] ) )
        return keys[0]
    except:
        print("request error")
        return -1
    return -1
