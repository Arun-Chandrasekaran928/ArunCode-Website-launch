"""
ArunCode — Flask Backend v4
Run: python app.py  ->  http://127.0.0.1:5500
"""
import os, json
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = "aruncode-secret-key-v5-do-not-share"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

USERS_FILE  = "users.json"
EMAILS_FILE = "emails.json"
WORKSPACE   = "workspace"
DOCS_FILE   = "docs.json"
os.makedirs(WORKSPACE, exist_ok=True)

# ── Users ──────────────────────────────────────
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f: return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f, indent=2)

USERS = load_users()

CORE_ACCOUNTS = {
    "ArunC": {
        "email":    "chandrasekarana@student.rcdsb.on.ca",
        "password": generate_password_hash("927927"),
        "pin":      "283283",
        "role":     "admin"
    },
    "VijiN": {
        "email":    "nambi.vijilaxmi@gmail.com",
        "password": generate_password_hash("865864"),
        "pin":      "438438",
        "role":     "admin"
    },
    "ParthyC": {
        "email":    "partheinstein@gmail.com",
        "password": generate_password_hash("654654"),
        "pin":      "383383",
        "role":     "security"
    },
    "SujaC": {
        "email":    "you@gmail.com",
        "password": generate_password_hash("543543"),
        "pin":      "383383",
        "role":     "security"
    },
    "ChandrasekaranN": {
        "email":    "natarajchand@gmail.com",
        "password": generate_password_hash("875875"),
        "pin":      "573573",
        "role":     "security"
    },
    "News": {
        "email":    "news@aruncode.com",
        "password": generate_password_hash("927927"),
        "pin":      "283293",
        "role":     "news"
    }
}

for uname, udata in CORE_ACCOUNTS.items():
    # Always overwrite core accounts to keep passwords/roles in sync
    USERS[uname] = udata

save_users(USERS)

# ── Emails ─────────────────────────────────────
def load_emails():
    if os.path.exists(EMAILS_FILE):
        with open(EMAILS_FILE) as f: return json.load(f)
    return []

def save_emails(emails):
    with open(EMAILS_FILE, "w") as f: json.dump(emails, f, indent=2)

# ── Auth Log ───────────────────────────────────
AUTH_LOG = []

def log_event(event_type, username, detail="", ip=""):
    AUTH_LOG.append({
        "time":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type":     event_type,
        "username": username,
        "detail":   detail,
        "ip":       ip
    })
    if len(AUTH_LOG) > 200:
        AUTH_LOG.pop(0)

# ── Auth decorators ────────────────────────────
def login_required(f):
    @wraps(f)
    def d(*a, **k):
        if not session.get("logged_in"):
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        return f(*a, **k)
    return d

def admin_required(f):
    @wraps(f)
    def d(*a, **k):
        if not session.get("logged_in"):
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        if session.get("role") != "admin":
            return jsonify({"ok": False, "error": "Admin only"}), 403
        return f(*a, **k)
    return d

def security_required(f):
    @wraps(f)
    def d(*a, **k):
        if not session.get("logged_in"):
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        if session.get("role") not in ("admin", "security"):
            return jsonify({"ok": False, "error": "Security access required"}), 403
        return f(*a, **k)
    return d

# ── News auth decorator ────────────────────────
def news_required(f):
    @wraps(f)
    def d(*a, **k):
        if not session.get("logged_in"):
            return jsonify({"ok": False, "error": "Not authenticated"}), 401
        if session.get("role") not in ("admin", "news"):
            return jsonify({"ok": False, "error": "News access required"}), 403
        return f(*a, **k)
    return d

# ── Static routes ──────────────────────────────
@app.route("/")
def launcher():       return send_from_directory(app.static_folder, "launcher.html")
@app.route("/terminal")
@app.route("/terminal/")
def terminal():       return send_from_directory(app.static_folder, "index.html")
@app.route("/home")
def home():           return send_from_directory(app.static_folder, "home.html")
@app.route("/ide")
@app.route("/ide/")
def ide():            return send_from_directory("ide", "index.html")
@app.route("/emails")
@app.route("/emails/")
def emails():         return send_from_directory(app.static_folder, "emails.html")
@app.route("/ptc")
@app.route("/ptc/")
def ptc():            return send_from_directory(app.static_folder, "ptc.html")
@app.route("/admin")
@app.route("/admin/")
def admin_panel():    return send_from_directory(app.static_folder, "admin.html")
@app.route("/security")
@app.route("/security/")
def security_panel(): return send_from_directory(app.static_folder, "security.html")
@app.route("/docs")
@app.route("/docs/")
def docs():           return send_from_directory(app.static_folder, "docs.html")
@app.route("/news")
@app.route("/news/")
def news():           return send_from_directory(app.static_folder, "news.html")
@app.route("/github")
@app.route("/github/")
def github():         return send_from_directory(app.static_folder, "github.html")
@app.route("/profile")
@app.route("/profile/")
def profile():        return send_from_directory(app.static_folder, "profile.html")
@app.route("/about/about.html")
def about():          return send_from_directory(app.static_folder, "about/about.html")
@app.route("/about/versions/version.html")
def version():        return send_from_directory(app.static_folder, "about/versions/version.html")
@app.route("/about/versions/versionhistory.html")
def versionhistory(): return send_from_directory(app.static_folder, "about/versions/versionhistory.html")

# ── Auth routes ────────────────────────────────
@app.route("/api/register", methods=["POST"])
def api_register():
    d        = request.get_json(silent=True) or {}
    username = (d.get("username") or "").strip()
    email    = (d.get("email")    or "").strip().lower()
    password = (d.get("password") or "")
    ip       = request.remote_addr
    if not username or not email or not password:
        return jsonify({"ok": False, "error": "All fields required."}), 400
    if len(username) < 3:
        return jsonify({"ok": False, "error": "Username must be 3+ characters."}), 400
    if len(password) < 6:
        return jsonify({"ok": False, "error": "Password must be 6+ characters."}), 400
    if "@" not in email:
        return jsonify({"ok": False, "error": "Invalid email."}), 400
    if username in USERS:
        return jsonify({"ok": False, "error": "Username taken."}), 400
    for u in USERS.values():
        if u["email"].lower() == email:
            return jsonify({"ok": False, "error": "Email already registered."}), 400
    USERS[username] = {"email": email, "password": generate_password_hash(password), "pin": "", "role": "user"}
    save_users(USERS)
    log_event("REGISTER", username, "New account created", ip)
    return jsonify({"ok": True})

@app.route("/api/login", methods=["POST"])
def api_login():
    d        = request.get_json(silent=True) or {}
    username = (d.get("username") or "").strip()
    email    = (d.get("email")    or "").strip().lower()
    password = (d.get("password") or "")
    ip       = request.remote_addr
    matched  = next((u for u in USERS if u.lower() == username.lower()), None)
    if matched: username = matched
    user = USERS.get(username)
    if not user or user["email"].lower() != email.lower() or not check_password_hash(user["password"], password):
        log_event("LOGIN_FAIL", username, "Bad credentials", ip)
        return jsonify({"ok": False, "error": "Invalid credentials."}), 401
    session["pending_username"] = username
    needs_pin = (user["role"] in ("admin", "security") and bool(user.get("pin")))
    log_event("LOGIN_ATTEMPT", username, f"Step 1 passed, needs_pin={needs_pin}", ip)
    return jsonify({"ok": True, "needs_pin": needs_pin})

@app.route("/api/verify", methods=["POST"])
def api_verify():
    d        = request.get_json(silent=True) or {}
    code     = (d.get("code") or "").strip()
    username = session.get("pending_username")
    ip       = request.remote_addr
    if not username: return jsonify({"ok": False, "error": "Session expired."}), 400
    user = USERS.get(username)
    if not user: return jsonify({"ok": False, "error": "User not found."}), 400
    if user.get("pin") and code != user["pin"]:
        log_event("PIN_FAIL", username, "Wrong PIN", ip)
        return jsonify({"ok": False, "error": "Incorrect PIN."}), 401
    session["logged_in"] = True
    session["username"]  = username
    session["role"]      = user["role"]
    session.pop("pending_username", None)
    log_event("LOGIN_OK", username, f"Logged in as {user['role']}", ip)
    return jsonify({"ok": True, "username": username, "role": user["role"]})

@app.route("/api/complete_login", methods=["POST"])
def api_complete_login():
    username = session.get("pending_username")
    ip       = request.remote_addr
    if not username: return jsonify({"ok": False, "error": "Session expired."}), 400
    user = USERS.get(username)
    if not user or user["role"] in ("admin", "security"):
        return jsonify({"ok": False, "error": "Unauthorized."}), 403
    session["logged_in"] = True
    session["username"]  = username
    session["role"]      = user["role"]  # preserves "news", "user" etc
    session.pop("pending_username", None)
    log_event("LOGIN_OK", username, "Logged in as user", ip)
    return jsonify({"ok": True, "username": username, "role": "user"})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    log_event("LOGOUT", session.get("username", "unknown"))
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
@login_required
def api_me():
    return jsonify({"ok": True, "username": session["username"], "role": session.get("role", "user")})

# ── Admin: users ───────────────────────────────
@app.route("/api/admin/users")
@security_required
def api_admin_users():
    safe = {u: {"email": d["email"], "role": d["role"]} for u, d in USERS.items()}
    return jsonify({"ok": True, "users": safe})

@app.route("/api/admin/users/<username>", methods=["DELETE"])
@security_required
def api_admin_delete_user(username):
    caller_role = session.get("role")
    if username == "ArunC":
        return jsonify({"ok": False, "error": "Cannot delete primary admin."}), 403
    if username not in USERS:
        return jsonify({"ok": False, "error": "User not found."}), 404
    target_role = USERS[username]["role"]
    if caller_role == "security" and target_role in ("admin", "security"):
        return jsonify({"ok": False, "error": "Security manager cannot delete admin accounts."}), 403
    del USERS[username]
    save_users(USERS)
    log_event("DELETE_USER", session.get("username"), f"Deleted {username}")
    return jsonify({"ok": True})

# ── Security: logs ─────────────────────────────
@app.route("/api/security/logs")
@security_required
def api_security_logs():
    return jsonify({"ok": True, "logs": list(reversed(AUTH_LOG))})

@app.route("/api/security/stats")
@security_required
def api_security_stats():
    total    = len(USERS)
    admins   = sum(1 for u in USERS.values() if u["role"] == "admin")
    security = sum(1 for u in USERS.values() if u["role"] == "security")
    regular  = sum(1 for u in USERS.values() if u["role"] == "user")
    failed   = sum(1 for l in AUTH_LOG if l["type"] in ("LOGIN_FAIL", "PIN_FAIL"))
    return jsonify({"ok": True, "stats": {
        "total_users": total, "admins": admins,
        "security": security, "regular": regular,
        "failed_logins": failed, "log_entries": len(AUTH_LOG)
    }})

# ── Emails ─────────────────────────────────────
@app.route("/api/emails", methods=["GET"])
@login_required
def api_emails_get():
    me         = session["username"]
    emails_all = load_emails()
    user_email = USERS.get(me, {}).get("email", "").lower()
    inbox = [e for e in emails_all if e.get("to_user","").lower() == me.lower()
             or e.get("to_addr","").lower() == user_email]
    sent  = [e for e in emails_all if e.get("from_user","").lower() == me.lower()]
    return jsonify({"ok": True, "inbox": inbox, "sent": sent})

@app.route("/api/emails", methods=["POST"])
@login_required
def api_emails_send():
    d       = request.get_json(silent=True) or {}
    to_raw  = (d.get("to")      or "").strip()
    subject = (d.get("subject") or "").strip()
    body    = (d.get("body")    or "").strip()
    me      = session["username"]
    if not to_raw or not subject:
        return jsonify({"ok": False, "error": "To and Subject are required."}), 400
    to_user = ""; to_addr = to_raw
    for uname, udata in USERS.items():
        if uname.lower() == to_raw.lower() or udata["email"].lower() == to_raw.lower():
            to_user = uname; to_addr = udata["email"]; break
    emails_all = load_emails()
    email = {
        "id":        len(emails_all) + 1,
        "from_user": me,
        "from_addr": USERS.get(me, {}).get("email", ""),
        "to_user":   to_user, "to_addr": to_addr,
        "subject":   subject, "body": body,
        "date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
        "read": False, "starred": False,
    }
    emails_all.append(email)
    save_emails(emails_all)
    return jsonify({"ok": True, "email": email})

@app.route("/api/emails/<int:email_id>/read", methods=["POST"])
@login_required
def api_email_mark_read(email_id):
    emails_all = load_emails()
    for e in emails_all:
        if e["id"] == email_id: e["read"] = True; break
    save_emails(emails_all)
    return jsonify({"ok": True})

@app.route("/api/emails/<int:email_id>/star", methods=["POST"])
@login_required
def api_email_star(email_id):
    emails_all = load_emails()
    for e in emails_all:
        if e["id"] == email_id: e["starred"] = not e.get("starred", False); break
    save_emails(emails_all)
    return jsonify({"ok": True})

@app.route("/api/emails/<int:email_id>", methods=["DELETE"])
@login_required
def api_email_delete(email_id):
    save_emails([e for e in load_emails() if e["id"] != email_id])
    return jsonify({"ok": True})

# ── Docs ───────────────────────────────────────
@app.route("/api/docs", methods=["GET"])
@login_required
def api_docs_get():
    if os.path.exists(DOCS_FILE):
        with open(DOCS_FILE) as f: return jsonify({"ok": True, "docs": json.load(f)})
    return jsonify({"ok": True, "docs": []})

@app.route("/api/docs", methods=["POST"])
@admin_required
def api_docs_save():
    d    = request.get_json(silent=True) or {}
    docs = d.get("docs", [])
    with open(DOCS_FILE, "w") as f: json.dump(docs, f, indent=2)
    return jsonify({"ok": True})

# ── News API ───────────────────────────────────
NEWS_FILE = "news.json"

def load_news():
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE) as f: return json.load(f)
    return []

def save_news(posts):
    with open(NEWS_FILE, "w") as f: json.dump(posts, f, indent=2)

@app.route("/api/news", methods=["GET"])
@login_required
def api_news_get():
    return jsonify({"ok": True, "posts": load_news()})

@app.route("/api/news", methods=["POST"])
@news_required
def api_news_post():
    d     = request.get_json(silent=True) or {}
    title = (d.get("title") or "").strip()
    body  = (d.get("body")  or "").strip()
    tag   = (d.get("tag")   or "general").strip()
    if not title or not body:
        return jsonify({"ok": False, "error": "Title and body required."}), 400
    posts = load_news()
    post  = {
        "id":     len(posts) + 1,
        "title":  title, "body": body, "tag": tag,
        "author": session["username"],
        "date":   datetime.now().strftime("%Y-%m-%d %H:%M"),
        "pinned": False
    }
    posts.insert(0, post)
    save_news(posts)
    return jsonify({"ok": True, "post": post})

@app.route("/api/news/<int:post_id>", methods=["PUT"])
@news_required
def api_news_edit(post_id):
    d     = request.get_json(silent=True) or {}
    posts = load_news()
    for p in posts:
        if p["id"] == post_id:
            p["title"]  = (d.get("title") or p["title"]).strip()
            p["body"]   = (d.get("body")  or p["body"]).strip()
            p["tag"]    = (d.get("tag")   or p["tag"])
            p["edited"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    save_news(posts)
    return jsonify({"ok": True})

@app.route("/api/news/<int:post_id>", methods=["DELETE"])
@news_required
def api_news_delete(post_id):
    save_news([p for p in load_news() if p["id"] != post_id])
    return jsonify({"ok": True})

@app.route("/api/news/<int:post_id>/pin", methods=["POST"])
@news_required
def api_news_pin(post_id):
    posts = load_news()
    for p in posts:
        if p["id"] == post_id:
            p["pinned"] = not p.get("pinned", False)
            break
    save_news(posts)
    return jsonify({"ok": True})

# ── Profile ────────────────────────────────────
@app.route("/api/profile")
@login_required
def api_profile_get():
    me   = session["username"]
    user = USERS.get(me, {})
    return jsonify({"ok": True, "username": me, "email": user.get("email",""), "role": user.get("role","user"), "avatar": user.get("avatar","")})

@app.route("/api/profile/avatar", methods=["POST"])
@login_required
def api_profile_avatar():
    me   = session["username"]
    d    = request.get_json(silent=True) or {}
    av   = d.get("avatar", "").strip()
    if not av:
        return jsonify({"ok": False, "error": "No avatar provided."}), 400
    # If image upload, limit size
    if av.startswith("data:") and len(av) > 2*1024*1024:
        return jsonify({"ok": False, "error": "Image too large."}), 400
    USERS[me]["avatar"] = av
    save_users(USERS)
    return jsonify({"ok": True})

@app.route("/api/profile/username", methods=["POST"])
@login_required
def api_profile_username():
    me       = session["username"]
    d        = request.get_json(silent=True) or {}
    new_name = (d.get("username") or "").strip()
    if len(new_name) < 3:
        return jsonify({"ok": False, "error": "Username must be 3+ characters."}), 400
    if new_name in USERS and new_name != me:
        return jsonify({"ok": False, "error": "Username already taken."}), 400
    # Move user data to new key
    USERS[new_name] = USERS.pop(me)
    save_users(USERS)
    session["username"] = new_name
    return jsonify({"ok": True})

@app.route("/api/profile/email", methods=["POST"])
@login_required
def api_profile_email():
    me    = session["username"]
    d     = request.get_json(silent=True) or {}
    email = (d.get("email") or "").strip().lower()
    if "@" not in email:
        return jsonify({"ok": False, "error": "Invalid email."}), 400
    for uname, udata in USERS.items():
        if uname != me and udata["email"].lower() == email:
            return jsonify({"ok": False, "error": "Email already in use."}), 400
    USERS[me]["email"] = email
    save_users(USERS)
    return jsonify({"ok": True})

@app.route("/api/profile/password", methods=["POST"])
@login_required
def api_profile_password():
    me  = session["username"]
    d   = request.get_json(silent=True) or {}
    cur = d.get("current", "")
    nw  = d.get("newpass", "")
    if not check_password_hash(USERS[me]["password"], cur):
        return jsonify({"ok": False, "error": "Current password is incorrect."}), 401
    if len(nw) < 6:
        return jsonify({"ok": False, "error": "New password must be 6+ characters."}), 400
    USERS[me]["password"] = generate_password_hash(nw)
    save_users(USERS)
    return jsonify({"ok": True})

@app.route("/api/profile/pin", methods=["POST"])
@login_required
def api_profile_pin():
    me   = session["username"]
    role = session.get("role","user")
    if role not in ("admin","security"):
        return jsonify({"ok": False, "error": "Only privileged accounts can set a PIN."}), 403
    d   = request.get_json(silent=True) or {}
    pin = (d.get("pin") or "").strip()
    if len(pin) != 6 or not pin.isdigit():
        return jsonify({"ok": False, "error": "PIN must be exactly 6 digits."}), 400
    USERS[me]["pin"] = pin
    save_users(USERS)
    return jsonify({"ok": True})

# ── Github ─────────────────────────────────────
GITHUB_FILE = "github.json"

def load_repos():
    if os.path.exists(GITHUB_FILE):
        with open(GITHUB_FILE) as f: return json.load(f)
    return []

def save_repos(repos):
    with open(GITHUB_FILE, "w") as f: json.dump(repos, f, indent=2)

@app.route("/api/github/repos", methods=["GET"])
@login_required
def api_github_repos():
    me    = session["username"]
    repos = load_repos()
    # Return public repos + caller's own repos
    visible = [r for r in repos if r.get("visibility")=="public" or r.get("owner")==me]
    return jsonify({"ok": True, "repos": visible})

@app.route("/api/github/repos", methods=["POST"])
@login_required
def api_github_create_repo():
    d    = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip().replace(" ","-")
    desc = (d.get("desc") or "").strip()
    lang = (d.get("lang") or "Other").strip()
    vis  = (d.get("visibility") or "public")
    me   = session["username"]
    if not name:
        return jsonify({"ok": False, "error": "Name required."}), 400
    repos = load_repos()
    for r in repos:
        if r["owner"] == me and r["name"].lower() == name.lower():
            return jsonify({"ok": False, "error": "Repo name already exists."}), 400
    repo = {
        "id":         f"{me}-{name}-{int(datetime.now().timestamp())}",
        "owner":      me,
        "name":       name,
        "desc":       desc,
        "lang":       lang,
        "visibility": vis,
        "created":    datetime.now().strftime("%Y-%m-%d"),
        "files":      []
    }
    repos.append(repo)
    save_repos(repos)
    return jsonify({"ok": True, "repo": repo})

@app.route("/api/github/repos/<repo_id>", methods=["DELETE"])
@login_required
def api_github_delete_repo(repo_id):
    me    = session["username"]
    repos = load_repos()
    repo  = next((r for r in repos if r["id"]==repo_id), None)
    if not repo:
        return jsonify({"ok": False, "error": "Not found."}), 404
    if repo["owner"] != me and session.get("role") != "admin":
        return jsonify({"ok": False, "error": "Not your repo."}), 403
    save_repos([r for r in repos if r["id"]!=repo_id])
    return jsonify({"ok": True})

@app.route("/api/github/repos/<repo_id>/files", methods=["POST"])
@login_required
def api_github_upload_file(repo_id):
    me    = session["username"]
    repos = load_repos()
    repo  = next((r for r in repos if r["id"]==repo_id), None)
    if not repo:
        return jsonify({"ok": False, "error": "Repo not found."}), 404
    if repo["owner"] != me:
        return jsonify({"ok": False, "error": "Not your repo."}), 403
    d       = request.get_json(silent=True) or {}
    fname   = (d.get("name") or "").strip()
    content = d.get("content", "")
    size    = d.get("size", len(content.encode()))
    if not fname:
        return jsonify({"ok": False, "error": "Filename required."}), 400
    # Replace existing file with same name
    repo["files"] = [f for f in repo.get("files",[]) if f["name"]!=fname]
    repo["files"].append({"name": fname, "content": content, "size": size})
    save_repos(repos)
    return jsonify({"ok": True})

@app.route("/api/github/repos/<repo_id>/files/<path:filename>", methods=["GET"])
@login_required
def api_github_get_file(repo_id, filename):
    me    = session["username"]
    repos = load_repos()
    repo  = next((r for r in repos if r["id"]==repo_id), None)
    if not repo:
        return jsonify({"ok": False, "error": "Repo not found."}), 404
    if repo.get("visibility")!="public" and repo["owner"]!=me:
        return jsonify({"ok": False, "error": "Private repo."}), 403
    f = next((f for f in repo.get("files",[]) if f["name"]==filename), None)
    if not f:
        return jsonify({"ok": False, "error": "File not found."}), 404
    content = f.get("content","")
    return jsonify({"ok": True, "content": content, "size": f.get("size",0), "lines": content.count("\n")+1})

@app.route("/api/github/repos/<repo_id>/files/<path:filename>", methods=["DELETE"])
@login_required
def api_github_delete_file(repo_id, filename):
    me    = session["username"]
    repos = load_repos()
    repo  = next((r for r in repos if r["id"]==repo_id), None)
    if not repo or repo["owner"]!=me:
        return jsonify({"ok": False, "error": "Not authorized."}), 403
    repo["files"] = [f for f in repo.get("files",[]) if f["name"]!=filename]
    save_repos(repos)
    return jsonify({"ok": True})

@app.route("/api/github/users", methods=["GET"])
@login_required
def api_github_users():
    safe = [{"username": u, "role": d.get("role","user"), "avatar": d.get("avatar","")}
            for u, d in USERS.items()]
    return jsonify({"ok": True, "users": safe})

# ── Files (IDE) ────────────────────────────────
def safe_path(filename):
    name = os.path.basename(filename.replace("/", os.sep).replace("..", ""))
    return os.path.join(WORKSPACE, name)

@app.route("/api/files", methods=["GET"])
@login_required
def api_files_list():
    items = []
    for entry in sorted(os.scandir(WORKSPACE), key=lambda e: (not e.is_dir(), e.name)):
        items.append({"name": entry.name, "type": "folder" if entry.is_dir() else "file",
                      "size": entry.stat().st_size if entry.is_file() else 0})
    return jsonify({"ok": True, "files": items})

@app.route("/api/files/<path:filename>", methods=["GET"])
@login_required
def api_file_read(filename):
    path = safe_path(filename)
    if not os.path.isfile(path): return jsonify({"ok": False, "error": "File not found."}), 404
    with open(path, "r", errors="replace") as f: content = f.read()
    return jsonify({"ok": True, "content": content})

@app.route("/api/files/<path:filename>", methods=["POST"])
@login_required
def api_file_save(filename):
    path = safe_path(filename)
    d    = request.get_json(silent=True) or {}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f: f.write(d.get("content", ""))
    return jsonify({"ok": True})

@app.route("/api/files/<path:filename>", methods=["DELETE"])
@login_required
def api_file_delete(filename):
    path = safe_path(filename)
    if not os.path.exists(path): return jsonify({"ok": False, "error": "Not found."}), 404
    if os.path.isdir(path):
        import shutil; shutil.rmtree(path)
    else:
        os.remove(path)
    return jsonify({"ok": True})

@app.route("/api/folders", methods=["POST"])
@login_required
def api_folder_create():
    d    = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name: return jsonify({"ok": False, "error": "Folder name required."}), 400
    os.makedirs(os.path.join(WORKSPACE, os.path.basename(name)), exist_ok=True)
    return jsonify({"ok": True})

if __name__ == "__main__":
    print("\n  ArunCode backend starting...")
    print("  Open -> http://127.0.0.1:5500\n")
    app.run(host="127.0.0.1", port=5500, debug=True)