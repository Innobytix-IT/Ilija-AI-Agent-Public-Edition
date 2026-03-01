# 🤖 Ilija – Public Edition (LINUX)
(English version below)

> Persönlicher KI-Assistent für Dokumentenverwaltung, Kommunikation und Organisation.

---

## ✨ Features

- **🗂 DMS** – KI-gestütztes Dokumentenmanagementsystem mit Web-GUI
- **🧠 Langzeitgedächtnis** – ChromaDB, dauerhaft auch nach Neustart
- **💬 WhatsApp** – überwacht Chats, vereinbart Termine, nimmt Nachrichten an
- **📱 Telegram** – vollständige Fernsteuerung, Dokumente per App senden
- **🔍 Internet-Recherche** – DuckDuckGo, Wikipedia, Webseiten lesen
- **🌐 Web-Interface** – Browser-Chat mit Datei-Upload & DMS-Integration
- **🤖 Multi-Provider** – Claude → GPT → Gemini → Ollama (automatisch)

---

## 🚀 Schnellstart

📋 System vorbereiten (einmalig)
Bevor du startest, stelle sicher, dass dein System die nötigen Werkzeuge besitzt:

```bash
sudo apt update && sudo apt install -y git curl python3-pip python3-venv wget
```

```bash
git clone https://github.com/Innobytix-IT/Ilija-AI-Agent-Public-Edition.git
cd Ilija-AI-Agent-Public-Edition
chmod +x install.sh
./install.sh
```

### Manuell

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env öffnen und mindestens einen API-Key eintragen
python web_server.py
```

---

## ▶️ Starten

```bash
source venv/bin/activate
```

| Interface | Befehl | URL |
|-----------|--------|-----|
| Web-Interface | `python web_server.py` | http://localhost:5000 |
| DMS | `python web_server.py` | http://localhost:5000/dms |
| Telegram-Bot | `python telegram_bot.py` | Telegram-App |
| Beide gleichzeitig | `python telegram_bot.py & python web_server.py` | – |
| Terminal | `python kernel.py` | Konsole |

---

## 🗂 DMS – Dokumentenverwaltung

Unterstützte Formate: PDF · DOCX · XLSX · PPTX · JPG · PNG · TXT · CSV · MD · und mehr

Die KI analysiert jeden Dateiinhalt und archiviert automatisch nach:
```
data/dms/archiv/Kategorie/Unterkategorie/Jahr/Dateiname.pdf
```

**Duplikat-Erkennung** via SHA-256 · **Automatische Versionierung** (_v2, _v3)

Dokumente hinzufügen:
- Drag & Drop in die Web-GUI
- Per Telegram als Datei oder Foto senden
- Manuell in `data/dms/import/` kopieren

---

## 🔧 Provider konfigurieren

| Provider | Variable | Modell |
|----------|----------|--------|
| Claude | `ANTHROPIC_API_KEY` | claude-opus-4-6 |
| ChatGPT | `OPENAI_API_KEY` | gpt-4o |
| Gemini | `GOOGLE_API_KEY` | gemini-2.5-flash |
| Ollama | — | qwen2.5:7b |

---

## 📱 Telegram-Bot

1. @BotFather → `/newbot` → Token kopieren → in `.env` eintragen
2. User-ID über @userinfobot → `TELEGRAM_ALLOWED_USERS=` in `.env`
3. `python telegram_bot.py`

**Telegram-DMS-Befehle:**
- `/dms_import` – Import-Ordner anzeigen
- `/dms_sort` – Dokumente einsortieren
- `/dms_stats` – Archiv-Statistiken
- Datei/Foto senden → automatisch in DMS-Import

---

## 📁 Projektstruktur

```
ilija-public/
├── install.sh              # Installationsskript (empfohlen)
├── install_EN.sh           # Installation (English)
├── web_server.py           # Flask Web-Interface
├── telegram_bot.py         # Telegram-Bot
├── kernel.py               # Zentraler Agent + Terminal
├── providers.py            # KI-Provider-Management
├── skill_manager.py        # Skill-Verwaltung
├── agent_state.py          # Zustandsverwaltung
├── model_registry.py       # Modell-Konfiguration
├── dms_routes.py           # DMS Flask-Routen
├── skills/
│   ├── dms.py              # DMS-Skill (KI-Archivierung)
│   ├── gedaechtnis.py      # Langzeitgedächtnis (ChromaDB)
│   ├── basis_tools.py      # Datum, Notizen, Rechner
│   ├── webseiten_inhalt_lesen.py  # Internet-Recherche
│   └── whatsapp_autonomer_dialog.py
├── templates/
│   ├── index.html          # Web-Chat-Interface
│   └── dms.html            # DMS Web-GUI
├── data/
│   └── dms/
│       ├── import/         # Neue Dokumente hier ablegen
│       └── archiv/         # Archivierte Dokumente
├── memory/                 # ChromaDB (lokal, nicht committet)
├── .env.example
├── requirements.txt
└── models_config.json
```

---

## 📋 Anforderungen

- Python 3.10+
- Ubuntu / Debian Linux (oder macOS kommt später)
- Google Chrome (für WhatsApp-Skill)
- Mindestens ein API-Key **oder** lokales Ollama-Modell

---

## 🔗 Verwandt

| Version | Repository |
|---------|-----------|
| Ilija EVO (Entwickler-Version) | [ilija-AI-Agent](https://github.com/Innobytix-IT/ilija-AI-Agent) |
| Ilija Public Edition (dieses Repo) | ← du bist hier |

---

## 📄 Lizenz

MIT License

---
---

# 🤖 Ilija – Public Edition

> Your personal AI assistant for document management, communication and organisation.

---

## ✨ Features

- **🗂 DMS** – AI-powered document management system with Web GUI
- **🧠 Long-Term Memory** – ChromaDB, persistent across restarts
- **💬 WhatsApp** – monitors chats, schedules appointments, takes messages
- **📱 Telegram** – full remote control, send documents via app
- **🔍 Web Research** – DuckDuckGo, Wikipedia, read web pages
- **🌐 Web Interface** – browser chat with file upload & DMS integration
- **🤖 Multi-Provider** – Claude → GPT → Gemini → Ollama (automatic)

---

## 🚀 Quickstart


```bash
sudo apt update && sudo apt install -y git curl python3-pip python3-venv wget
```

```bash
git clone https://github.com/Innobytix-IT/Ilija-AI-Agent-Public-Edition.git
cd Ilija-AI-Agent-Public-Edition
chmod +x install_EN.sh
./install_EN.sh
```

### Manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Open .env and add at least one API key
python web_server.py
```

---

## ▶️ Starting Ilija

| Interface | Command | URL |
|-----------|---------|-----|
| Web Interface | `python web_server.py` | http://localhost:5000 |
| DMS | `python web_server.py` | http://localhost:5000/dms |
| Telegram Bot | `python telegram_bot.py` | Telegram app |
| Both simultaneously | `python telegram_bot.py & python web_server.py` | – |
| Terminal | `python kernel.py` | Console |

---

## 🗂 DMS – Document Management

Supported formats: PDF · DOCX · XLSX · PPTX · JPG · PNG · TXT · CSV · MD · and more

The AI analyses each file's content and archives automatically into:
```
data/dms/archiv/Category/Subcategory/Year/Filename.pdf
```

**Duplicate detection** via SHA-256 · **Automatic versioning** (_v2, _v3)

Add documents:
- Drag & drop into the Web GUI
- Send via Telegram as file or photo
- Manually copy into `data/dms/import/`

---

## 🔧 Provider Configuration

| Provider | Variable | Model |
|----------|----------|-------|
| Claude | `ANTHROPIC_API_KEY` | claude-opus-4-6 |
| ChatGPT | `OPENAI_API_KEY` | gpt-4o |
| Gemini | `GOOGLE_API_KEY` | gemini-2.5-flash |
| Ollama | — | qwen2.5:7b |

---

## 📱 Telegram Bot Setup

1. @BotFather → `/newbot` → copy token → add to `.env`
2. Find your User ID via @userinfobot → `TELEGRAM_ALLOWED_USERS=` in `.env`
3. `python telegram_bot.py`

**Telegram DMS commands:**
- `/dms_import` – show import folder
- `/dms_sort` – sort documents with AI
- `/dms_stats` – archive statistics
- Send file/photo → automatically saved to DMS import

---

## 📋 Requirements

- Python 3.10+
- Ubuntu / Debian Linux (or macOS comes later)
- Google Chrome (for WhatsApp skill)
- At least one API key **or** local Ollama model

---

## 🔗 Related

| Version | Repository |
|---------|-----------|
| Ilija EVO (Developer version) | [ilija-AI-Agent](https://github.com/Innobytix-IT/ilija-AI-Agent) |
| Ilija Public Edition (this repo) | ← you are here |

---

## 📄 License

MIT License – free to use, share and modify.
