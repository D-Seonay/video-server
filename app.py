import os
import subprocess
import platform
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "static/videos"
ALLOWED_EXTENSIONS = {"mp4"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

current_video = None

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    files = os.listdir(UPLOAD_FOLDER)
    files = [f for f in files if f.endswith(".mp4")]
    return render_template("index.html", files=files, current_video=current_video)

@app.route("/upload", methods=["POST"])
def upload_file():
    global current_video
    if "file" not in request.files:
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        change_video(filepath)

    return redirect(url_for("index"))

@app.route("/play/<filename>")
def play_video(filename):
    global current_video
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    change_video(filepath)
    return redirect(url_for("index"))

@app.route("/play_youtube", methods=["POST"])
def play_youtube():
    global current_video
    video_url = request.form.get("youtube_url")

    if video_url:
        change_video(video_url)

    return redirect(url_for("index"))

@app.route("/delete/<filename>")
def delete_video(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for("index"))

@app.route("/current_video")
def get_current_video():
    return jsonify({"current_video": current_video})

def change_video(source):
    """Lance une vidéo locale ou une vidéo YouTube."""
    global current_video
    subprocess.run(["pkill", "mpv"])  # Arrêter la vidéo précédente

    # Détection YouTube (URL contenant 'youtube' ou 'youtu.be')
    if "youtube.com" in source or "youtu.be" in source:
        command = ["mpv", "--loop=inf", source]
    else:  # Vidéo locale
        command = ["mpv", "--loop=inf", os.path.abspath(source)]

    subprocess.Popen(command)
    current_video = source  # Mettre à jour la vidéo en cours

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
