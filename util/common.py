from string import Formatter
from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor
from datetime import datetime, time
import requests
import json

# Lambda functions to log the start and end of operations with formatted output
logstart = lambda x: print(f"start {x:.<30}...")
logend = lambda x: print(f"end   {x:.<30}...")

def load_env_parameter(envparma, env: dict, CONFIG: dict):
    """
    Loads environment parameter from an environment dictionary into a CONFIG dictionary.
    If the parameter doesn't exist, sets it to "na" as default value.
    
    Args:
        envparma: Name of the environment parameter to load
        env: Dictionary containing environment variables
        CONFIG: Configuration dictionary to update
        
    Returns:
        Updated CONFIG dictionary with the parameter added
    """
    CONFIG[envparma] = "na"
    try:
        CONFIG[envparma] = env[envparma]
    except:
        pass    
    return CONFIG.copy()

def format_message(template, **kwargs):
    """
    Formats a string template with provided variables.
    Uses a SafeFormatter to prevent errors when a variable isn't provided.
    Missing variables are kept as {variable_name} in the output.
    
    Args:
        template: String template to format
        **kwargs: Variables to insert into the template
        
    Returns:
        Formatted string
    """
    class SafeFormatter(Formatter):
        def get_value(self, key, args, kwargs):
            try:
                return super().get_value(key, args, kwargs)
            except (KeyError, IndexError):
                return '{' + key + '}'
    formatter = SafeFormatter()
    return formatter.format(template, **kwargs)

def mng_library(libs):
    """
    Manages external libraries by installing and importing them.
    Takes a comma-separated string of library names.
    
    Args:
        libs: Comma-separated string of library names to install and import
    """
    if libs:
        for lib in libs.split(","):
            install_and_import(lib)
            
def calcolateformatted_timestamp(CONFIG):
    """
    Calculates and formats the current timestamp in the timezone specified in CONFIG.
    
    Args:
        CONFIG: Configuration dictionary with TIMEZONE key
        
    Returns:
        Formatted timestamp string in 'YYYY-MM-DD HH:MM:SS' format
    """
    from datetime import datetime
    import pytz

    # Get current timestamp in Rome timezone
    _tz = pytz.timezone(CONFIG.TIMEZONE)
    _time = datetime.now(_tz)

    # Format timestamp as string (for SQLite)
    return _time.strftime('%Y-%m-%d %H:%M:%S')
    
def crondecode(cronexpr):
    """
    Decodes a cron expression into a human-readable description.
    
    Args:
        cronexpr: Cron expression string (e.g. "0 0 * * *")
        
    Returns:
        Human-readable description of the cron schedule
    """
    options = Options()
    options.throw_exception_on_parse_error = True
    options.casing_type = CasingTypeEnum.Sentence
    options.use_24hour_time_format = True
    descriptor = ExpressionDescriptor(cronexpr, options)
    return descriptor.get_description(DescriptionTypeEnum.FULL)

def is_time_between(begin_time, end_time, check_time=None):
    """
    Checks if a specific time is between two other times.
    Handles cases where the time range crosses midnight.
    
    Args:
        begin_time: Start time
        end_time: End time
        check_time: Time to check (defaults to current time)
        
    Returns:
        Boolean indicating if check_time is between begin_time and end_time
    """
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: 
        return check_time >= begin_time or check_time <= end_time

def effify(non_f_str: str, gdict):
    """
    Converts a regular string with curly braces to an f-string by evaluating it.
    Uses a global dictionary to provide variables for interpolation.
    
    Args:
        non_f_str: String with potential {variable} placeholders
        gdict: Dictionary of variables to use for interpolation
        
    Returns:
        String with variables interpolated
    """
    globals().update(gdict)
    if "{" in non_f_str:
        msg = non_f_str
        try:
            msg = eval(f'f"""{non_f_str}"""')
        except:
            pass
        return msg
    else:
        return non_f_str
    
def check_parma_and_load(ddict, nomeparam):
    """
    Checks if a parameter exists in a dictionary and returns its value.
    If the parameter doesn't exist, returns None.
    
    Args:
        ddict: Dictionary to check for parameter
        nomeparam: Name of parameter to look for
        
    Returns:
        Parameter value or None
    """
    retval = ""
    try:
        retval = ddict[nomeparam]
    except:
        retval = None
    return retval

def check_parma_and_load(ddict, nomeparam, default=None):
    """
    Checks if a parameter exists in a dictionary and returns its value.
    If the parameter doesn't exist, returns the default value if provided, otherwise None.
    
    Args:
        ddict: Dictionary to check for parameter
        nomeparam: Name of parameter to look for
        default: Default value to return if parameter doesn't exist
        
    Returns:
        Parameter value, default value, or None
    """
    retval = ""
    try:
        retval = ddict[nomeparam]
    except:
        if default != None:
            retval = default
        else:
            retval = None
    return retval

def check_for_notify(notify):
    """
    Placeholder function to check notification settings.
    Currently always returns True.
    
    Args:
        notify: Notification settings (not used currently)
        
    Returns:
        Always returns True
    """
    return True

def install_and_import(package):
    """
    Dynamically installs and imports a Python package.
    If the package is already installed, just imports it.
    Makes the package available in the global namespace.
    
    Args:
        package: Name of the package to install and import
    """
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

def checkandloadparam(self, modulename, paramneed, param):
    """
    Checks if required parameters are present and loads them into the global dictionary.
    
    Args:
        self: Object instance containing a global dictionary (gdict)
        modulename: Name of the module requiring parameters (for error messages)
        paramneed: List of parameter names that are required
        param: Dictionary containing parameters
        
    Returns:
        Boolean indicating if all required parameters were found
    """
    ret = True
    for par in paramneed:
        if par in param:
            self.gdict[par] = param.get(par)
        else:
            print(f'the param {par} need for {modulename}, nedded parameter are {paramneed}')
            ret = False
            break
    return ret

def checkparam(paramname, param):
    """
    Checks if a specific parameter exists in a dictionary.
    
    Args:
        paramname: Name of parameter to check for
        param: Dictionary to check in
        
    Returns:
        Boolean indicating if parameter exists
    """
    ret = False
    if paramname in param:
        ret = True
    return ret

def silent_execution(func):
    """
    Decorator that executes a function silently, suppressing any exceptions.
    
    Args:
        func: Function to execute silently
        
    Returns:
        Wrapper function that catches all exceptions
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            pass
    return wrapper