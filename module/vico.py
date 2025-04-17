import requests
import json
def checkvico(paramd):
    url = "https://api.beddy.io/BOL/search"
    # date_from = "2026-08-08"
    # date_to = "2026-08-22"

    # date_from = "2024-08-01"
    # date_to = "2024-08-17"
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
        out =  f"camere disponibili {lacc}  {paramd["date_from"]} - {paramd["date_to"]}"
    
    else:
        out = f"nessuna stanza disponibile per  {paramd["date_from"]} - {paramd["date_to"]}"
    
    print(out)
    return out
    #sendtelegram(out)
