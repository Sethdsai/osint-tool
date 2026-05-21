import json
from flask import Flask, request, jsonify, render_template_string
from backends import (
    search_username,
    lookup_email,
    lookup_domain,
    lookup_ip,
    lookup_phone,
    extract_url,
)

app = Flask(__name__)

HTML_PAGE = open("index.html", "r").read()

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/username", methods=["POST"])
def api_username():
    username = request.form.get("username", "").strip()
    if not username:
        return jsonify({"error": "Username required"}), 400
    result = search_username(username)
    return jsonify(result)

@app.route("/api/email", methods=["POST"])
def api_email():
    email = request.form.get("email", "").strip()
    if not email:
        return jsonify({"error": "Email required"}), 400
    result = lookup_email(email)
    return jsonify(result)

@app.route("/api/domain", methods=["POST"])
def api_domain():
    domain = request.form.get("domain", "").strip()
    if not domain:
        return jsonify({"error": "Domain required"}), 400
    result = lookup_domain(domain)
    return jsonify(result)

@app.route("/api/ip", methods=["POST"])
def api_ip():
    ip = request.form.get("ip", "").strip()
    if not ip:
        return jsonify({"error": "IP required"}), 400
    result = lookup_ip(ip)
    return jsonify(result)

@app.route("/api/phone", methods=["POST"])
def api_phone():
    phone = request.form.get("phone", "").strip()
    if not phone:
        return jsonify({"error": "Phone required"}), 400
    result = lookup_phone(phone)
    return jsonify(result)

@app.route("/api/extract", methods=["POST"])
def api_extract():
    target = request.form.get("target", "").strip()
    if not target:
        return jsonify({"error": "URL required"}), 400
    result = extract_url(target)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
