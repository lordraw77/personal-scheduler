import requests
import json
import logging
def checkvico(paramd,logger):
    url = "https://api.beddy.io/BOL/search"
    # date_from = "2026-08-08"
    # date_to = "2026-08-22"

    date_from =  paramd["date_from"] 
    date_to = paramd["date_to"]
    
    pl =  {
    "date_from":  paramd["date_from"] ,
    "date_to": paramd["date_to"] ,
    "rooms": [
        {
        "num_adults": 2,
        "children": []
        }
    ],
    "lang": "it",
    "currency": "EUR",
    "booking_widget_code": "8553bdc120521",
    "coupon_code": None,
    "unlock_key": [],
    "searchOrigin": "mask"
    }
    
    payload = json.dumps(pl)
    headers = {
    'Origin': 'https://www.lavalledivico.it',
    'Referer': 'https://www.lavalledivico.it',
    'Content-Type': 'application/json'
    }
    logger.info(f"checkvico {date_from} {date_to} {payload}")
    response = requests.request("POST", url, headers=headers, data=payload)

    #print(response.text)
    
    aDict = json.loads(response.text)
    out = ""
   
    if len(aDict['data']['search_results'])> 0:
        acc = aDict['data']['search_results']['1726']['accommodations']
        lacc = len(acc)
        # pre = json.dumps(acc,indent=4)
        # print(pre)
        # print(aDict)
        out =  f"camere disponibili {lacc}  {date_from} - {date_to}"
    
    else:
        out = f"nessuna stanza disponibile per  {date_from} - {date_to}"
    
    print(out)
    return out
    #sendtelegram(out)
