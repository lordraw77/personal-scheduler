import requests
import json
from string import Formatter

# Funzione per formattare la stringa di notifica con valori dinamici
def format_message(template, **kwargs):
    class SafeFormatter(Formatter):
        def get_value(self, key, args, kwargs):
            try:
                return super().get_value(key, args, kwargs)
            except (KeyError, IndexError):
                return '{' + key + '}'
    formatter = SafeFormatter()
    return formatter.format(template, **kwargs)

# Funzione principale
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
    except Exception as e:
        print(f"Errore durante la valutazione della condizione: {e}")
    
    # Crea un nuovo oggetto JSON per la risposta
    result_json = {
        "original_response": retval,
        "accommodations": [],
        "available_rooms": if_result,
        "date_from": paramd["date_from"],
        "date_to": paramd["date_to"]
    }
    
    # Estrai gli alloggi se disponibili
    if if_result > 0:
        try:
            accommodations = eval(config["returnvalue"])
            result_json["accommodations"] = accommodations
        except Exception as e:
            print(f"Errore durante l'estrazione degli alloggi: {e}")
    
    # Formatta il messaggio di notifica personalizzato se presente nella config
    if "notifymes" in config:
        try:
            # Prepara i parametri per la formattazione
            format_params = {
                **paramd,
                "date_from": paramd["date_from"],
                "date_to": paramd["date_to"],
                "len": len  # Passare la funzione len per poterla usare nel template
            }
            
            # Formatta il messaggio di notifica
            notification_message = format_message(config["notifymes"], **locals(), **format_params)
            result_json["notification_message"] = notification_message
        except Exception as e:
            print(f"Errore durante la formattazione del messaggio di notifica: {e}")
            result_json["notification_message"] = "Errore nella formattazione del messaggio"
    
    return result_json

# Esempio di utilizzo
if __name__ == "__main__":
    # Carica la configurazione
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
    
    # Parametri di esempio per le date
    paramd = {
        "date_from": "2025-05-01",
        "date_to": "2025-05-05"
    }
    
    try:
        result_json = execute_api_request(config, paramd)
        
        # Stampa il messaggio di notifica
        if "notification_message" in result_json:
            print(result_json["notification_message"])
        
        print(f"Stanze disponibili: {result_json['available_rooms']}")
        
        if result_json["accommodations"]:
            print(f"\nTrovati {len(result_json['accommodations'])} alloggi:")
            for i, accommodation in enumerate(result_json["accommodations"], 1):
                print(f"\nAlloggio #{i}:")
                if isinstance(accommodation, dict):
                    print(f"Nome: {accommodation.get('name', 'N/A')}")
                    print(f"Prezzo: {accommodation.get('price', 'N/A')} {config['payload']['currency']}")
        
        # Salva il risultato in un file JSON
        with open("availability_result.json", "w", encoding="utf-8") as f:
            json.dump(result_json, f, ensure_ascii=False, indent=2)
        print("\nRisultato salvato nel file 'availability_result.json'")
        
    except Exception as e:
        print(f"Errore durante l'esecuzione della richiesta: {e}")