import json
import requests
paramd= {}
# paramd["date_from"] ="2026-08-08"
# paramd["date_to"]="2026-08-22" 
paramd["date_from"] ="2025-04-23"
paramd["date_to"]="2025-04-24" 
config = {
    "url": "https://api.beddy.io/BOL/search",
    "payload": {
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
        },
    "headers": {
        'Origin': 'https://www.lavalledivico.it',
        'Referer': 'https://www.lavalledivico.it',
        'Content-Type': 'application/json'
        },
    "method": "POST",
    "responseType":"json",
    "responseVariable":"retval",
    "ifmethod":"lambda x: len(retval['data']['search_results']['1726']['accommodations']) if len(retval['data']['search_results'])> 0 else 0",
    "returnvalue": "retval['data']['search_results']['1726']['accommodations']"
    }

print(config)

def execute_api_request(config, paramd):
    # Estrai i parametri dalla configurazione
    url = config["url"]
    method = config["method"]
    headers = config["headers"]
    
    # Prepara il payload sostituendo i parametri date_from e date_to
    payload = config["payload"].copy()
    payload["date_from"] = paramd["date_from"]
    payload["date_to"] = paramd["date_to"]
    
    # Esegui la richiesta HTTP
    if method == "POST":
        response = requests.post(url, json=payload, headers=headers)
    elif method == "GET":
        response = requests.get(url, params=payload, headers=headers)
    else:
        raise ValueError(f"Metodo HTTP non supportato: {method}")
    
    # Verifica se la richiesta è andata a buon fine
    response.raise_for_status()
    
    # Converti la risposta in JSON
    retval = response.json()
    
    # Valuta la condizione ifmethod in modo sicuro
    if_result = 0
    try:
        # Estrai la logica dalla stringa, senza la parte "lambda x:"
        if_code = config["ifmethod"].split("lambda x:", 1)[1].strip()
        
        # Valuta la condizione nel contesto corrente dove retval è definito
        if_result = eval(if_code)
        print(f"Risultato della condizione ifmethod: {if_result}")
    except Exception as e:
        print(f"Errore durante la valutazione della condizione: {e}")
    
    # Estrai e restituisci il valore specificato in returnvalue
    if if_result > 0:
        try:
            # Valuta returnvalue nel contesto corrente dove retval è definito
            return eval(config["returnvalue"])
        except Exception as e:
            print(f"Errore durante l'estrazione del risultato: {e}")
            return []
    else:
        return []


if __name__ == "__main__":

    try:
        result = execute_api_request(config, paramd)
        print(f"Numero di alloggi trovati: {len(result)}")
        print("Dettagli degli alloggi:")
        for i, accommodation in enumerate(result, 1):
            print(f"\nAlloggio #{i}:")
            # Mostra alcune informazioni chiave per ogni alloggio
            if isinstance(accommodation, dict):
                print(f"Nome: {accommodation.get('name', 'N/A')}")
                print(f"Prezzo: {accommodation.get('price', 'N/A')} {config['payload']['currency']}")
                print(f"Disponibilità: {accommodation.get('availability', 'N/A')}")
    except Exception as e:
        print(f"Errore durante l'esecuzione della richiesta: {e}")