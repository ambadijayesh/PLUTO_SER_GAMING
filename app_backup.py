from flask import Flask, request, redirect, session, render_template_string
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

USERNAME = "plutogaming"
PASSWORD_HASH = generate_password_hash(
    os.environ.get("ADMIN_PASSWORD", "ambadijayesh")
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CATEGORIES = ["Gaming Clips", "Gaming Photos", "Gaming DP", "Gaming Wallpapers"]

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>PLUTO SER GAMING</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#080808;color:white;font-family:Arial;text-align:center;margin:0}
header{background:#151515;padding:25px;border-bottom:2px solid red}
h1{
color:red;
animation: glow 2s infinite alternate;
}

@keyframes glow{
from{
text-shadow:0 0 5px red;
}
to{
text-shadow:0 0 25px red, 0 0 40px red;
}
}
.card{background:#191919;margin:15px;padding:20px;border-radius:15px}

 a,button{background:linear-gradient(135deg,#ff0000,#8b0000);color:white;padding:12px 22px;border:1px solid #ff3333;border-radius:8px;text-decoration:none;cursor:pointer;transition:all .3s ease;box-shadow:0 0 8px #ff0000}button:hover,a:hover{transform:scale(1.07);box-shadow:0 0 22px #ff0000;background:linear-gradient(135deg,#ff3333,#cc0000)}button:active{transform:scale(.94)}
input,select{padding:12px;margin:8px;border-radius:7px;max-width:90%}
img,video{width:100%;max-width:350px;border-radius:10px}
.item{background:#202020;margin:15px;padding:15px;border-radius:12px}
body{position:relative;isolation:isolate;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:radial-gradient(circle,#ff3030 1.5px,transparent 2px),radial-gradient(circle,#ff0000 1px,transparent 2px),radial-gradient(circle,#ff7777 1px,transparent 2px);background-size:110px 110px,170px 170px,230px 230px;background-position:0 0,50px 80px,100px 30px;animation:neonParticles 12s linear infinite}
@keyframes neonParticles{0%{background-position:0 0,50px 80px,100px 30px}100%{background-position:0 110px,50px 250px,100px 260px}}
body {
    background: linear-gradient(-45deg, #050505, #10102b, #200000, #050505);
    background-size: 400% 400%;
    animation: gamingBG 12s ease infinite;
}

@keyframes gamingBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
</head>
<body>
<header>
<h1>PLUTO SER GAMING WEB</h1>
<a href="https://www.instagram.com/pluto_ser_her/" target="_blank">
VISIT INSTAGRAM
</a>
<p>WELCOME TO GAMING WORLD</p>
</header>

{% if not logged %}
<div class="card">
<h2>👑 ADMIN PANEL</h2>

<div style="display:flex;justify-content:space-between;gap:10px;">
<a href="/logout">LOGOUT</a>
<button type="submit" form="uploadForm">UPLOAD</button>
</div>

<form method="POST" action="/delete" style="text-align:center;">
<input type="hidden" name="filename" value="{{f.name}}">
<button type="submit">DELETE</button>
</form>

<form method="POST" action="/delete" style="text-align:center;">
<button type="submit">DELETE</button>
</form>
</div>
{% endfor %}
</body>
</html>
"""

files = []

@app.route("/")
def home():
    return render_template_string(
        HTML,
        logged=session.get("admin", False),
        categories=CATEGORIES,
        files=files
    )

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("username") == USERNAME and check_password_hash(
        PASSWORD_HASH, request.form.get("password", "")
    ):
        session["admin"] = True
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/upload", methods=["POST"])
def upload():
    if not session.get("admin"):
        return "Unauthorized", 403

    f = request.files.get("file")
    category = request.form.get("category")

    if not f or not f.filename or category not in CATEGORIES:
        return "Invalid upload", 400

    name = secure_filename(f.filename)
    if not name:
        return "Invalid filename", 400

    path = os.path.join(UPLOAD_FOLDER, name)
    if os.path.exists(path):
        return "File already exists", 400

    f.save(path)
    kind = "video" if f.mimetype.startswith("video/") else "image"

    if not (f.mimetype.startswith("video/") or f.mimetype.startswith("image/")):
        os.remove(path)
        return "Only images and videos allowed", 400

    files.append({"name": name, "category": category, "kind": kind})
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    if not session.get("admin"):
        return "Unauthorized", 403

    name = request.form.get("filename")
    for item in files:
        if item["name"] == name:
            path = os.path.join(UPLOAD_FOLDER, name)
            if os.path.exists(path):
                os.remove(path)
            files.remove(item)
            break
    return redirect("/")

@app.route("/uploads/<path:name>")
def uploaded(name):
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
