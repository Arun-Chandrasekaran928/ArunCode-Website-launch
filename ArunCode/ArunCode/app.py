"""
ArunCode_Term - Flask Backend
Run with: python app.py
"""
import os, json
from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.urandom(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

USERS = load_users()

if "ArunC" not in USERS:
    USERS["ArunC"] = {
        "email":    "chandrasekarana@student.rcdsb.on.ca",
        "password": generate_password_hash("927927"),
        "pin":      "283283",
        "role":     "admin"
    }
    save_users(USERS)
if "VijiN" not in USERS:
    USERS["VijiN"] = {
        "email":    "nambi.vijilaxmi@gmail.com",
        "password": generate_password_hash("865864"),
        "pin":      "438438",
        "role":     "admin"
    }
    save_users(USERS)

if "ParthyC" not in USERS:
    USERS["ParthyC"] = {
        "email":    "partheinstein@gmail.com",
        "password": generate_password_hash("654654"),
        "pin":      "383383s",
        "role":     "admin"
    }
    save_users(USERS)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        if session.get("role") != "admin":
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def launcher():
    return send_from_directory(app.static_folder, "launcher.html")

@app.route("/terminal")
@app.route("/terminal/")
def terminal():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/home")
def home():
    return send_from_directory(app.static_folder, "home.html")

@app.route("/ide")
@app.route("/ide/")
def ide():
    return send_from_directory("ide", "index.html")

@app.route("/about/about.html")
def about():
    return send_from_directory(app.static_folder, "about/about.html")

@app.route("/about/versions/version.html")
def version():
    return send_from_directory(app.static_folder, "about/versions/version.html")

@app.route("/about/versions/versionhistory.html")
def versionhistory():
    return send_from_directory(app.static_folder, "about/versions/versionhistory.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    data     = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "")
    if not username or not email or not password:
        return jsonify({"ok": False, "error": "All fields are required."}), 400
    if len(username) < 3:
        return jsonify({"ok": False, "error": "Username must be at least 3 characters."}), 400
    if len(password) < 6:
        return jsonify({"ok": False, "error": "Password must be at least 6 characters."}), 400
    if "@" not in email:
        return jsonify({"ok": False, "error": "Invalid email address."}), 400
    if username in USERS:
        return jsonify({"ok": False, "error": "Username already taken."}), 400
    for u in USERS.values():
        if u["email"].lower() == email:
            return jsonify({"ok": False, "error": "Email already registered."}), 400
    USERS[username] = {
        "email":    email,
        "password": generate_password_hash(password),
        "pin":      "",
        "role":     "user"
    }
    save_users(USERS)
    return jsonify({"ok": True})

@app.route("/api/login", methods=["POST"])
def api_login():
    data     = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "")
    user = USERS.get(username)
    if not user or user["email"].lower() != email or not check_password_hash(user["password"], password):
        return jsonify({"ok": False, "error": "Invalid credentials."}), 401
    session["pending_username"] = username
    needs_pin = (user["role"] == "admin" and bool(user.get("pin")))
    return jsonify({"ok": True, "needs_pin": needs_pin})

@app.route("/api/verify", methods=["POST"])
def api_verify():
    data     = request.get_json(silent=True) or {}
    code     = (data.get("code") or "").strip()
    username = session.get("pending_username")
    if not username:
        return jsonify({"ok": False, "error": "Session expired."}), 400
    user = USERS.get(username)
    if not user:
        return jsonify({"ok": False, "error": "User not found."}), 400
    if user["role"] == "admin" and user.get("pin"):
        if code != user["pin"]:
            return jsonify({"ok": False, "error": "Incorrect PIN."}), 401
    session["logged_in"] = True
    session["username"]  = username
    session["role"]      = user["role"]
    session.pop("pending_username", None)
    return jsonify({"ok": True, "username": username, "role": user["role"]})

@app.route("/api/complete_login", methods=["POST"])
def api_complete_login():
    username = session.get("pending_username")
    if not username:
        return jsonify({"ok": False, "error": "Session expired."}), 400
    user = USERS.get(username)
    if not user or user["role"] == "admin":
        return jsonify({"ok": False, "error": "Unauthorized."}), 403
    session["logged_in"] = True
    session["username"]  = username
    session["role"]      = "user"
    session.pop("pending_username", None)
    return jsonify({"ok": True, "username": username, "role": "user"})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
@login_required
def api_me():
    return jsonify({"ok": True, "username": session["username"], "role": session.get("role", "user")})

@app.route("/api/admin/users")
@admin_required
def api_admin_users():
    safe = {u: {"email": d["email"], "role": d["role"]} for u, d in USERS.items()}
    return jsonify({"ok": True, "users": safe})

@app.route("/api/admin/users/<username>", methods=["DELETE"])
@admin_required
def api_admin_delete_user(username):
    if username == "ArunC":
        return jsonify({"ok": False, "error": "Cannot delete admin."}), 403
    if username not in USERS:
        return jsonify({"ok": False, "error": "User not found."}), 404
    del USERS[username]
    save_users(USERS)
    return jsonify({"ok": True})

if __name__ == "__main__":
    print("\n  ArunCode_Term backend starting...")
    print("  Open -> http://127.0.0.1:5500\n")
    app.run(host="127.0.0.1", port=5500, debug=True)