# 🤖 Ilija – Public Workflow-Edition (LINUX)
(English version below)

> Persönlicher KI-Assistent für Automatisierung, Dokumentenverwaltung, Kommunikation und Organisation.

---

## ✨ Features

- **⚡ Workflow Studio** – n8n-ähnlicher visueller Workflow-Builder mit 22 Node-Typen
- **🗂 DMS** – KI-gestütztes Dokumentenmanagementsystem mit Web-GUI
- **🧠 Langzeitgedächtnis** – ChromaDB, dauerhaft auch nach Neustart
- **💬 WhatsApp** – überwacht Chats, vereinbart Termine, nimmt Nachrichten an
- **📱 Telegram** – vollständige Fernsteuerung, Dokumente per App senden
- **🔍 Internet-Recherche** – DuckDuckGo / Google, Wikipedia, Webseiten lesen
- **🌐 Web-Interface** – Browser-Chat mit Datei-Upload & DMS-Integration
- **🤖 Multi-Provider** – Claude → GPT → Gemini → Ollama DSGVO konform (automatisch)

---

## 🚀 Schnellstart

📋 System vorbereiten (einmalig):

```bash
sudo apt update && sudo apt install -y git curl python3-pip python3-venv wget
```

```bash
git clone https://github.com/Innobytix-IT/Ilija-AI-Agent-Public-Edition.git
cd Ilija-AI-Agent-Public-Edition/ilija_public_final
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
| Workflow Studio | `python web_server.py` | http://localhost:5000 |
| Web-Chat | `python web_server.py` | http://localhost:5000/chat |
| DMS | `python web_server.py` | http://localhost:5000/dms |
| Telegram-Bot | `python telegram_bot.py` | Telegram-App |
| Beide gleichzeitig | `python telegram_bot.py & python web_server.py` | – |
| Terminal | `python kernel.py` | Konsole |

---

## ⚡ Workflow Studio

Das Herzstück von Ilija: ein n8n-ähnlicher visueller Workflow-Builder, mit dem du Automatisierungen per Drag & Drop zusammenstellst – ganz ohne Programmieren.

**Aufruf:** `http://localhost:5000`

### Node-Typen

| Kategorie | Nodes |
|-----------|-------|
| **Trigger** | `trigger` (manuell), `schedule_trigger` (Zeitplan), `webhook` |
| **KI** | `chat` (Ilija-Chat), `chatfilter` |
| **Skills** | `skill` (alle installierten Skills aufrufbar) |
| **Kommunikation** | `telegram` (lesen & senden), `gmail`, `email` |
| **Google** | `google_docs` (erstellen/bearbeiten), `google_sheets` |
| **Daten** | `set` (Variable setzen), `memory_window`, `memory_summary` |
| **Logik** | `condition` (wenn/dann), `switch`, `loop`, `wait` |
| **Extern** | `http` (API-Aufrufe), `rss` (Feed-Leser), `code` |
| **Sonstiges** | `note` (Kommentar), `error_handler` |

### Variablen & Verkettung

Nodes werden per Linie verbunden. Das Ergebnis eines Nodes wird als `{{input}}` im nächsten Node verfügbar:

```
[Trigger] → [Skill: internet_suche] → [Chat: "Fasse zusammen: {{input}}"] → [Google Docs: erstellen]
```

### Zeitplan-Trigger

Workflows können automatisch ausgeführt werden – z.B. täglich um 08:00 Uhr oder alle 30 Minuten. Der Scheduler läuft im Hintergrund, solange `web_server.py` aktiv ist.

### Beispiel-Workflows

33 fertige Beispiel-Workflows in `data/workflows/test_workflows/` – direkt importierbar:

- Morgen-Report (Datum + Wetter → KI-Zusammenfassung)
- Internet-Recherche → Google Docs
- Telegram-Nachrichten auslesen → KI-Antwort → zurücksenden
- RSS-Feed-Monitor → E-Mail-Zusammenfassung
- Multi-Themen-Recherche mit Loop
- … und viele mehr

---

## 🗂 DMS – Dokumentenverwaltung

Unterstützte Formate: PDF · DOCX · XLSX · PPTX · JPG · PNG · TXT · CSV · MD · und mehr

Die KI analysiert jeden Dateiinhalt und archiviert automatisch nach:
```
data/dms/archiv/Kategorie/Unterkategorie/Jahr/Dateiname.pdf
```

**Duplikat-Erkennung** via SHA-256 · **Automatische Versionierung** (_v2, _v3)

Dokumente hinzufügen:
- Drag & Drop in die Web-GUI (`/dms`)
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

Ilija wechselt bei Ausfall automatisch zum nächsten verfügbaren Provider.

### Google Websuche (optional)

Für echte Google-Suche statt DuckDuckGo werden zwei zusätzliche Keys benötigt:

```env
GOOGLE_SEARCH_API_KEY=...   # Google Cloud Console → Custom Search API
GOOGLE_SEARCH_CX=...        # programmablesearchengine.google.com → Such-Engine-ID
```

Anleitung dazu in `.env.example`.

---

## 🔑 Google OAuth2 (Kalender, Gmail, Drive, Docs)

Für Workflow-Nodes wie `google_docs`, `gmail` oder `google_sheets` sowie den Kalender-Skill wird eine eigene Google OAuth2-App benötigt.

**Anleitung (ca. 10 Minuten):**

1. [Google Cloud Console](https://console.cloud.google.com/) → Neues Projekt erstellen
2. APIs aktivieren: **Calendar API**, **Gmail API**, **Drive API**, **Docs API**
3. OAuth-Zustimmungsbildschirm → Typ: **Extern** → eigene E-Mail als Testnutzer eintragen
4. Anmeldedaten → **OAuth-Client-ID** → Typ: **Desktop-Anwendung** → JSON herunterladen
5. Heruntergeladene Datei umbenennen zu `credentials.json` und ablegen unter:
   ```
   data/google_kalender/credentials.json
   ```
6. Beim ersten Start öffnet sich ein Browser-Fenster zur Autorisierung → einmalig bestätigen

Eine vollständige Schritt-für-Schritt-Anleitung mit allen Details befindet sich in:
```
data/google_kalender/credentials.example.json
```

---

## 📱 Telegram-Bot

1. `@BotFather` in Telegram → `/newbot` → Token kopieren → in `.env` eintragen als `TELEGRAM_BOT_TOKEN`
2. User-ID über `@userinfobot` → in `.env` eintragen als `TELEGRAM_ALLOWED_USERS`
3. `python telegram_bot.py`

**Telegram-DMS-Befehle:**
- `/dms_import` – Import-Ordner anzeigen
- `/dms_sort` – Dokumente per KI einsortieren
- `/dms_stats` – Archiv-Statistiken
- Datei/Foto senden → automatisch in DMS-Import

---

## 📁 Projektstruktur

```
ilija_public_final/
├── install.sh              # Installationsskript (Deutsch, empfohlen)
├── install_EN.sh           # Installation (English)
├── web_server.py           # Flask-Server (Workflow Studio + Chat + DMS)
├── workflow_routes.py      # n8n-ähnliches Workflow-Backend
├── telegram_bot.py         # Telegram-Bot
├── kernel.py               # Zentraler Agent + Terminal-Modus
├── providers.py            # KI-Provider-Management
├── skill_manager.py        # Skill-Verwaltung
├── dms_routes.py           # DMS Flask-Routen
├── agent_state.py          # Zustandsverwaltung
├── model_registry.py       # Modell-Konfiguration
├── skills/
│   ├── dms.py              # DMS-Skill (KI-Archivierung)
│   ├── gedaechtnis.py      # Langzeitgedächtnis (ChromaDB)
│   ├── basis_tools.py      # Datum, Notizen, Rechner
│   ├── webseiten_inhalt_lesen.py  # Internet-Recherche (DuckDuckGo/Google)
│   ├── telegram_skill.py   # Telegram senden/empfangen
│   ├── email_skill.py      # E-Mail (IMAP/SMTP)
│   ├── outlook_kalender.py # Outlook-Kalender
│   ├── whatsapp_autonomer_dialog.py
│   └── ...
├── templates/
│   ├── index.html          # Workflow Studio UI
│   ├── indexchat.html      # Web-Chat-Interface
│   └── dms.html            # DMS Web-GUI
├── data/
│   ├── workflows/
│   │   └── test_workflows/ # 33 Beispiel-Workflows
│   ├── schedules/          # Zeitplan-Konfiguration (Laufzeit)
│   ├── google_kalender/
│   │   └── credentials.example.json  # Google OAuth2 Vorlage + Anleitung
│   └── dms/
│       ├── import/         # Neue Dokumente hier ablegen
│       └── archiv/         # Archivierte Dokumente
├── memory/                 # ChromaDB-Gedächtnis (lokal, nicht committet)
├── tests/                  # Pytest-Testsuite
├── .env.example            # Konfigurationsvorlage
├── .gitignore
├── requirements.txt
└── models_config.json
```

---

## 📋 Anforderungen

- Python 3.10+
- Ubuntu / Debian Linux (macOS: experimentell)
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

MIT License – kostenlos nutzbar, teilbar und anpassbar.

---
---

# 🤖 Ilija – Public Workflow-Edition

> Your personal AI assistant for automation, document management, communication and organisation.

---

## ✨ Features

- **⚡ Workflow Studio** – n8n-like visual workflow builder with 22 node types
- **🗂 DMS** – AI-powered document management system with Web GUI
- **🧠 Long-Term Memory** – ChromaDB, persistent across restarts
- **💬 WhatsApp** – monitors chats, schedules appointments, takes messages
- **📱 Telegram** – full remote control, send documents via app
- **🔍 Web Research** – DuckDuckGo / Google, Wikipedia, read web pages
- **🌐 Web Interface** – browser chat with file upload & DMS integration
- **🤖 Multi-Provider** – Claude → GPT → Gemini → Ollama (automatic)

---

## 🚀 Quickstart

```bash
sudo apt update && sudo apt install -y git curl python3-pip python3-venv wget
```

```bash
git clone https://github.com/Innobytix-IT/Ilija-AI-Agent-Public-Edition.git
cd Ilija-AI-Agent-Public-Edition/ilija_public_final
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
| Workflow Studio | `python web_server.py` | http://localhost:5000 |
| Web Chat | `python web_server.py` | http://localhost:5000/chat |
| DMS | `python web_server.py` | http://localhost:5000/dms |
| Telegram Bot | `python telegram_bot.py` | Telegram app |
| Both simultaneously | `python telegram_bot.py & python web_server.py` | – |
| Terminal | `python kernel.py` | Console |

---

## ⚡ Workflow Studio

The heart of Ilija: an n8n-like visual workflow builder that lets you create automations by drag & drop – no coding required.

**Open at:** `http://localhost:5000`

### Node Types

| Category | Nodes |
|----------|-------|
| **Trigger** | `trigger` (manual), `schedule_trigger` (scheduled), `webhook` |
| **AI** | `chat` (Ilija chat), `chatfilter` |
| **Skills** | `skill` (all installed skills callable) |
| **Messaging** | `telegram` (read & send), `gmail`, `email` |
| **Google** | `google_docs` (create/edit), `google_sheets` |
| **Data** | `set` (set variable), `memory_window`, `memory_summary` |
| **Logic** | `condition` (if/then), `switch`, `loop`, `wait` |
| **External** | `http` (API calls), `rss` (feed reader), `code` |
| **Other** | `note` (comment), `error_handler` |

### Variables & Chaining

Nodes are connected by drawing lines. The output of one node is passed as `{{input}}` to the next:

```
[Trigger] → [Skill: internet_search] → [Chat: "Summarise: {{input}}"] → [Google Docs: create]
```

### Schedule Trigger

Workflows can run automatically – e.g. every day at 08:00 or every 30 minutes. The scheduler runs in the background as long as `web_server.py` is active.

### Example Workflows

33 ready-to-use example workflows in `data/workflows/test_workflows/`:

- Morning report (date + weather → AI summary)
- Web research → Google Docs
- Read Telegram messages → AI reply → send back
- RSS feed monitor → email summary
- Multi-topic research with loop
- … and many more

---

## 🗂 DMS – Document Management

Supported formats: PDF · DOCX · XLSX · PPTX · JPG · PNG · TXT · CSV · MD · and more

The AI analyses each file's content and archives automatically into:
```
data/dms/archiv/Category/Subcategory/Year/Filename.pdf
```

**Duplicate detection** via SHA-256 · **Automatic versioning** (_v2, _v3)

Add documents:
- Drag & drop into the Web GUI (`/dms`)
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

Ilija automatically switches to the next available provider on failure.

### Google Web Search (optional)

For real Google search instead of DuckDuckGo, two additional keys are required:

```env
GOOGLE_SEARCH_API_KEY=...   # Google Cloud Console → Custom Search API
GOOGLE_SEARCH_CX=...        # programmablesearchengine.google.com → Search Engine ID
```

Setup instructions are in `.env.example`.

---

## 🔑 Google OAuth2 (Calendar, Gmail, Drive, Docs)

Workflow nodes like `google_docs`, `gmail` or `google_sheets` and the calendar skill require your own Google OAuth2 app.

**Setup (approx. 10 minutes):**

1. [Google Cloud Console](https://console.cloud.google.com/) → Create a new project
2. Enable APIs: **Calendar API**, **Gmail API**, **Drive API**, **Docs API**
3. OAuth consent screen → Type: **External** → add your own email as a test user
4. Credentials → **OAuth Client ID** → Type: **Desktop application** → Download JSON
5. Rename the downloaded file to `credentials.json` and place it at:
   ```
   data/google_kalender/credentials.json
   ```
6. On first run, a browser window opens for authorisation → confirm once

A complete step-by-step guide with all details is in:
```
data/google_kalender/credentials.example.json
```

---

## 📱 Telegram Bot Setup

1. `@BotFather` on Telegram → `/newbot` → copy token → add to `.env` as `TELEGRAM_BOT_TOKEN`
2. Get your User ID via `@userinfobot` → add to `.env` as `TELEGRAM_ALLOWED_USERS`
3. `python telegram_bot.py`

**Telegram DMS commands:**
- `/dms_import` – show import folder
- `/dms_sort` – sort documents with AI
- `/dms_stats` – archive statistics
- Send file/photo → automatically saved to DMS import

---

## 📁 Project Structure

```
ilija_public_final/
├── install.sh              # Installer (German, recommended)
├── install_EN.sh           # Installer (English)
├── web_server.py           # Flask server (Workflow Studio + Chat + DMS)
├── workflow_routes.py      # n8n-like workflow backend
├── telegram_bot.py         # Telegram bot
├── kernel.py               # Central agent + terminal mode
├── providers.py            # AI provider management
├── skill_manager.py        # Skill management
├── dms_routes.py           # DMS Flask routes
├── agent_state.py          # State management
├── model_registry.py       # Model configuration
├── skills/
│   ├── dms.py              # DMS skill (AI archiving)
│   ├── gedaechtnis.py      # Long-term memory (ChromaDB)
│   ├── basis_tools.py      # Date, notes, calculator
│   ├── webseiten_inhalt_lesen.py  # Web research (DuckDuckGo/Google)
│   ├── telegram_skill.py   # Telegram send/receive
│   ├── email_skill.py      # Email (IMAP/SMTP)
│   ├── outlook_kalender.py # Outlook calendar
│   ├── whatsapp_autonomer_dialog.py
│   └── ...
├── templates/
│   ├── index.html          # Workflow Studio UI
│   ├── indexchat.html      # Web chat interface
│   └── dms.html            # DMS web GUI
├── data/
│   ├── workflows/
│   │   └── test_workflows/ # 33 example workflows
│   ├── schedules/          # Schedule config (runtime)
│   ├── google_kalender/
│   │   └── credentials.example.json  # Google OAuth2 template + guide
│   └── dms/
│       ├── import/         # Place new documents here
│       └── archiv/         # Archived documents
├── memory/                 # ChromaDB memory (local, not committed)
├── tests/                  # Pytest test suite
├── .env.example            # Configuration template
├── .gitignore
├── requirements.txt
└── models_config.json
```

---

## 📋 Requirements

- Python 3.10+
- Ubuntu / Debian Linux (macOS: experimental)
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
