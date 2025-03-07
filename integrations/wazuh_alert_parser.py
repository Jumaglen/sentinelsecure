
from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

LOKI_URL = "http://loki:3100/loki/api/v1/push"

@app.route('/wazuh-alert', methods=['POST'])
def wazuh_alert():
    alert = request.json
    log_entry = {
        "streams": [
            {"labels": '{source="wazuh"}', "entries": [{"ts": alert.get("timestamp", ""), "line": json.dumps(alert)}]}
        ]
    }
    requests.post(LOKI_URL, json=log_entry)
    return jsonify({"status": "forwarded"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
