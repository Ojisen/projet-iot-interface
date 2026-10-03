"""
=============================================================
STRUCTURE Firebase créée :
  /
  ├── temperature : 37
  ├── humidity    : 15
  └── historique/
        ├── -NxABC... : { temperature, humidity, timestamp }
        └── ...
=============================================================
"""

import json
import time
import os
import firebase_admin
from firebase_admin import credentials, db

# ─────────────────────────────────────────────
# 1. CONFIGURATION — 
# ─────────────────────────────────────────────

# Chemin vers le fichier serviceAccountKey.json (uniquement pour le local)
SERVICE_ACCOUNT_KEY = "serviceAccountKey_firebase.json"


# URL de Realtime Database
DATABASE_URL = "https://projet-iot-a9c26-default-rtdb.firebaseio.com/"

# Fichier JSON contenant les mesures DHT11
DATA_FILE = "data.json"

# Délai (secondes) entre chaque envoi de mesure
DELAY_SECONDES = 5

# ─────────────────────────────────────────────
# 2. INITIALISATION FIREBASE
# ─────────────────────────────────────────────

import base64  # <--- Assurez-vous d'avoir cet import tout en haut du fichier avec les autres

def init_firebase():
    """Initialise la connexion Firebase de manière sécurisée (Production ou Local)."""
    firebase_config_env = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    
    if firebase_config_env:
        try:
            # 1. On tente de lire le Base64 de manière sécurisée
            try:
                # Décodage de la chaîne Base64 reçue de Render
                decoded_bytes = base64.b64decode(firebase_config_env.encode('utf-8'))
                decoded_str = decoded_bytes.decode('utf-8')
                config_dict = json.loads(decoded_str)
            except Exception:
                # Si ce n'est pas du Base64, on tente une lecture JSON directe (secours)
                config_dict = json.loads(firebase_config_env)
            
            # Réparation de sécurité au cas où des \n traînent encore
            if "private_key" in config_dict and "\\n" in config_dict["private_key"]:
                config_dict["private_key"] = config_dict["private_key"].replace("\\n", "\n")
                
            cred = credentials.Certificate(config_dict)
            firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
            print("[OK] Connecté à Firebase en production via Variable Base64 décodée.")
            return
        except Exception as e:
            print(f"[ERREUR] Échec du chargement de la variable d'environnement : {e}")
            exit(1)

    # 2. Secours en local
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"[ERREUR] Fichier '{SERVICE_ACCOUNT_KEY}' introuvable.")
        exit(1)

    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
    print("[OK] Connecté à Firebase en local via le fichier JSON.")

# ─────────────────────────────────────────────
# 3. LECTURE DU FICHIER JSON
# ─────────────────────────────────────────────

def lire_json(fichier):
    """Charge et retourne les mesures du fichier JSON."""
    if not os.path.exists(fichier):
        print(f"[ERREUR] Fichier '{fichier}' introuvable.")
        exit(1)

    with open(fichier, "r", encoding="utf-8") as f:
        contenu = json.load(f)

    mesures = contenu.get("mesures", [])
    print(f"[OK] {len(mesures)} mesures chargées depuis '{fichier}'")
    return mesures

# ─────────────────────────────────────────────
# 4. ENVOI VERS FIREBASE
# ─────────────────────────────────────────────

def envoyer_mesure(mesure):
    """
    Envoie une mesure vers Firebase :
      - Met à jour /temperature et /humidity (valeurs en temps réel)
      - Ajoute une entrée dans /historique/ (historique complet)
    """
    temperature = mesure["temperature"]
    humidity    = mesure["humidity"]
    timestamp   = mesure.get("timestamp", "")

    # Mise à jour des valeurs actuelles (lues par l'interface web)
    db.reference("/").update({
        "temperature": temperature,
        "humidity":    humidity
    })

    # Ajout dans l'historique (push génère une clé unique automatique)
    db.reference("/historique").push({
        "temperature": temperature,
        "humidity":    humidity,
        "timestamp":   timestamp
    })

    print(f"  [→ Firebase] Temp: {temperature}°C | Humidité: {humidity}%  ({timestamp})")

# ─────────────────────────────────────────────
# 5. BOUCLE PRINCIPALE
# ─────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  DHT11 → JSON → Firebase — Envoi automatique")
    print("=" * 55)

    init_firebase()
    mesures = lire_json(DATA_FILE)

    print(f"\n[START] Envoi en boucle infinie de {len(mesures)} mesures (intervalle : {DELAY_SECONDES}s)\n")

    # La boucle principale doit tourner indéfiniment
    while True:
        for i, mesure in enumerate(mesures, 1):
            print(f"[{i}/{len(mesures)}]", end=" ")
            envoyer_mesure(mesure)

            # Pause obligatoire entre chaque envoi
            time.sleep(DELAY_SECONDES)
        
        print("\n[REBOUT] Fin de la liste de données. Redémarrage du cycle de simulation...\n")

# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
