from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor
from datetime import datetime, time
import requests
import json

def load_env_parameter(envparma, env : dict,CONFIG: dict):
    CONFIG[envparma] = "na"
    try:
        CONFIG[envparma] = env[envparma]
    except:
        pass    
    return  CONFIG.copy()

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
def checkAllowSendTelegram(CONFIG):
    try:
        DUCKDNS_SENDTELEGRAM=CONFIG.SENDTELEGRAM
    except:
        DUCKDNS_SENDTELEGRAM=False
    return bool(DUCKDNS_SENDTELEGRAM)

def sendtelegram(CONFIG,text):
    print("1")
    if checkAllowSendTelegram(CONFIG) == True:
        print("2")
        try:
            PS_BOTKEY = CONFIG.BOTKEY
        except KeyError:
            print("PS_BOTKEY not found in environment variables.")
            return
        try:
            PS_CHATID = CONFIG.CHATID
        except KeyError:
            print("PS_CHATID not found in environment variables.")
            return

        body =  {}
        botkey = PS_BOTKEY
        chat = PS_CHATID
        
        url = f"https://api.telegram.org/{botkey}/sendMessage"

        headers = {
                'Content-Type': 'application/json'
            }

        body["chat_id"]=chat
        body["text"]=f"{text}"
        response = requests.request("POST", url, headers=headers, data=json.dumps(body))
        text1 = response.text
        print(text1)

def check_parma_and_load(ddict,nomeparam):
    retval =""
    try:
        retval = ddict[nomeparam]
    except:
        retval = None
    return retval

def check_for_notify(notify):
    return False