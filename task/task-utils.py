import time
import inspect
import json
import util.common as common
import jmespath

# Global dictionary to store variables
gdict={}

# Function to get the name of the calling function
myself = lambda: inspect.stack()[1][3]

def setgdict(self, gdict):
    """
    Sets the global dictionary reference
    
    Args:
        self: The class instance
        gdict: Dictionary to be set as global dictionary
    """
    self.gdict = gdict
    
def jsonxpath(self, param):
    """
    Extracts data from JSON using JMESPath expression
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - jsonvar: Variable name containing JSON data
            - xpath: JMESPath expression to apply
            - printout (optional): Flag to print the result
            - saveonvar (optional): Variable name to save the result
    """
    common.logstart(myself())
    if common.checkandloadparam(self, myself(), ('jsonvar', 'xpath'), param):
        data = gdict[param['jsonvar']]
        vxpath = param['xpath']
        valjmes = jmespath.search(vxpath, data)
        if common.checkparam('printout', param):
            printout = param['printout']
            if printout:
                print(valjmes)
        if common.checkparam('saveonvar', param):
            saveonvar = param['saveonvar']
            gdict[saveonvar] = valjmes
    common.logend(myself())
            
def setsleep(self, param):
    """
    Pauses execution for specified number of seconds
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - seconds: Number of seconds to sleep
    """
    common.logstart(myself())
    if common.checkandloadparam(self, myself(), ('seconds',), param):
        seconds = gdict['seconds']
        time.sleep(seconds)
        common.logend(myself())
    else:
        exit()


def printvar(self, param):
    """
    Prints the value of a variable from the global dictionary
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - varname: Name of the variable to print
    """
    common.logstart(myself())
    if common.checkandloadparam(self, myself(), ('varname',), param):
        varname = gdict['varname']
        print(gdict[varname])
        common.logend(myself())
    else:
        exit()
        

def setvar(self, param):
    """
    Sets a variable in the global dictionary
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - varname: Name of the variable to set
            - varvalue: Value to assign to the variable
    """
    common.logstart(myself()) 
    if common.checkandloadparam(self, myself(), ('varname', 'varvalue'), param):
        varname = gdict['varname']
        varvalue = gdict['varvalue']
        gdict[varname] = varvalue
        common.logend(myself())
    else:
        exit()

def dumpvar(self, param):
    """
    Dumps the global dictionary as formatted JSON
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - savetofile (optional): Filename to save the dumped dictionary
    """
    if common.checkparam('savetofile', param):
        savetofile = param['savetofile']
        common.writefile(savetofile, json.dumps(self.gdict, indent=4, sort_keys=True))
    print(json.dumps(self.gdict, indent=4, sort_keys=True))

def loadvarfromjson(self, param):
    """
    Loads variables from a JSON file into the global dictionary
    
    Args:
        self: The class instance
        param: Dictionary containing parameters:
            - filename: Path to the JSON file to load
    """
    common.logstart(myself())
    if common.checkandloadparam(self, myself(), ('filename', ), param):
        filename = common.effify(gdict['filename'], gdict)
        with open(filename, 'r') as f:
            data = f.read()
            jdata = json.loads(data)
            for d in jdata.keys():
                gdict[d] = jdata.get(d)
        common.logend(myself())
    else:
        exit()