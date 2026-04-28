# Ilija – Public Edition

> Persoenlicher KI-Assistent fuer Bueros und Kleinbetriebe:  
> Dokumentenverwaltung · Telefon-Assistent (FritzBox) · WhatsApp · Telegram · Web-Interface

---

## Features

| Modul | Beschreibung |
|-------|-------------|
| **DMS** | KI-gestuetztes Dokumentenmanagementsystem (PDF, DOCX, XLSX, Bilder, ...) |
| **Telefon-Assistent** | Nimmt Anrufe via FritzBox entgegen, bucht Termine, spricht mit Kunden |
| **Lokaler Kalender** | JSON-Kalender mit freien Slots, Termin-Buchung, 3-Faktor-Authentifizierung |
| **Langzeitgedaechtnis** | ChromaDB, dauerhaft auch nach Neustart |
| **WhatsApp** | Ueberwacht Chats, vereinbart Termine, nimmt Nachrichten an |
| **Telegram** | Vollstaendige Fernsteuerung, Dokumente per App senden |
| **Web-Interface** | Browser-Chat mit Datei-Upload und DMS-Integration |
| **Multi-Provider** | Claude -> GPT -> Gemini -> Ollama (automatisches Fallback) |
| **Workflows** | Automatisierte Aufgaben mit visuell konfigurierbaren Workflows |

---

## Schnellstart (Linux)

```bash
# 1. System vorbereiten
sudo apt update && sudo apt install -y git curl python3-pip python3-venv wget

# 2. Klonen
git clone https://github.com/Innobytix-IT/Ilija-AI-Agent-Public-Edition.git
cd Ilija-AI-Agent-Public-Edition/ilija_public_final

# 3. Installieren (interaktiv)
chmod +x install.sh
./install.sh
```

### Manuell (Linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env oeffnen und mindestens einen API-Key eintragen
python web_server.py
```

---

## Windows – Setup & Control Center

Auf Windows gibt es die grafische Einrichtungsoberflaeche `Ilija_Start_App.py`:

```
python Ilija_Start_App.py
```

Die App enthaelt 9 Reiter fuer die komplette Konfiguration:

| Reiter | Inhalt |
|--------|--------|
| 1. Allgemein | Firmenname, Rolle, Beschreibung |
| 2. KI-Provider | API-Keys fuer Claude, GPT, Gemini, Ollama |
| 3. Gedaechtnis | ChromaDB-Einstellungen |
| 4. Kalender | Verfuegbarkeitszeiten, Terminlaenge |
| 5. DMS | Import- und Archiv-Pfade |
| 6. Server | Port, Debug-Modus |
| **7. FritzBox** | SIP-Server, SIP-User, SIP-Passwort, RTP-Ports, Mikrofon-ID |
| 8. Eingangs-kanaele | Telegram, WhatsApp, E-Mail-Einstellungen |
| 9. Start | Starten, Status, Logs |

---

## Telefon-Assistent (FritzBox)

### Voraussetzungen

- FritzBox mit eingerichtetem IP-Telefonie-Konto
- Linux mit `portaudio19-dev`:  
  `sudo apt-get install -y portaudio19-dev`
- Python-Pakete: `pyaudio edge-tts openai-whisper`

### Einrichten

1. **FritzBox**: Telefonie -> Eigene Rufnummern -> IP-Telefonie-Konto anlegen  
2. **`.env`** eintragen (oder via GUI Reiter 7):

```env
SIP_SERVER=fritz.box
SIP_PORT=5060
SIP_USER=deine_interne_rufnummer
SIP_PASSWORD=dein_sip_passwort
SIP_MY_IP=                 # leer lassen = automatisch ermitteln
SIP_MIC_ID=0               # 0 = Standard-Mikrofon
SIP_RTP_LOW=10000
SIP_RTP_HIGH=10100
```

3. **Wissensbasis befuellen**: Eigene Dokumente in `data/public_info/` ablegen (siehe unten)

4. **Starten**: `python fritzbox_skill.py` oder via Start-Tab der GUI

### Funktionen

- Begruessung und natuerlicher Telefon-Dialog (kein Sprachauswahl-Menue)
- Freie Terminslots aus lokalem Kalender vorlesen
- Termin buchen (wird in `data/local_calendar_events.json` gespeichert)
- Eigene Termine abfragen (3-Faktor-Auth: Rufnummer + Vor- + Nachname)
- Termin stornieren
- Buchstabier-Modus fuer schwierige Namen (NATO-Alphabet)
- Allgemeine Fragen beantworten (Oeffnungszeiten, Adresse, ...)
- Kundenfragen aus eigenen Dokumenten beantworten (Wissensbasis)
- **Kalender-Synchronisation**: Neue Buchungen werden nach dem Anruf automatisch
  an Google Kalender oder Outlook uebertragen (konfigurierbar in Setup & Control Center)

---

## Wissensbasis – `data/public_info/`

Ilija kann Kundenfragen automatisch aus eigenen Dokumenten beantworten –
zum Beispiel zu Preisen, Leistungen, Produkten oder der Adresse.

### So funktioniert es

Dateien die in `data/public_info/` liegen werden beim Start geladen.
Wenn ein Anrufer oder WhatsApp-Kontakt eine Frage stellt, sucht Ilija
keyword-basiert nach passenden Textabschnitten und antwortet darauf –
ohne dass der Nutzer merkt, dass Ilija gerade ein Dokument nachgeschlagen hat.

> **Ilija erfindet dabei nichts.** Er antwortet ausschliesslich auf Basis
> der gefundenen Passagen. Steht die Antwort nicht in den Dokumenten,
> sagt er das dem Anrufer ehrlich.

### Unterstuetzte Formate

| Format | Hinweis |
|--------|---------|
| `.txt` | Empfohlen, keine Abhaengigkeiten |
| `.md`  | Markdown-Formatierung wird als Text gelesen |
| `.pdf` | Benoetigt `pip install pymupdf` oder `pip install pdfplumber` |

### Dateien befuellen

Einfach beliebige Textdateien in `data/public_info/` ablegen, z.B.:

```
data/public_info/
  leistungen.txt        # Beschreibung der angebotenen Dienstleistungen
  preise.txt            # Preisliste
  adresse_kontakt.txt   # Adresse, Telefon, E-Mail
  faq.txt               # Haeufige Fragen und Antworten
```

Dateien die mit `_` beginnen (z.B. `_hinweis.txt`) werden ignoriert
und koennen fuer interne Notizen genutzt werden.

### Ilija proaktiv darauf hinweisen lassen

Damit Ilija die Wissensbasis auch aktiv anbietet wenn Kunden fragen
"Was kannst du?", einfach einen passenden Eintrag im Setup & Control Center
unter **Eingangskanale → Angebotene Dienste** hinzufuegen:

**Telefon (Reiter 8 → Telefon):**
```
Oeffnungszeiten nennen
Termine vereinbaren
Nachricht hinterlassen (der Inhaber wird informiert)
Fragen zu unseren Leistungen und Preisen beantworten
```

**WhatsApp (Reiter 8 → WhatsApp):**
```
Termin vereinbaren
Oeffnungszeiten mitteilen
Allgemeine Fragen beantworten
Fragen zu unseren Leistungen und Produkten beantworten
```

Ilija liest diese Liste vor wenn jemand fragt was er kann –
genau so wie es dort eingetragen ist.

---

## Starten (Linux)

```bash
source venv/bin/activate
```

| Interface | Befehl | URL |
|-----------|--------|-----|
| Web-Interface | `python web_server.py` | http://localhost:5000 |
| DMS | `python web_server.py` | http://localhost:5000/dms |
| Telegram-Bot | `python telegram_bot.py` | Telegram-App |
| Web + Telegram | `python telegram_bot.py & python web_server.py` | – |
| Terminal-Modus | `python kernel.py` | Konsole |

---

## DMS – Dokumentenverwaltung

Unterstuetzte Formate: PDF · DOCX · XLSX · PPTX · JPG · PNG · TXT · CSV · MD

Die KI analysiert jeden Dateiinhalt und archiviert automatisch:
```
data/dms/archiv/Kategorie/Unterkategorie/Jahr/Dateiname.pdf
```

- Duplikat-Erkennung via SHA-256
- Automatische Versionierung (_v2, _v3)
- Drag & Drop in die Web-GUI
- Per Telegram als Datei oder Foto senden
- Manuell in `data/dms/import/` kopieren

---

## Provider konfigurieren

| Provider | .env-Variable | Standard-Modell |
|----------|--------------|----------------|
| Claude (Anthropic) | `ANTHROPIC_API_KEY` | claude-opus-4-6 |
| ChatGPT (OpenAI) | `OPENAI_API_KEY` | gpt-4o |
| Gemini (Google) | `GOOGLE_API_KEY` | gemini-2.5-flash |
| Ollama (lokal) | — | qwen2.5:7b |

Ilija waehlt automatisch den besten verfuegbaren Provider.

---

## Telegram-Bot

1. Telegram -> @BotFather -> `/newbot` -> Token kopieren
2. `TELEGRAM_BOT_TOKEN=...` in `.env` eintragen
3. User-ID ueber @userinfobot -> `TELEGRAM_ALLOWED_USERS=...` in `.env`
4. `python telegram_bot.py`

Telegram-Befehle: `/dms_import` · `/dms_sort` · `/dms_stats`  
Datei/Foto senden -> automatisch in DMS-Import

---

## Projektstruktur

```
ilija_public_final/
|-- install.sh                  # Installationsskript (Linux, interaktiv)
|-- Ilija_Start_App.py          # Windows Setup & Control Center (GUI)
|-- web_server.py               # Flask Web-Interface
|-- telegram_bot.py             # Telegram-Bot
|-- kernel.py                   # Zentraler Agent + Terminal-Modus
|-- customer_kernel.py          # Telefon-Assistent-Kernel
|-- phone_dialog.py             # Telefon-Dialog-Logik (Hybrid LLM + Python)
|-- phone_kernel.py             # Telefon-Basisklasse (Injection-Guard, TTS)
|-- providers.py                # KI-Provider-Management (4 Provider)
|-- skill_manager.py            # Skill-Verwaltung
|-- workflow_routes.py          # Workflow-Automatisierung
|-- local_calendar_routes.py    # Kalender-Web-API
|-- phone_config.json           # Konfiguration des Telefon-Assistenten
|-- skills/
|   |-- dms.py                  # DMS-Skill
|   |-- gedaechtnis.py          # Langzeitgedaechtnis (ChromaDB)
|   |-- basis_tools.py          # Datum, Notizen, Rechner
|   |-- lokaler_kalender_skill.py  # Terminverwaltung (3-Faktor-Auth)
|   |-- fritzbox_skill.py       # FritzBox SIP-Verbindung + Anruf-Loop
|   |-- verfuegbarkeit_skill.py # Oeffnungszeiten-Verwaltung
|   |-- webseiten_inhalt_lesen.py  # Web-Recherche
|   `-- whatsapp_autonomer_dialog.py
|-- templates/
|   |-- index.html              # Web-Chat-Interface
|   `-- dms.html                # DMS Web-GUI
|-- data/
|   |-- local_calendar_events.json   # Lokaler Kalender (nicht committet)
|   |-- verfuegbarkeit.txt           # Verfuegbarkeitszeiten
|   |-- public_info/                 # Infotexte fuer Telefon-Assistent
|   |-- dms/
|   |   |-- import/                  # Neue Dokumente hier ablegen
|   |   `-- archiv/                  # Archivierte Dokumente
|   |-- whatsapp/
|   |   `-- whatsapp_config.json     # WhatsApp-Konfiguration (nicht committet)
|   |-- telegram/
|   |-- email/
|   `-- dms/
|-- tests/
|   |-- test_phone_dialog.py    # Tests: Datums-Parser, Dialog-Logik (35 Tests)
|   |-- test_kalender.py        # Tests: Kalender-Skill (13 Tests)
|   |-- test_workflow_routes.py # Tests: Workflow-API
|   |-- test_basis_tools.py     # Tests: Basis-Skills
|   |-- conftest.py             # Gemeinsame Fixtures
|   |-- helpers.py              # Test-Hilfsfunktionen
|   `-- manual/                 # Manuelle Tests (nicht in pytest)
|       |-- fritz_sip_debug.py  # FritzBox SIP-Verbindungstest
|       `-- fritz_verbindungstest.py
|-- memory/                     # ChromaDB (lokal, nicht committet)
|-- .env.example                # Vorlagendatei fuer Konfiguration
|-- requirements.txt
`-- pyproject.toml
```

---

## Anforderungen

- **Python** 3.10+
- **Linux** Ubuntu/Debian (oder Windows mit `Ilija_Start_App.py`)
- **Telefon-Assistent**: `portaudio19-dev` (Linux), FritzBox mit IP-Telefonie
- **WhatsApp-Skill**: Google Chrome
- Mindestens ein API-Key **oder** lokales Ollama-Modell

---

## Tests ausfuehren

```bash
source venv/bin/activate
pytest tests/ -v
```

Oder mit Coverage:

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

Manuelle FritzBox-Tests (kein pytest, echte Hardware benoetigt):

```bash
python tests/manual/fritz_sip_debug.py
```

---

## Verwandte Projekte

| Version | Repository |
|---------|-----------|
| Ilija EVO (Entwickler-Version) | [ilija-AI-Agent](https://github.com/Innobytix-IT/ilija-AI-Agent) |
| Ilija Public Edition (dieses Repo) | <- du bist hier |

---

## Lizenz

MIT License – kostenlos verwenden, weitergeben und anpassen.

---

---

# Ilija – Public Edition (English)

> Personal AI assistant for offices and small businesses:  
> Document management · Phone assistant (FritzBox) · WhatsApp · Telegram · Web interface

---

## Features

| Module | Description |
|--------|-------------|
| **DMS** | AI-powered document management (PDF, DOCX, XLSX, images, ...) |
| **Phone assistant** | Answers calls via FritzBox, books appointments, talks to customers |
| **Local calendar** | JSON calendar with free slots, appointment booking, 3-factor auth |
| **Long-term memory** | ChromaDB, persistent across restarts |
| **WhatsApp** | Monitors chats, schedules appointments, takes messages |
| **Telegram** | Full remote control, send documents via app |
| **Web interface** | Browser chat with file upload and DMS integration |
| **Multi-provider** | Claude -> GPT -> Gemini -> Ollama (automatic fallback) |
| **Workflows** | Automated tasks with visually configurable workflows |

---

## Quickstart (Linux)

```bash
# 1. Prepare system
sudo apt update && sudo apt install -y git curl python3-pip python3-venv wget

# 2. Clone
git clone https://github.com/Innobytix-IT/Ilija-AI-Agent-Public-Edition.git
cd Ilija-AI-Agent-Public-Edition/ilija_public_final

# 3. Install (interactive)
chmod +x install.sh
./install.sh
```

## Windows – Setup & Control Center

On Windows, use the graphical setup app `Ilija_Start_App.py`:

```
python Ilija_Start_App.py
```

The app has 9 tabs for complete configuration, including a dedicated **FritzBox tab** (tab 7) for SIP/VoIP setup.

---

## Phone Assistant (FritzBox)

### Prerequisites

- FritzBox with IP telephony account configured
- Linux: `sudo apt-get install -y portaudio19-dev`
- Python packages: `pyaudio edge-tts openai-whisper`

### Setup

1. **FritzBox**: Telephony -> Own numbers -> Add IP telephony account
2. **`.env`** (or use GUI tab 7):

```env
SIP_SERVER=fritz.box
SIP_PORT=5060
SIP_USER=your_internal_number
SIP_PASSWORD=your_sip_password
SIP_MY_IP=                 # leave empty = auto-detect
SIP_MIC_ID=0               # 0 = default microphone
SIP_RTP_LOW=10000
SIP_RTP_HIGH=10100
```

### Features

- Natural phone dialogue (no voice menu / IVR)
- Reads available appointment slots from local calendar
- Books appointments (stored in `data/local_calendar_events.json`)
- Lets callers query their own appointments (3-factor auth)
- Cancel appointments
- Spelling mode for difficult names (NATO alphabet)
- Answers general questions (opening hours, address, ...)
- Answers customer questions from your own documents (knowledge base)
- **Calendar sync**: New bookings are automatically pushed to Google Calendar or Outlook
  after each call (configurable in Setup & Control Center)

---

## Knowledge Base – `data/public_info/`

Ilija can automatically answer customer questions from your own documents –
for example about prices, services, products or your address.

### How it works

Files placed in `data/public_info/` are loaded at startup.
When a caller or WhatsApp contact asks a question, Ilija searches for
relevant text passages using keyword matching and answers accordingly –
without the customer noticing that Ilija looked something up.

> **Ilija never makes things up.** It only answers based on the passages
> found in your documents. If the answer is not in the documents,
> Ilija will say so honestly.

### Supported formats

| Format | Note |
|--------|------|
| `.txt` | Recommended, no dependencies |
| `.md`  | Markdown formatting is read as plain text |
| `.pdf` | Requires `pip install pymupdf` or `pip install pdfplumber` |

### Adding documents

Simply place text files in `data/public_info/`, for example:

```
data/public_info/
  services.txt          # Description of offered services
  pricing.txt           # Price list
  contact_address.txt   # Address, phone, email
  faq.txt               # Frequently asked questions
```

Files starting with `_` (e.g. `_notes.txt`) are ignored and can be
used for internal notes.

### Making Ilija proactively mention it

To have Ilija actively offer the knowledge base when customers ask
"What can you do?", add an entry in the Setup & Control Center under
**Input Channels → Offered Services**:

**Phone (Tab 8 → Phone):**
```
State opening hours
Schedule appointments
Take a message (owner will be notified)
Answer questions about our services and pricing
```

**WhatsApp (Tab 8 → WhatsApp):**
```
Schedule appointments
Provide opening hours
Answer general questions
Answer questions about our services and products
```

Ilija reads this list exactly as written when someone asks what it can do.

---

## Requirements

- **Python** 3.10+
- **Linux** Ubuntu/Debian (or Windows with `Ilija_Start_App.py`)
- **Phone assistant**: `portaudio19-dev` (Linux), FritzBox with IP telephony
- **WhatsApp skill**: Google Chrome
- At least one API key **or** local Ollama model

---

## License

MIT License – free to use, share and modify.
