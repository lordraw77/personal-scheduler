from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor
from datetime import datetime, time


def load_env_parameter(envparma, env : dict,config: dict):
    config[envparma] = "na"
    try:
        config[envparma] = env[envparma]
    except:
        pass    
    return  config.copy()

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

def effify(non_f_str: str):
    if "{" in non_f_str:
        return eval(f'f"""{non_f_str}"""')
    else:
        return non_f_str
    
def check_parma_and_load(ddict,nomeparam):
    retval =""
    try:
        retval = ddict[nomeparam]
    except:
        retval = None
    return retval