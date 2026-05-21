import os
import requests
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet

app = Flask(__name__)
k = Fernet.generate_key()
f = Fernet(k)

def _x(d):
    return f.encrypt(d.encode()).decode()

def _y(d):
    return f.decrypt(d.encode()).decode()

@app.route('/')
def h():
    return open('index.html').read()

@app.route('/extract', methods=['POST'])
def e():
    t = request.form.get('target')
    if not t: return "ERROR", 400
    try:
        r = requests.get(t, timeout=5)
        d = f"STATUS {r.status_code} LENGTH {len(r.text)} SERVER {r.headers.get('Server', 'UNKNOWN')}"
    except:
        d = "EXTRACTION FAILED"
    enc = _x(d)
    return _y(enc)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
