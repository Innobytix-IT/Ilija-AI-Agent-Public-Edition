"""
web_server.py – Web-Interface für Ilija Public Edition
Starten: python web_server.py
Browser: http://localhost:5000
"""

import os
import json
import threading
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from kernel import Kernel

load_dotenv()

app    = Flask(__name__)
CORS(app)

# Globaler Kernel (Thread-safe via Lock)
kernel      = None
kernel_lock = threading.Lock()


def get_kernel() -> Kernel:
    global kernel
    if kernel is None:
        kernel = Kernel()
    return kernel


# ── DMS-Routen einbinden ──────────────────────────────────────
from dms_routes import register_dms_routes
register_dms_routes(app)


# ── Haupt-Chat-Interface ──────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data  = request.get_json() or {}
    msg   = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "Leere Nachricht"}), 400
    with kernel_lock:
        k        = get_kernel()
        response = k.chat(msg)
    return jsonify({"response": response, "provider": k.state.active_provider})


@app.route("/api/status")
def status():
    with kernel_lock:
        k = get_kernel()
        return jsonify(k.state.get_status_dict())


# Alias /api/stats → gleiche Daten (wird von externen Clients abgefragt)
@app.route("/api/stats")
def stats_alias():
    with kernel_lock:
        k = get_kernel()
        d = k.state.get_status_dict()
    # DMS-Stats ergänzen falls verfügbar
    try:
        from skills.dms import dms_stats
        d["dms"] = dms_stats()
    except Exception:
        pass
    return jsonify(d)


@app.route("/api/reload", methods=["POST"])
def reload_skills():
    with kernel_lock:
        k   = get_kernel()
        msg = k.reload_skills()
    return jsonify({"message": msg})


@app.route("/api/clear", methods=["POST"])
def clear_history():
    with kernel_lock:
        k = get_kernel()
        k.state.clear_history()
    return jsonify({"message": "Chat-Verlauf gelöscht"})


@app.route("/api/switch", methods=["POST"])
def switch_provider():
    data = request.get_json() or {}
    mode = data.get("provider", "auto")
    with kernel_lock:
        k   = get_kernel()
        msg = k.switch_provider(mode)
    return jsonify({"message": msg, "provider": k.state.active_provider})


@app.route("/api/providers")
def providers():
    from providers import get_available_providers
    return jsonify(get_available_providers())


@app.route("/api/skills")
def skills():
    with kernel_lock:
        k = get_kernel()
        return jsonify(k.manager.list_skills())


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Datei-Upload für Chat (Bilder, Dokumente)."""
    if "file" not in request.files:
        return jsonify({"error": "Keine Datei"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Kein Dateiname"}), 400

    upload_dir = os.path.join("data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    from werkzeug.utils import secure_filename
    filename  = secure_filename(file.filename)
    filepath  = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Direkt in DMS-Import kopieren?
    auto_dms = request.form.get("auto_dms", "false").lower() == "true"
    if auto_dms:
        import shutil
        dms_import = os.path.join("data", "dms", "import")
        os.makedirs(dms_import, exist_ok=True)
        shutil.copy(filepath, os.path.join(dms_import, filename))
        return jsonify({"message": f"{filename} in DMS-Import gespeichert", "filename": filename})

    return jsonify({"message": f"{filename} hochgeladen", "filename": filename, "path": filepath})


if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    import socket
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "127.0.0.1"

    print(f"\n{'='*50}")
    print(f"  Ilija Public Edition – Web Interface")
    print(f"  Lokal:    http://localhost:{port}")
    print(f"  Netzwerk: http://{ip}:{port}")
    print(f"  DMS:      http://localhost:{port}/dms")
    print(f"{'='*50}\n")

    app.run(host="0.0.0.0", port=port, debug=debug, threaded=True)
