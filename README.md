# 🌦️ Climate Monitor — DHT11 + Firebase + Render

A complete end-to-end IoT software stack designed to simulate a **DHT11** temperature and humidity sensor, pipe data continuously into a cloud-hosted **Firebase Realtime Database**, and render it dynamically on a web dashboard accessible globally.

This project features a decoupled, async multi-process wrapper engineered specifically for zero-config production deployments on **Render**.

---

## 🏗️ Project Architecture

```text
projet-iot-interface/
├── app.py                  # Core Flask server (handles routing and background process spawning)
├── upload_to_firebase.py   # Autonomous worker thread pushing simulated metrics to Firebase
├── index.html              # Live real-time dashboard UI
├── style.css               # User interface look and feel styling
├── data.json               # Seed metrics dataset representing real/simulated DHT11 ticks
├── requirements.txt        # Managed Python environment packaging definitions for Render
└── .gitignore              # Access control map preventing credential leaks to version control
```

---

## 🚀 Features

- **Continuous Hardware Simulation**: Reads historical sensor metrics sequentially from a static JSON file and streams updates into Firebase indefinitely at a configurable 5-second cadence.
- **Dynamic Updates**: Uses full duplex client-side WebSocket streams via Firebase SDK to refresh UI metric tiles seamlessly without reloading the browser.
- **Interactive Graphing**: Includes responsive charting engines plotting real-time rolling metrics across the latest 20 telemetry ticks.
- **Production-Grade Secrets Masking**: Utilizes a secure payload proxy decoding server-side administrative access tokens from isolated runtime environment values.

---

## 🛠️ Local Configuration and Setup

### 1. Environmental Prerequisites
Ensure **Python 3.8+** is installed on your local host architecture.

### 2. Dependency Packaging
Provision the local runtime environment from the manifest layout using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Firebase Authentication Handshake
1. Authenticate with your administrative profile inside the **Firebase Console**.
2. Navigate to your project parameters and generate a new private structural key under the **Service Accounts** tab.
3. Move the downloaded payload directly to the project root directory and change its name exactly to: `serviceAccountKey_firebase.json`.
4. *Important: Double-check that this file filename remains within your local `.gitignore` map before making any commits.*

### 4. Running the Project Local Host
Execute the primary web management wrapper script:
```bash
python app.py
```
Open your standard web browser and direct your viewport to `http://localhost:10000` or `http://127.0.0.1:5500`.

---

## 🌐 Cloud Production Deployment on Render

This software suite is pre-configured to run as a unified Python **Web Service** on Render.

### 1. Runtime Pipeline Bindings
Under the **Settings** tab within your Render dashboard service profile, supply these operational variables:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

### 2. Safeguarding Your Infrastructure Credentials
To ensure absolute isolation of administrative credentials from public repository trees, configure a secured environment variable injection:

1. Copy the raw plain-text payload of your local `serviceAccountKey_firebase.json` file.
2. Direct your browser to an isolated hashing wrapper engine such as **[base64encode.org](https://base64encode.org)**, supply the raw JSON string, and convert it to a **Base64** string.
3. Access your Render service console profile and navigate to the **Environment** parameters tab.
4. Declare a new configuration entry bound explicitly to the parameters listed below:
   - **Key**: `FIREBASE_SERVICE_ACCOUNT`
   - **Value**: *(Paste the continuous cryptographic Base64 string generated from the step above)*
5. Confirm and apply the changes. The platform will automatically trigger a clean system reboot, parse the encrypted binary memory map into temporary variables, and cleanly lock a socket connection to your remote database endpoint.

---

## 🔒 Recommended Firebase Access Rules

To ensure unrestricted dashboard reads while completely locking down write access to unauthorized clients, paste this configuration tree into the **Rules** tab of your cloud-hosted Firebase Realtime Database dashboard:

```json
{
  "rules": {
    ".read": true,
    ".write": "auth != null"
  }
}
```
