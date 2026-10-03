import os
import time
import json
import threading
from flask import Flask, send_from_directory
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# ─── CONFIGURATION FIREBASE ───
DATABASE_URL = "https://firebaseio.com"
DATA_FILE = "data.json"
DELAY_SECONDES = 5

def init_firebase():
    """Initialise la connexion Firebase de manière sécurisée (Production ou Local)."""
    if not firebase_admin._apps:
        firebase_config_env = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if firebase_config_env:
            try:
                config_dict = json.loads(firebase_config_env)
                cred = credentials.Certificate(config_dict)
                firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
                print("[OK] Firebase connecté via variable d'environnement.")
                return
            except Exception as e:
                print(f"[ERREUR] Variable d'environnement corrompue : {e}")
        
        # Secours local
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
            print("[OK] Firebase connecté via fichier local.")
        else:
            print("[ERREUR] Aucune clé d'authentification Firebase trouvée.")

def boucle_simulation_capteur():
    """Simule le capteur DHT11 en tâche de fond de manière infinie."""
    init_firebase()
    
    # Attendre que le fichier data.json soit disponible
    while not os.path.exists(DATA_FILE):
        print(f"[ATTENTE] Le fichier {DATA_FILE} n'est pas encore accessible...")
        time.sleep(2)
        
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        contenu = json.load(f)
    mesures = contenu.get("mesures", [])
    
    print(f"[START] Envoi en boucle de {len(mesures)} mesures...")
    
    while True:
        for mesure in mesures:
            try:
                temp = mesure["temperature"]
                hum = mesure["humidity"]
                ts = mesure.get("timestamp", "")
                
                # Envoi temps réel
                db.reference("/").update({"temperature": temp, "humidity": hum})
                # Envoi historique
                db.reference("/historique").push({"temperature": temp, "humidity": hum, "timestamp": ts})
                
                print(f"[→ Firebase Thread] Temp: {temp}°C | Hum: {hum}%")
            except Exception as e:
                print(f"[ERREUR ENVOI] Impossible de mettre à jour Firebase : {e}")
                
            time.sleep(DELAY_SECONDES)

# ─── ROUTES FLASK ───
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Lance le thread de simulation pour qu'il s'exécute en parallèle de Flask
    sim_thread = threading.Thread(target=boucle_simulation_capteur, daemon=True)
    sim_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
