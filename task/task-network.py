import json
import requests
import util.common as common
import inspect
import http.client

gdict={}

def setgdict(self,gdict):
    self.gdict=gdict

myself = lambda: inspect.stack()[1][3]



def httpget(self,param):
    """
    - name: make http get 
      task-network.httpget: 
        host: 10.70.1.15
        port: 9999
        get:/
        printout: True #optional default false 
        saveonvar: outputvar #optional save output in var
        
    """  
    common.logstart(myself())

    if common.checkandloadparam(self,myself(),('host','port','get'),param):
        try:
            host = common.effify(gdict['host'])
            port=  int(common.effify(gdict['port']))
            get=  gdict['get']
            connection = http.client.HTTPConnection(host,port)
            connection.request("GET", get)
            response = connection.getresponse()
            print(f"Status: {response.status} and reason: {response.reason}")
            output= response.read().decode()
            if common.checkparam('printout',param):
                printout=param['printout']
                if printout:
                    print(output)
            if common.checkparam('saveonvar',param):
                saveonvar=param['saveonvar']
                gdict[saveonvar]=output

            connection.close()
        except Exception as e:
            print(e)
        common.logend(myself())
    else:
        exit()
        
        
def httpspost(self,param):
    """
    - name: make https post 
      task-network.httpspost: 
         host: w3vcs05.emslabw3.local
        port: 443
        get:/
        payload: [{"id":"aaa}]
        headers: headers
        verify: True #optional default false
        printout: True #optional default false 
        saveonvar: outputvar #optional save output in var
        
    """      
    common.logstart(myself())

    if common.checkandloadparam(self,myself(),('host','port','get','payload'),param):
        verify=False
        if common.checkparam('verify',param):
            verify=param['verify']
        host = common.effify(gdict['host'],gdict)
        port=  int(gdict['port'])
        get=   common.effify(gdict['get'],gdict)
        payload =  json.loads(common.effify(gdict['payload'],gdict).replace("None", "null"))[0]
        headers= json.loads(param['headers'].replace("'", "\""))[0]
        if str(port) == "443":
            url = f"https://{host}{get}"
        else:
            url = f"https://{host}:{port}{get}"
        response = requests.post( url, headers=headers, json=payload)
        output = json.loads(response.text)
        if common.checkparam('printout',param):
            printout=param['printout']
            if printout:
                print(output)
        if common.checkparam('saveonvar',param):
            saveonvar=param['saveonvar']
            gdict[saveonvar]=output
        common.logend(myself())
    
       
def httpsget(self,param):
    """
    - name: make http get 
      task-network.httpsget: 
        host: w3vcs05.emslabw3.local
        port: 443
        get:/
        verify: True #optional default false
        printout: True #optional default false 
        saveonvar: outputvar #optional save output in var
        
    """  
    common.logstart(myself())

    if common.checkandloadparam(self,myself(),('host','port','get','payload'),param):
        try:
            host = common.effify(gdict['host'],gdict)
            port=  int(common.effify(gdict['port']),gdict)
            get=  gdict['get']
            verify=False
            if common.checkparam('verify',param):
                verify=param['verify']
            response = requests.get(f'https://{host}:{port}{get}', verify = verify)
            print(f"Status: {response.status_code} and reason: {response.reason}")
            output= response.content
            if common.checkparam('printout',param):
                printout=param['printout']
                if printout:
                    print(output)
            if common.checkparam('saveonvar',param):
                saveonvar=param['saveonvar']
                gdict[saveonvar]=output
        except Exception as e:
            print(e)
        common.logend(myself())
    else:
        exit()


