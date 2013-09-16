import argparse
import requests
import sys
import json
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
    
'''
Created on 13.09.2013

@author: Marco Hoyer
'''
    
def exit_ok(message):
    print "OK - " + message
    sys.exit(0)
    
def exit_warning(message):
    print "WARNING - " + message
    sys.exit(1)
    
def exit_critical(message):
    print "CRITICAL - " + message
    sys.exit(2)
        
def exit_unknown(message):
    print "UNKNOWN - " + message
    sys.exit(3)
    
def get_perfdata(key,value):
        return "|" + str(key).lower() + "=" + str(value)
    
def get_url(targethost, port, uri):
    return "http://%s:%d%s" % (targethost,port, uri)
    
def get_by_http(url):
    try:
        response = requests.get(url)
    except Exception as e:
        exit_unknown(repr(e))
    if (response.status_code == 200):
        return (response.text, response.headers['content-type'])
    else:
        exit_unknown("server responded with status-code " + str(response.status_code))
        return None
    
def check_value(key, value, warning, critical, inverse):
    if inverse:
        if (value > warning):
            exit_ok("value: " + str(value) + get_perfdata(key,value))
        elif (value > critical):
            exit_warning("value: " + str(value) + " (is below warning treshold of " + str(warning) + ")" + get_perfdata(key,value))
        else:
            exit_critical("value: " + str(value) + " (is below critical treshold of " + str(critical) + ")" + get_perfdata(key,value))
    else:
        if (value < warning):
            exit_ok("value: " + str(value) + get_perfdata(key,value))
        elif (value < critical):
            exit_warning("value: " + str(value) + " (exceeds warning treshold of " + str(warning) + ")" + get_perfdata(key,value))
        else:
            exit_critical("value: " + str(value) + " (exceeds critical treshold of " + str(critical) + ")" + get_perfdata(key,value))
        
def check_tresholds(warning, critical, inverse):
    if (warning == critical):
        exit_unknown("warning and critical cannot be equal")
    if inverse:
        if (warning <= critical):
            exit_unknown("warning must be bigger than critical")
    else:
        if (warning >= critical):
            exit_unknown("warning must be lower than critical")

def parse_yaml(raw_data):
    yaml_data = load(raw_data, Loader=Loader)
    return yaml_data

def parse_json(raw_data):
    json_data = json.load(raw_data)
    return json_data

def find_value_for_key(data, key):
    try:
        return int(data[key])
    except KeyError:
        exit_unknown("key not found in server response")
    except ValueError:
        exit_unknown("value found for given key is not an integer")

def get_dict_from_response(response):
    if (response[1].__contains__("yaml")):
        return parse_yaml(response[0])
    elif (response[1].__contains__("json")):
        return parse_json(response[0])
    else:
        exit_unknown("unknown content type: " + response[1] + " (use json or yaml)")

# main action
def main(args):
    url = get_url("localhost",80,"/testsite?query=STATUSFILEAGETT")
    response = get_by_http(url)
    data = get_dict_from_response(response)
    value = find_value_for_key(data, "STATUSFILEAGETT")
    check_value("STATUSFILEAGETT",int(value), 5, 8, False)
    

# parameter handling separation
if __name__ == '__main__':
    # parameter handling
    parser = argparse.ArgumentParser(description='Checks for values in a key-value yaml dict offered by http')
    parser.add_argument("--debug", help="show debug output", action="store_true")
    parser.add_argument("--warning", help="warning thresholds", type=int)
    parser.add_argument("--critical", help="critical thresholds", type=int)
    parser.add_argument("--inverse", help="invert thresholds", action="store_true")
    parser.add_argument("--hostname", help="hostname", type=str)
    parser.add_argument("--port", help="port",type=int)
    parser.add_argument("--url", help="url for resource to query", type=str)
    parser.add_argument("--key", help="key to query a value for", type=str)
    args = parser.parse_args()
    main(args)