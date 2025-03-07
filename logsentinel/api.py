
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(filename='/app/logs/security_events.log', level=logging.INFO)

@app.route('/log_event', methods=['POST'])
def log_event():
    event = request.json
    logging.info(str(event))
    return jsonify({"status": "logged"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
