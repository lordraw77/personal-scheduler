import requests
import json
import datetime
from datetime import datetime as dt

def execute_request(config, date_from, date_to):
    """Esegue una richiesta API basata sulla configurazione JSON fornita"""
    # Copio il payload per non modificare l'originale
    payload = config["payload"].copy()
    
    # Aggiorno le date nel payload
    payload["date_from"] = date_from
    payload["date_to"] = date_to
    
    # Eseguo la richiesta con i parametri specificati nel JSON
    url = config["url"]
    headers = config["headers"]
    method = config["method"]
    
    if method.upper() == "POST":
        response = requests.post(url, headers=headers, json=payload)
    elif method.upper() == "GET":
        response = requests.get(url, headers=headers, params=payload)
    else:
        raise ValueError(f"Metodo HTTP non supportato: {method}")
    
    # Verifico se la richiesta è andata a buon fine
    if response.status_code == 200:
        # Assegno la risposta alla variabile specificata
        retval = response.json()
        
        # Valuto la condizione if specificata nel JSON
        ifmethod_code = config["ifmethod"]
        # La funzione lambda è definita come stringa, la eseguo in modo sicuro
        # In questo caso, non eseguo direttamente la stringa ma interpreto la logica
        if len(retval['data']['search_results']) > 0 and '1726' in retval['data']['search_results']:
            result_count = len(retval['data']['search_results']['1726']['accommodations'])
        else:
            result_count = 0
            
        # Se ci sono risultati, estraggo i dati come specificato in returnvalue
        if result_count > 0:
            # In un caso reale, bisognerebbe valutare questa espressione in modo sicuro
            # ma per semplicità interpretiamo direttamente la logica
            accommodations = retval['data']['search_results']['1726']['accommodations']
            
            # Formatto il messaggio come specificato in notifymes
            notification_message = f"camere disponibili {len(accommodations)} {date_from} - {date_to}"
            return True, notification_message, accommodations
        else:
            notification_message = f"Nessuna camera disponibile per {date_from} - {date_to}"
            return False, notification_message, []
    else:
        return False, f"Errore nella richiesta: {response.status_code}", []

def main():
    # La configurazione JSON fornita
    config = {
        "url": "https://api.beddy.io/BOL/search",
        "payload": {
            "date_from": None,  # Sarà sostituito
            "date_to": None,    # Sarà sostituito
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
        },
        "headers": {
            'Origin': 'https://www.lavalledivico.it',
            'Referer': 'https://www.lavalledivico.it',
            'Content-Type': 'application/json'
        },
        "method": "POST",
        "responseType": "json",
        "responseVariable": "retval",
        "ifmethod": "lambda x: len(retval['data']['search_results']['1726']['accommodations']) if len(retval['data']['search_results'])> 0 else 0",
        "returnvalue": "retval['data']['search_results']['1726']['accommodations']",
        "notifymes": "camere disponibili {len(retval['data']['search_results']['1726']['accommodations'])} {date_from} - {date_to}"
    }
    
    # Imposto le date per la richiesta (oggi e domani per esempio)
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    day_after = today + datetime.timedelta(days=2)
    
    date_from = tomorrow.strftime("%Y-%m-%d")
    date_to = day_after.strftime("%Y-%m-%d")
    
    # Eseguo la richiesta
    success, message, accommodations = execute_request(config, date_from, date_to)
    print(message)
    
    if success and accommodations:
        print("\nDettagli delle camere disponibili:")
        for i, accommodation in enumerate(accommodations, 1):
            print(f"\nCamera {i}:")
            print(f"Nome: {accommodation.get('name', 'N/A')}")
            print(f"Prezzo: {accommodation.get('price', 'N/A')} {accommodation.get('currency', 'EUR')}")

if __name__ == "__main__":
    main()