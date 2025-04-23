import util.common as common
import inspect
import requests

gdict={}

def setgdict(self,gdict):
     self.gdict=gdict

myself = lambda: inspect.stack()[1][3]


def sendtelegramnotify(self,param):
    """
    Assume the bot name is my_bot.

    1- Make /start on your bot

    2- Send a dummy message to the bot.
    You can use this example: /my_id @my_bot
    
    3- Go to following url: https://api.telegram.org/botXXX:YYYY/getUpdates
    replace XXX:YYYY with your bot token
    Or join https://t.me/RawDataBot /start 

    4- Look for "chat":{"id":zzzzzzzzzz, zzzzzzzzzz is your chat id 
    
    - name: send telegram message
      task-notify.sendtelegramnotify:
        tokenid: "XXX:YYYY"
        chatid: 
           - "zzzzzzzzzz"
        message: "prova {zzz} test"
        printresponse: True #optional

    """
    common.logstart(myself())
    if common.checkandloadparam(self,myself(),('tokenid','chatid','message'),param):
        tokenid=gdict['tokenid']
        chatid=gdict['chatid']
        message=common.effify(gdict['message'],gdict)
        for cid in chatid:
            send_text = 'https://api.telegram.org/' + tokenid + '/sendMessage?chat_id=' + cid + '&parse_mode=Markdown&text=' + message

        response = requests.get(send_text)
        if common.checkparam('printresponse',param):
            if param['printresponse']:
                print(response.json())

        
        common.logend(myself())
    else:
        exit()
        