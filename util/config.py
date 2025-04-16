import yaml
import os
from pyaml_env import parse_config



class Config:
    
    def d(self,dec):
        from cryptography.fernet import Fernet
        s = 912149642944558232130003047997343013285860479538
        ss = b'8phYq9o8FyJSX4AD9OhvcqEsQIL33_wb-xfhl-TQckc='
        f = Fernet(ss)
        e= f.decrypt(dec)
        return  e.decode("utf-8")
    ## general param
    _logfilepath="logfilepath"
    _logbackupsize="logbackupsize"
    _loglevel="loglevel"
    _sendtelegram="sendtelegram"
    _botkey="botkey"
    _chatid="chatid"
    LOGFILEPATH=""
    LOGBACKUPSIZE=""
    LOGLEVEL="" 
    SENDTELEGRAM=""
    BOTKEY=""
    CHATID=""
    
    def _getparam(self,pramname):
        try:
            if self.conf[pramname]:
                return self.conf[pramname]
            else:
                print(f"error missing parameter: {pramname}")
                raise Exception(f"error missing parameter: {pramname}")
        except:
            print(f"error missing parameter: {pramname}")
            raise Exception(f"error missing parameter: {pramname}")
        
    def __init__(self, filename):   
        from dotenv import dotenv_values

        configfile = filename
        conf = {}
        self.conf = parse_config(configfile)        
        if len(self.conf) > 0:
            self.LOGFILEPATH = self._getparam(self._logfilepath)
            self.LOGBACKUPSIZE = self._getparam(self._logbackupsize)
            self.LOGLEVEL = self._getparam(self._loglevel)
            self.SENDTELEGRAM = self._getparam(self._sendtelegram)
            self.BOTKEY = self._getparam(self._botkey)
            self.CHATID = self._getparam(self._chatid)
            #self.env_variables = dotenv_values(".env")
            #self.conf.update(dotenv_values(".env"))
            #print(self.env_variables)
            print(self.conf) 
