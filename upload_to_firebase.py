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

# Chemin vers  fichier serviceAccountKey.json
SERVICE_ACCOUNT_KEY = "serviceAccountKey.json"

# URL de Realtime Database
DATABASE_URL = "https://projet-iot-a9c26-default-rtdb.firebaseio.com/"

# Fichier JSON contenant les mesures DHT11
DATA_FILE = "data.json"

# Délai (secondes) entre chaque envoi de mesure
DELAY_SECONDES = 5

# ─────────────────────────────────────────────
# 2. INITIALISATION FIREBASE
# ─────────────────────────────────────────────

def init_firebase():
    """Initialise la connexion Firebase avec le compte de service."""
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"[ERREUR] Fichier '{SERVICE_ACCOUNT_KEY}' introuvable.")
        print("  → Téléchargez-le depuis Firebase Console :")
        print("     Paramètres du projet > Comptes de service > Générer une nouvelle clé privée")
        exit(1)

    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
    print("[OK] Connecté à Firebase :", DATABASE_URL)

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

    print(f"\n[START] Envoi en boucle de {len(mesures)} mesures "
          f"(intervalle : {DELAY_SECONDES}s)\n")

    # La boucle infinie doit englober l'envoi des mesures
    while True:
        for i, mesure in enumerate(mesures, 1):
            print(f"[{i}/{len(mesures)}]", end=" ")
            envoyer_mesure(mesure)

            # Pause entre chaque mesure
            time.sleep(DELAY_SECONDES)
        
        print("\n[REBOUT] Fin de la liste, redémarrage de la boucle...\n")

if __name__ == "__main__":
    main()