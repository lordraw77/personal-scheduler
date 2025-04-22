import time
import inspect
import json
import util.common as common
gdict={}

myself = lambda: inspect.stack()[1][3]

def setgdict(self,gdict):
    self.gdict=gdict
    
def setsleep(self,param):
    common.logstart(myself())
    if common.checkandloadparam(self,myself(),('seconds',),param):
        seconds=gdict['seconds']
        time.sleep(seconds)
        common.logend(myself())
    else:
        exit()


def printvar(self,param):
    common.logstart(myself())
    if common.checkandloadparam(self,myself(),('varname',),param):
        varname=gdict['varname']
        
        print (gdict[varname])
        common.logend(myself())
    else:
        exit()
        

def setvar(self,param):   
    common.logstart(myself()) 
    if common.checkandloadparam(self,myself(),('varname','varvalue'),param):
        varname=gdict['varname']
        varvalue=gdict['varvalue']
        gdict[varname] = varvalue
        common.logend(myself())
    else:
        exit()

def dumpvar(self,param):
    if common.checkparam('savetofile',param):
        savetofile=param['savetofile']
        common.writefile(savetofile,json.dumps(self.gdict, indent=4, sort_keys=True))
    print(json.dumps(self.gdict, indent=4, sort_keys=True))

def loadvarfromjson(self,param):
    common.logstart(myself())
    if common.checkandloadparam(self,myself(),('filename', ),param):
        
        filename=common.effify(gdict['filename'],gdict)
        with open(filename,'r') as f:
            data = f.read()
            jdata = json.loads(data)
            for d in jdata.keys():
                gdict[d]=jdata.get(d)
        common.logend(myself())
    else:
        exit()
        