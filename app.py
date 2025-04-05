from flask import Flask, render_template, jsonify, request
import json
import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Define log file paths
LOG_DIR = "logs"
ANOMALIES_LOG_FILE = os.path.join(LOG_DIR, "anomalies.json")
NETWORK_LOG_FILE = os.path.join(LOG_DIR, "network_logs.json")

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/anomalies')
def anomalies():
    return render_template('anomalies.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/anomalies')
def get_anomalies():
    """Fetch anomalies from the anomalies log file."""
    if os.path.exists(ANOMALIES_LOG_FILE):
        with open(ANOMALIES_LOG_FILE, "r") as file:
            try:
                anomalies = json.load(file)
            except json.JSONDecodeError:
                anomalies = []
                print("Error: Invalid JSON in anomalies log file.")
    else:
        anomalies = []
        print("Warning: Anomalies log file not found.")
    return jsonify(anomalies)

@app.route('/api/logs')
def get_logs():
    """Fetch network logs from the network log file."""
    if os.path.exists(NETWORK_LOG_FILE):
        with open(NETWORK_LOG_FILE, "r") as file:
            try:
                logs = json.load(file)
            except json.JSONDecodeError:
                logs = []
                print("Error: Invalid JSON in network log file.")
    else:
        logs = []
        print("Warning: Network log file not found.")
    return jsonify(logs)

@app.route('/api/turn_off_ids', methods=['POST'])
def turn_off_ids():
    """Turn off the IDS system (requires admin credentials)."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Verify admin credentials
    if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
        try:
            # Platform-independent way to stop the IDS program
            if sys.platform == "win32":
                # Windows: Use taskkill to terminate the process
                subprocess.run(["taskkill", "/f", "/im", "python.exe"], check=True)
            else:
                # Unix-based systems: Use pkill to terminate the process
                subprocess.run(["pkill", "-f", "anomaly_detector.py"], check=True)
            return jsonify({"success": True, "message": "IDS program turned off successfully."})
        except subprocess.CalledProcessError as e:
            return jsonify({"success": False, "message": f"Failed to turn off IDS: {str(e)}"})
        except Exception as e:
            return jsonify({"success": False, "message": f"An error occurred: {str(e)}"})
    else:
        return jsonify({"success": False, "message": "Invalid username or password."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)