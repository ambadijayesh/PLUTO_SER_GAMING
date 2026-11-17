
from flask import Flask, request, redirect, session, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, uuid
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)

USERNAME = "plutogaming"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ambadijayesh")
PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
DATA_FILE = os.path.join(app.root_path, "files.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CATEGORIES = [
    "Gaming Clips",
    "Gaming Photos",
    "Gaming DP",
    "Gaming Wallpapers"
]

IMAGES = {"png", "jpg", "jpeg", "gif", "webp"}
VIDEOS = {"mp4", "webm", "mov", "mkv"}

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


def load_files():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_files():
    temp = DATA_FILE + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(files, f, indent=2)
    os.replace(temp, DATA_FILE)


files = load_files()


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return "Unauthorized", 403
        return func(*args, **kwargs)
    return wrapper


HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PLUTO SER GAMING</title>

<style>
*{box-sizing:border-box}

body{
background:linear-gradient(-45deg,#050505,#10102b,#200000,#050505);
background-size:400% 400%;
animation:bg 12s ease infinite;
color:white;
font-family:Arial;
text-align:center;
margin:0
}

@keyframes bg{
0%{background-position:0% 50%}
50%{background-position:100% 50%}
100%{background-position:0% 50%}
}

header{
background:#151515;
padding:25px 10px;
border-bottom:2px solid red
}

h1{
color:red;
text-shadow:0 0 10px red,0 0 25px red
}

.card,.item{
background:#191919;
margin:15px;
padding:20px;
border-radius:15px;
border:1px solid #333
}

button,a{
background:linear-gradient(135deg,#ff0000,#8b0000);
color:white;
padding:12px 18px;
border:1px solid red;
border-radius:8px;
text-decoration:none;
cursor:pointer;
font-weight:bold
}

button:hover,a:hover{
box-shadow:0 0 18px red
}

input,select{
padding:12px;
margin:8px;
border-radius:7px;
max-width:95%
}

img,video{
width:100%;
max-width:400px;
border-radius:10px
}

.admin-actions{
display:flex;
justify-content:space-between;
gap:12px;
margin-bottom:20px
}

.admin-actions button,
.admin-actions a{
width:50%;
display:block;
padding:15px 5px
}

.upload-btn{background:linear-gradient(135deg,#ff0000,#8b0000)}
.logout-btn{background:#333;border-color:#777}

.file-box{
background:#252525;
padding:15px;
border-radius:12px;
margin-top:15px
}

.delete-btn{
background:#b00000;
margin-top:12px
}

.category{
color:#ff4444;
font-weight:bold
}

footer{
padding:25px;
color:#aaa
}

/* PLUTO SER MASS LOADING THEME */
#massLoader {
 position:fixed; inset:0; z-index:99999;
 background:#050505; display:flex;
 align-items:center; justify-content:center;
 transition:opacity .7s ease, visibility .7s ease;
}
#massLoader.hide {opacity:0;visibility:hidden}
.loader-content {width:85%;max-width:350px;text-align:center}
.loader-content h1 {
 color:red;font-size:36px;letter-spacing:5px;
 text-shadow:0 0 15px red,0 0 30px red;
}
.loader-content h2 {color:white;letter-spacing:8px}
.loader-bar {
 height:7px;background:#333;border-radius:20px;
 overflow:hidden;margin-top:25px;
}
#loaderProgress {
 width:0;height:100%;background:red;
 box-shadow:0 0 15px red;
 transition:width .2s ease;
}
#loaderText {color:red;letter-spacing:3px;margin-top:15px}
body {animation:massPageIn .8s ease}
@keyframes massPageIn {
 from {opacity:0;transform:translateY(12px)}
 to {opacity:1;transform:translateY(0)}
}

</style>
</head>

<body>

<header>
<h1> PLUTO SER GAMING WEB </h1>
<a href="https://www.instagram.com/pluto_ser_her/" target="_blank">
VISIT INSTAGRAM
</a>
<p>WELCOME TO GAMING WORLD</p>
</header>

{% if logged %}

<div class="card">

<h2>👑 ADMIN PANEL</h2>

<div class="admin-actions">

<button class="upload-btn"
type="submit" form="uploadForm">
⬆ UPLOAD
</button>

<a class="logout-btn" href="/logout">
LOGOUT
</a>

</div>

<form id="uploadForm" method="POST"
action="/upload" enctype="multipart/form-data">

<h3>CHOOSE CATEGORY</h3>

<select name="category" required>
{% for c in categories %}
<option value="{{c}}">{{c}}</option>
{% endfor %}
</select>

<br>

<h3>CHOOSE FILE</h3>

<input type="file" name="file"
accept="image/*,video/*" required>

<p id="selectedFile">NO FILE SELECTED</p>

<button type="button" onclick="clearSelectedFile()">
🗑 CLEAR SELECTED FILE
</button>

<br><br>

</form>
</div>

{% else %}

<div class="card">
<h2>👑 ADMIN LOGIN</h2>

<form method="POST" action="/login">

<input name="username"
placeholder="Username" required>

<br>

<input name="password"
type="password"
placeholder="Password" required>

<br>

<button type="submit">LOGIN</button>

</form>
</div>

{% endif %}

<h2>🎮 GAMING COLLECTION</h2>

<input type="search" id="searchBox"
placeholder="🔍 Search gaming files..."
oninput="searchFiles()">

<script>
function searchFiles(){
    const q = document.getElementById("searchBox").value.toLowerCase();
    document.querySelectorAll(".item").forEach(item => {
        item.style.display = item.innerText.toLowerCase().includes(q) ? "" : "none";
    });
}
</script>

{% for f in files %}

<div class="item">

<h3 class="category">{{f.category}}</h3>

{% if f.kind == "image" %}
<img src="/uploads/{{f.name}}" loading="lazy">
{% elif f.kind == "video" %}
<video controls preload="metadata">
<source src="/uploads/{{f.name}}">
</video>
{% endif %}

<p>{{f.name}}</p>
<a href="/uploads/{{f.name}}" download="{{f.name}}">
⬇ DOWNLOAD FILE
</a>

{% if logged %}

<div class="file-box">
<form method="POST" action="/delete"
onsubmit="return confirm('Delete this uploaded file?')">

<input type="hidden" name="filename"
value="{{f.name}}">

<button type="submit" class="delete-btn">
🗑 DELETE UPLOADED FILE
</button>

</form>
</div>

{% endif %}

</div>

{% else %}
<p>NO GAMING FILES YET</p>
{% endfor %}

<footer>
🔥 PLUTO SER GAMING 🔥
</footer>

<script>
const fileInput = document.querySelector('input[name="file"]');

if(fileInput){
    fileInput.addEventListener("change", function(){
        document.getElementById("selectedFile").textContent =
        this.files.length ? this.files[0].name : "NO FILE SELECTED";
    });
}

function clearSelectedFile(){
    if(fileInput){
        fileInput.value = "";
        document.getElementById("selectedFile").textContent =
        "NO FILE SELECTED";
    }
}
</script>


<div id="massLoader">
 <div class="loader-content">
  <h1>PLUTO SER</h1>
  <h2>GAMING</h2>
  <div class="loader-bar">
   <div id="loaderProgress"></div>
  </div>
  <p id="loaderText">LOADING 0%</p>
 </div>
</div>
<script>
(function(){
 let progress=0;
 const bar=document.getElementById('loaderProgress');
 const label=document.getElementById('loaderText');
 const loader=document.getElementById('massLoader');
 const timer=setInterval(()=>{
   progress=Math.min(progress+2,90);
   bar.style.width=progress+'%';
   label.textContent='LOADING '+progress+'%';
 },40);
 function finishLoading(){
   clearInterval(timer);
   progress=100;
   bar.style.width='100%';
   label.textContent='LOADING 100%';
   setTimeout(()=>{
     loader.classList.add('hide');
     setTimeout(()=>loader.remove(),800);
   },700);
 }
 if(document.readyState === 'complete'){
   finishLoading();
 } else {
   window.addEventListener('load',finishLoading,{once:true});
 }
 setTimeout(finishLoading,5000);
 document.addEventListener('click',e=>{
   const a=e.target.closest('a');
   if(!a || a.target==='_blank' || !a.getAttribute('href')) return;
   const href=a.getAttribute('href');
   if(href.startsWith('#') || href.startsWith('javascript:')) return;
   document.body.classList.add('massPageOut');
 });
})();
</script>
<style>
@keyframes massPageOut {
 to {opacity:0;transform:translateY(-8px)}
}
body.massPageOut {animation:massPageOut .25s ease forwards}
</style>

</body>
</html>
"""


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
    if (
        request.form.get("username") == USERNAME
        and check_password_hash(
            PASSWORD_HASH,
            request.form.get("password", "")
        )
    ):
        session["admin"] = True

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/upload", methods=["POST"])
@admin_required
def upload():

    f = request.files.get("file")
    category = request.form.get("category")

    if not f or not f.filename:
        return "No file selected", 400

    if category not in CATEGORIES:
        return "Invalid category", 400

    original = secure_filename(f.filename)

    if "." not in original:
        return "Invalid file", 400

    ext = original.rsplit(".", 1)[1].lower()

    if ext in IMAGES:
        kind = "image"
    elif ext in VIDEOS:
        kind = "video"
    else:
        return "Only images and videos allowed", 400

    name = uuid.uuid4().hex + "." + ext
    f.save(os.path.join(UPLOAD_FOLDER, name))

    files.append({
        "name": name,
        "category": category,
        "kind": kind
    })

    save_files()
    return redirect("/")


@app.route("/delete", methods=["POST"])
@admin_required
def delete():

    name = request.form.get("filename", "")

    item = next(
        (x for x in files if x["name"] == name),
        None
    )

    if not item:
        return "File not found", 404

    path = os.path.join(UPLOAD_FOLDER, item["name"])

    if os.path.isfile(path):
        os.remove(path)

    files.remove(item)
    save_files()

    return redirect("/")


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.errorhandler(413)
def too_large(error):
    return "File too large. Maximum size is 100 MB.", 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

