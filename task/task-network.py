import json
import requests
import util.common as common
import inspect
import http.client

# Global dictionary to store variables
gdict={}

def setgdict(self, gdict):
    """
    Sets the global dictionary reference
    
    Args:
        self: The class instance
        gdict: Dictionary to be set as global dictionary
    """
    self.gdict = gdict

# Function to get the name of the calling function
myself = lambda: inspect.stack()[1][3]


def httpget(self, param):
    """
    Performs an HTTP GET request using http.client
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - host: Target hostname
            - port: Target port number
            - get: URL path for the GET request
            - printout (optional): Flag to print the response
            - saveonvar (optional): Variable name to store the response
    """
    common.logstart(myself())
    if common.checkandloadparam(self, myself(), ('host', 'port', 'get'), param):
        try:
            host = common.effify(gdict['host'])
            port = int(common.effify(gdict['port']))
            get = gdict['get']
            connection = http.client.HTTPConnection(host, port)
            connection.request("GET", get)
            response = connection.getresponse()
            print(f"Status: {response.status} and reason: {response.reason}")
            output = response.read().decode()
            if common.checkparam('printout', param):
                printout = param['printout']
                if printout:
                    print(output)
            if common.checkparam('saveonvar', param):
                saveonvar = param['saveonvar']
                gdict[saveonvar] = output

            connection.close()
        except Exception as e:
            print(e)
        common.logend(myself())
    else:
        exit()
        
        
def httpspost(self, param):
    """
    Performs an HTTPS POST request using the requests library
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - host: Target hostname
            - port: Target port number
            - get: URL path for the POST request
            - payload: JSON data to send in the request body
            - headers: Headers to include in the request
            - verify (optional): SSL certificate verification flag
            - printout (optional): Flag to print the response
            - saveonvar (optional): Variable name to store the response
    """
    common.logstart(myself())
    if common.checkandloadparam(self, myself(), ('host', 'port', 'get', 'payload'), param):
        verify = False
        if common.checkparam('verify', param):
            verify = param['verify']
        host = common.effify(gdict['host'], gdict)
        port = int(gdict['port'])
        get = common.effify(gdict['get'], gdict)
        payload = json.loads(common.effify(gdict['payload'], gdict).replace("None", "null"))
        if isinstance(payload, list):
            payload = payload[0]
            
        headers = json.loads(param['headers'].replace("'", "\""))
        if isinstance(headers, list):
            headers = headers[0]
            
        if str(port) == "443":
            url = f"https://{host}{get}"
        else:
            url = f"https://{host}:{port}{get}"
        response = requests.post(url, headers=headers, json=payload)
        output = json.loads(response.text)
        if common.checkparam('printout', param):
            printout = param['printout']
            if printout:
                print(output)
        if common.checkparam('saveonvar', param):
            saveonvar = param['saveonvar']
            gdict[saveonvar] = output
        common.logend(myself())
    
def httpsget(self, param):
    """
    Performs an HTTPS GET request using the requests library
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - host: Target hostname
            - port: Target port number
            - get: URL path for the GET request
            - verify (optional): SSL certificate verification flag
            - printout (optional): Flag to print the response
            - saveonvar (optional): Variable name to store the response
    """
    common.logstart(myself())

    if common.checkandloadparam(self, myself(), ('host', 'port', 'get'), param):
        try:
            host = common.effify(gdict['host'], gdict)
            port = int(common.effify(gdict['port']), gdict)
            get = gdict['get']
            verify = False
            if common.checkparam('verify', param):
                verify = param['verify']
            response = requests.get(f'https://{host}:{port}{get}', verify=verify)
            print(f"Status: {response.status_code} and reason: {response.reason}")
            output = response.content
            if common.checkparam('printout', param):
                printout = param['printout']
                if printout:
                    print(output)
            if common.checkparam('saveonvar', param):
                saveonvar = param['saveonvar']
                gdict[saveonvar] = output
        except Exception as e:
            print(e)
        common.logend(myself())
    else:
        exit()