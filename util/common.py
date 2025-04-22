from string import Formatter
from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor
from datetime import datetime, time
import requests
import json


logstart= lambda x: print(f"start {x:.<30}...")
logend  = lambda x: print(f"end   {x:.<30}...") 

def load_env_parameter(envparma, env : dict,CONFIG: dict):
    CONFIG[envparma] = "na"
    try:
        CONFIG[envparma] = env[envparma]
    except:
        pass    
    return  CONFIG.copy()

def format_message(template, **kwargs):
    class SafeFormatter(Formatter):
        def get_value(self, key, args, kwargs):
            try:
                return super().get_value(key, args, kwargs)
            except (KeyError, IndexError):
                return '{' + key + '}'
    formatter = SafeFormatter()
    return formatter.format(template, **kwargs)


def mng_library(libs):
    if libs:
        for lib in libs.split(","):
            install_and_import(lib)
            
            
def calcolateformatted_timestamp(CONFIG):
    from datetime import datetime
    import pytz

    # Ottieni il timestamp attuale nel fuso orario di Roma
    _tz = pytz.timezone(CONFIG.TIMEZONE)
    _time = datetime.now(_tz)

    # Formatta il timestamp come stringa (per SQLite)
    return  _time.strftime('%Y-%m-%d %H:%M:%S')
    
def crondecode(cronexpr):
    options = Options()
    options.throw_exception_on_parse_error = True
    options.casing_type = CasingTypeEnum.Sentence
    options.use_24hour_time_format = True
    descriptor = ExpressionDescriptor(cronexpr, options)
    return descriptor.get_description(DescriptionTypeEnum.FULL)

def is_time_between(begin_time, end_time, check_time=None):
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: 
        return check_time >= begin_time or check_time <= end_time

def effify(non_f_str: str,gdict):
    globals().update(gdict)
    if "{" in non_f_str:
        msg=non_f_str
        try:
            msg= eval(f'f"""{non_f_str}"""')
        except:
            pass
        return msg
    else:
        return non_f_str
    
def check_parma_and_load(ddict,nomeparam):
    retval =""
    try:
        retval = ddict[nomeparam]
    except:
        retval = None
    return retval

def check_parma_and_load(ddict,nomeparam,default=None):
    retval =""
    try:
        retval = ddict[nomeparam]
    except:
        if default!=None:
            retval=default
        else:
            retval = None
    return retval

def check_for_notify(notify):
    return True

def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
        import site
        from importlib import reload
        reload(site)
    finally:
        globals()[package] = importlib.import_module(package)

def checkandloadparam(self,modulename,paramneed,param ):
    ret=True
    for par in paramneed:
        if par in param:
            self.gdict[par]= param.get(par)
        else:
            print(f'the param {par} need for {modulename}, nedded parameter are {paramneed}')
            ret=False
            break
    return ret


def checkparam(paramname, param):
    ret=False
    if paramname in param:
        ret=True
    return ret

def silent_execution(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            pass
    return wrapper