"""
DMS-Routen für web_server.py
============================
Diese Routen in web_server.py einbinden:

    from dms_routes import register_dms_routes
    register_dms_routes(app)
"""

import os
import json
from pathlib import Path
from flask import jsonify, request, send_file, render_template, abort
from werkzeug.utils import secure_filename

IMPORT_DIR = os.path.abspath("data/dms/import")
ARCHIV_DIR = os.path.abspath("data/dms/archiv")

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "doc", "xlsx", "xls", "xlsm",
    "txt", "csv", "md", "rtf",
    "jpg", "jpeg", "png", "webp", "tiff", "tif",
    "bmp", "heic", "heif",
    "odt", "ods", "odp", "pptx", "ppt",
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def register_dms_routes(app):

    @app.route("/dms")
    def dms_index():
        return render_template("dms.html")

    @app.route("/api/dms/stats")
    def dms_stats_api():
        try:
            from skills.dms import dms_stats
            return jsonify(dms_stats())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/dms/tree")
    def dms_tree_api():
        try:
            from skills.dms import dms_archiv_baum
            return jsonify(dms_archiv_baum())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/dms/import-list")
    def dms_import_list():
        """Dateien im Import-Ordner auflisten."""
        os.makedirs(IMPORT_DIR, exist_ok=True)
        try:
            dateien = [
                {
                    "name":    f,
                    "groesse": os.path.getsize(os.path.join(IMPORT_DIR, f)),
                    "ext":     Path(f).suffix.lower().lstrip("."),
                }
                for f in os.listdir(IMPORT_DIR)
                if os.path.isfile(os.path.join(IMPORT_DIR, f))
                and allowed_file(f)
            ]
            return jsonify(sorted(dateien, key=lambda x: x["name"]))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/dms/upload", methods=["POST"])
    def dms_upload():
        """Dateien in den Import-Ordner hochladen."""
        os.makedirs(IMPORT_DIR, exist_ok=True)

        if "files" not in request.files:
            return jsonify({"error": "Keine Dateien empfangen"}), 400

        hochgeladen = []
        fehler      = []

        for file in request.files.getlist("files"):
            if file.filename == "":
                continue
            if not allowed_file(file.filename):
                fehler.append(f"{file.filename}: Format nicht unterstützt")
                continue
            try:
                filename = secure_filename(file.filename)
                # Duplikate im Import-Ordner umbenennen
                ziel = os.path.join(IMPORT_DIR, filename)
                if os.path.exists(ziel):
                    stem = Path(filename).stem
                    ext  = Path(filename).suffix
                    i    = 1
                    while os.path.exists(ziel):
                        ziel = os.path.join(IMPORT_DIR, f"{stem}_{i}{ext}")
                        i   += 1
                file.save(ziel)
                hochgeladen.append(os.path.basename(ziel))
            except Exception as e:
                fehler.append(f"{file.filename}: {str(e)}")

        return jsonify({
            "hochgeladen": hochgeladen,
            "fehler":      fehler,
            "anzahl":      len(hochgeladen),
        })

    @app.route("/api/dms/sort", methods=["POST"])
    def dms_sort():
        """Alle Import-Dateien per KI einsortieren."""
        try:
            from skills.dms import dms_einsortieren
            from providers import select_provider
            _, provider = select_provider("auto")
            ergebnis = dms_einsortieren(provider=provider)
            return jsonify({"ergebnis": ergebnis})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/dms/search")
    def dms_search():
        """Archiv nach Suchbegriff durchsuchen."""
        q = request.args.get("q", "").strip()
        if not q:
            return jsonify([])
        try:
            treffer = []
            q_lower = q.lower()
            for root, _, files in os.walk(ARCHIV_DIR):
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), ARCHIV_DIR).replace("\\", "/")
                    if q_lower in rel.lower():
                        voll = os.path.join(root, f)
                        treffer.append({
                            "pfad":    rel,
                            "name":    f,
                            "groesse": os.path.getsize(voll),
                            "datum":   str(Path(voll).stat().st_mtime),
                            "ext":     Path(f).suffix.lower().lstrip("."),
                        })
            return jsonify(sorted(treffer, key=lambda x: x["pfad"])[:100])
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/dms/download")
    def dms_download():
        """Archivierte Datei herunterladen."""
        pfad = request.args.get("pfad", "")
        if not pfad:
            abort(400)
        # Sicherheitscheck
        voll = os.path.abspath(os.path.join(ARCHIV_DIR, pfad))
        if not voll.startswith(os.path.abspath(ARCHIV_DIR)):
            abort(403)
        if not os.path.isfile(voll):
            abort(404)
        return send_file(voll, as_attachment=True)

    @app.route("/api/dms/delete", methods=["DELETE"])
    def dms_delete():
        """Datei aus dem Import-Ordner löschen."""
        data = request.get_json() or {}
        name = secure_filename(data.get("name", ""))
        if not name:
            return jsonify({"error": "Kein Dateiname"}), 400
        pfad = os.path.join(IMPORT_DIR, name)
        if not os.path.isfile(pfad):
            return jsonify({"error": "Datei nicht gefunden"}), 404
        os.remove(pfad)
        return jsonify({"ok": True})
