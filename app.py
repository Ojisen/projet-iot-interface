import os
import subprocess
from flask import Flask, send_from_directory

app = Flask(__name__)

def lancer_simulateur():
    try:
        # Popen lance upload_to_firebase.py de manière indépendante en arrière-plan
        subprocess.Popen(["python", "upload_to_firebase.py"])
        print("[OK] Script upload_to_firebase.py lancé en tâche de fond.")
    except Exception as e:
        print(f"[ERREUR] Impossible de lancer le script de données : {e}")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    lancer_simulateur()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
