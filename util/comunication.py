import requests
import json
import logging
logger = logging.getLogger()


def checkAllowSendTelegram(CONFIG):
    try:
        CSENDTELEGRAM=CONFIG.CANSENDTELEGRAM
    except:
        CSENDTELEGRAM=False
    return bool(CSENDTELEGRAM)

def sendtelegram(CONFIG,text):
    print("1")
    if checkAllowSendTelegram(CONFIG) == True:
        print("2")
        try:
            PS_BOTKEY = CONFIG.BOTKEY
        except KeyError:
            logger.error("PS_BOTKEY not found in environment variables.")
            return
        try:
            PS_CHATID = CONFIG.CHATID
        except KeyError:
            logger.error("PS_CHATID not found in environment variables.")
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
        logger.info(text1)
