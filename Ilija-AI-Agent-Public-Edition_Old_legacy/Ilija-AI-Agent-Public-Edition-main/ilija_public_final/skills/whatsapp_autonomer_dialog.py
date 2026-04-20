"""
WhatsApp Autonomer Dialog – Erweiterter Skill
=============================================
Modi:
  "kontakt"         – Spezifischen Kontakt überwachen
  "alle"            – Alle Chats überwachen, auf jeden antworten
  "anrufbeantworter"– Stellt sich vor, nimmt Nachrichten entgegen

Features:
  - Endlos-Listener im Hintergrund-Thread (kein Timeout)
  - Sprachnachrichten transkribieren (Whisper)
  - Gesprächslog mit Zeitstempel → whatsapp_log.txt
  - Log als Gedächtnis für spätere Gespräche
  - Eigentümername aus Ilija-Gedächtnis
"""

import os
import time
import threading
import logging
import datetime
import tempfile

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

_listener_thread = None
_stop_flag = threading.Event()

# Pfade relativ zum data/-Ordner (Public Edition)
_DATA_DIR        = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(_DATA_DIR, exist_ok=True)
LOG_FILE         = os.path.join(_DATA_DIR, "whatsapp_log.txt")
NACHRICHTEN_FILE = os.path.join(_DATA_DIR, "whatsapp_nachrichten.txt")
KALENDER_FILE    = os.path.join(_DATA_DIR, "whatsapp_kalender.txt")


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def remove_emojis(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)


def _log_schreiben(kontakt, absender, nachricht):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    zeile = f"[{ts}] [{kontakt}] {absender}: {nachricht}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(zeile)
    except Exception as e:
        logger.warning(f"Log-Fehler: {e}")


def _nachricht_hinterlassen(kontakt, nachricht):
    """Speichert eine hinterlassene Nachricht mit Zeitstempel."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    zeile = f"[{ts}] Von: {kontakt} | Nachricht: {nachricht}\n"
    try:
        with open(NACHRICHTEN_FILE, "a", encoding="utf-8") as f:
            f.write(zeile)
        logger.info(f"Nachricht hinterlassen von {kontakt}")
    except Exception as e:
        logger.warning(f"Nachricht-Datei Fehler: {e}")


def _kalender_konflikt_pruefen(datum, uhrzeit):
    """
    Prüft ob ein Termin zu diesem Datum+Uhrzeit bereits existiert.
    Gibt (True, bestehender_eintrag) zurück wenn Konflikt, sonst (False, "")
    """
    try:
        if not os.path.exists(KALENDER_FILE):
            return False, ""
        with open(KALENDER_FILE, encoding="utf-8") as f:
            zeilen = f.readlines()
        for zeile in zeilen:
            zeile = zeile.strip()
            if zeile.startswith("#") or not zeile:
                continue
            # Nur echte Termineinträge prüfen (nicht VERFÜGBAR/GESPERRT)
            if zeile.startswith("[VERFÜGBAR]") or zeile.startswith("[GESPERRT]"):
                continue
            # Format: [YYYY-MM-DD] [Wochentag] [HH:MM] [Kontakt] Titel
            if f"[{datum}]" in zeile and f"[{uhrzeit}]" in zeile:
                return True, zeile
        return False, ""
    except Exception as e:
        logger.warning(f"Konflikt-Prüfung Fehler: {e}")
        return False, ""


def _kalender_eintrag_hinzufuegen(kontakt, datum, uhrzeit, titel):
    """
    Fügt einen Termin in den Kalender ein – mit hartem Konflikt-Check.
    Gibt (True, "") bei Erfolg zurück, (False, grund) bei Konflikt/Fehler.
    """
    # ── Harter Code-Check ────────────────────────────────────────────
    konflikt, bestehend = _kalender_konflikt_pruefen(datum, uhrzeit)
    if konflikt:
        logger.warning(f"Termin-Konflikt: {datum} {uhrzeit} bereits belegt → {bestehend}")
        return False, f"Zeitslot bereits belegt: {bestehend}"

    try:
        wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                      "Freitag", "Samstag", "Sonntag"]
        dt = datetime.datetime.strptime(f"{datum} {uhrzeit}", "%Y-%m-%d %H:%M")
        wochentag = wochentage[dt.weekday()]
        zeile = f"[{datum}] [{wochentag}] [{uhrzeit}] [{kontakt}] {titel}\n"
        with open(KALENDER_FILE, "a", encoding="utf-8") as f:
            f.write(zeile)
        logger.info(f"Termin eingetragen: {zeile.strip()}")
        return True, ""
    except Exception as e:
        logger.warning(f"Kalender-Fehler: {e}")
        return False, str(e)


def _kalender_lesen():
    """Liest alle Kalendereinträge, sortiert nach Datum."""
    try:
        if not os.path.exists(KALENDER_FILE):
            return []
        with open(KALENDER_FILE, encoding="utf-8") as f:
            zeilen = [z.strip() for z in f.readlines() if z.strip()]
        return sorted(zeilen)  # alphabetisch = chronologisch wegen [YYYY-MM-DD]
    except Exception:
        return []


def _kalender_als_text():
    """Gibt den kompletten Kalenderinhalt als Text zurück (inkl. Verfügbarkeiten)."""
    try:
        if not os.path.exists(KALENDER_FILE):
            return "Kalender nicht gefunden."
        with open(KALENDER_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "Kalender konnte nicht gelesen werden."


def _kalender_initialisieren():
    """
    Erstellt die Kalenderdatei mit Platzhaltern falls sie noch nicht existiert.
    """
    if os.path.exists(KALENDER_FILE):
        return
    inhalt = """\
# ══════════════════════════════════════════════════════
# WhatsApp-Kalender – Ilija Terminverwaltung
# ══════════════════════════════════════════════════════
#
# VERFÜGBARKEIT: Wann bist du grundsätzlich erreichbar?
# Format: [VERFÜGBAR] [Tag oder Tage] [HH:MM-HH:MM]
#
[VERFÜGBAR] [Montag-Freitag] [09:00-12:00]
[VERFÜGBAR] [Dienstag] [15:00-17:00]
[GESPERRT]  [Samstag-Sonntag]
#
# TERMINE: Werden automatisch von Ilija eingetragen.
# Format: [YYYY-MM-DD] [Wochentag] [HH:MM] [Kontakt] Titel
# Beispiel:
# [2026-03-18] [Dienstag] [15:00] [Karsten] Kaffee
#
# ── Eingetragene Termine ────────────────────────────
"""
    try:
        with open(KALENDER_FILE, "w", encoding="utf-8") as f:
            f.write(inhalt)
        logger.info(f"Kalender initialisiert: {KALENDER_FILE}")
    except Exception as e:
        logger.warning(f"Kalender-Init Fehler: {e}")


def _nachrichten_initialisieren():
    """
    Erstellt die Nachrichten-Datei mit Erklärung falls sie noch nicht existiert.
    """
    if os.path.exists(NACHRICHTEN_FILE):
        return
    inhalt = """\
# ══════════════════════════════════════════════════════
# WhatsApp-Nachrichten – Hinterlassene Nachrichten
# ══════════════════════════════════════════════════════
# Hier speichert Ilija automatisch Nachrichten die
# WhatsApp-Kontakte explizit hinterlassen haben.
# Format: [DATUM UHRZEIT] Von: [Kontakt] | Nachricht: [Text]
#
# ── Hinterlassene Nachrichten ───────────────────────
"""
    try:
        with open(NACHRICHTEN_FILE, "w", encoding="utf-8") as f:
            f.write(inhalt)
        logger.info(f"Nachrichten-Datei initialisiert: {NACHRICHTEN_FILE}")
    except Exception as e:
        logger.warning(f"Nachrichten-Init Fehler: {e}")


def _log_lesen(kontakt=None, max_zeilen=50):
    try:
        if not os.path.exists(LOG_FILE):
            return ""
        with open(LOG_FILE, encoding="utf-8") as f:
            zeilen = f.readlines()
        if kontakt:
            zeilen = [z for z in zeilen if f"[{kontakt}]" in z]
        return "".join(zeilen[-max_zeilen:])
    except Exception:
        return ""


def _eigentümer_aus_gedächtnis():
    try:
        import sys, os as _os
        _skills_dir = _os.path.dirname(_os.path.abspath(__file__))
        if _skills_dir not in sys.path:
            sys.path.insert(0, _skills_dir)
        from gedaechtnis import gedaechtnis_suchen
        result = gedaechtnis_suchen("Name des Eigentümers Nutzer Besitzer")
        for zeile in result.split("\n"):
            zeile = zeile.strip()
            if zeile and "Nichts" not in zeile and "Erinnerungen" not in zeile and zeile != "•":
                # "  • Manuel" → "Manuel"
                return zeile.lstrip("• ").strip()
    except Exception:
        pass
    return "deinem Assistenten"


def _transkribiere_audio(audio_url, driver):
    try:
        import requests
        import subprocess
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        headers = {"User-Agent": driver.execute_script("return navigator.userAgent;")}
        response = requests.get(audio_url, cookies=cookies, headers=headers, timeout=30)
        if response.status_code != 200:
            return ""
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        wav_path = tmp_path.replace(".ogg", ".wav")
        subprocess.run(["ffmpeg", "-y", "-i", tmp_path, wav_path],
                       capture_output=True, timeout=30)
        os.unlink(tmp_path)
        import whisper
        model = whisper.load_model("base", device="cpu")
        result = model.transcribe(wav_path, language="de")
        os.unlink(wav_path)
        text = result.get("text", "").strip()
        return f"[Sprachnachricht]: {text}" if text else ""
    except Exception as e:
        logger.warning(f"Audio-Transkription fehlgeschlagen: {e}")
        return ""


def _hole_letzte_eingehende(driver):
    """
    Gibt (text, audio_url) der letzten eingehenden Nachricht zurück.
    Erkennt Medientypen anhand von HTML-Elementen.
    """
    import re
    try:
        msgs = driver.find_elements(
            By.XPATH, '//div[contains(@class, "message-in")]')
        if not msgs:
            return "", ""
        letztes = msgs[-1]

        # Bild erkennen
        try:
            letztes.find_element(By.XPATH,
                './/img[contains(@src,"blob:") or contains(@class,"media")]'
                ' | .//div[@data-testid="media-canvas"]'
                ' | .//div[contains(@data-testid,"image")]')
            return "[Bild]", ""
        except Exception:
            pass

        # Video erkennen
        try:
            letztes.find_element(By.XPATH,
                './/video | .//div[@data-testid="video-pip"]'
                ' | .//span[@data-testid="video-play"]')
            return "[Video]", ""
        except Exception:
            pass

        # Sprachnachricht per Audio-Tag
        try:
            audio = letztes.find_element(By.TAG_NAME, "audio")
            src = audio.get_attribute("src") or ""
            return "[Sprachnachricht]", src if src else ""
        except Exception:
            pass

        # Sprachnachricht per Icon
        try:
            letztes.find_element(By.XPATH,
                './/span[@data-testid="audio-play"]'
                ' | .//div[@data-testid="audio-player"]'
                ' | .//button[contains(@class,"audio")]')
            return "[Sprachnachricht]", ""
        except Exception:
            pass

        # Dokument / Datei erkennen
        try:
            letztes.find_element(By.XPATH,
                './/div[@data-testid="document-thumb"]'
                ' | .//span[@data-testid="document"]'
                ' | .//div[contains(@class,"document")]')
            return "[Dokument]", ""
        except Exception:
            pass

        # Sticker erkennen
        try:
            letztes.find_element(By.XPATH,
                './/div[@data-testid="sticker"]'
                ' | .//img[contains(@class,"sticker")]')
            return "[Sticker]", ""
        except Exception:
            pass

        text = letztes.text.split('\n')[0].strip()

        # Zeitformat "0:03" oder "1:23" → Sprachnachricht-Dauer
        if re.match(r'^\d+:\d{2}$', text):
            return "[Sprachnachricht]", ""

        return text, ""
    except Exception:
        return "", ""


def _hole_chats_mit_ungelesenen(driver):
    """
    Gibt Liste der Chat-Elemente mit ungelesenen Nachrichten zurück.
    Nutzt JavaScript um zuverlässig alle ungelesenen Chats zu finden.
    """
    ergebnis = []
    gefundene_namen = set()

    # Strategie 1: JavaScript – sucht nach Badges mit Zahlen (grüne Kreise)
    try:
        chats_js = driver.execute_script("""
            const results = [];
            // Alle Span-Elemente mit data-testid die "unread" enthalten
            const badges = document.querySelectorAll(
                'span[data-testid="icon-unread-count"], ' +
                'span[aria-label*="unread"], ' +
                'span[aria-label*="ungelesen"]'
            );
            badges.forEach(badge => {
                // Chat-Container hochgehen
                let el = badge;
                for (let i = 0; i < 10; i++) {
                    el = el.parentElement;
                    if (!el) break;
                    const title = el.querySelector('span[dir="auto"][title]');
                    if (title && title.getAttribute("title")) {
                        results.push(title.getAttribute("title"));
                        break;
                    }
                }
            });
            return results;
        """)

        if chats_js:
            for name in chats_js:
                if name and name not in gefundene_namen:
                    gefundene_namen.add(name)
                    # Chat per Klick öffnen via Suchfeld
                    ergebnis.append({"name": name, "element": None, "per_suche": True})

    except Exception as e:
        logger.debug(f"JS Chat-Scan Fehler: {e}")

    # Strategie 2: XPath-Fallback mit mehreren Varianten
    if not ergebnis:
        xpath_varianten = [
            '//span[@data-testid="icon-unread-count"]',
            '//div[contains(@aria-label,"unread")]',
            '//span[contains(@class,"unread")]',
        ]
        for xpath in xpath_varianten:
            try:
                elemente = driver.find_elements(By.XPATH, xpath)
                for el in elemente:
                    try:
                        for anc_xpath in [
                            './ancestor::div[@data-testid="cell-frame-container"]',
                            './ancestor::li',
                            './ancestor::div[@role="listitem"]',
                        ]:
                            try:
                                container = el.find_element(By.XPATH, anc_xpath)
                                for n_xpath in [
                                    './/span[@dir="auto"][@title]',
                                    './/span[contains(@class,"_ao3e")]',
                                ]:
                                    try:
                                        name_el = container.find_element(By.XPATH, n_xpath)
                                        name = name_el.get_attribute("title") or name_el.text
                                        if name and name not in gefundene_namen:
                                            gefundene_namen.add(name)
                                            ergebnis.append({"name": name, "element": container, "per_suche": False})
                                        break
                                    except Exception:
                                        continue
                                break
                            except Exception:
                                continue
                    except Exception:
                        continue
                if ergebnis:
                    break
            except Exception:
                continue

    return ergebnis


def _oeffne_kontakt_per_suche(driver, name):
    wait = WebDriverWait(driver, 30)
    sb = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
    sb.click()
    sb.send_keys(Keys.CONTROL + "a")
    sb.send_keys(Keys.BACKSPACE)
    sb.send_keys(remove_emojis(name))
    time.sleep(1.5)
    sb.send_keys(Keys.ENTER)
    time.sleep(1.5)


def _sende_nachricht(driver, text):
    try:
        wait = WebDriverWait(driver, 15)
        mb = wait.until(EC.presence_of_element_located(
            (By.XPATH,
             '//div[@contenteditable="true"][@role="textbox"][@data-tab="10"]')))
        for i, zeile in enumerate(text.split('\n')):
            mb.send_keys(zeile)
            if i < len(text.split('\n')) - 1:
                mb.send_keys(Keys.SHIFT, Keys.ENTER)
        time.sleep(0.3)
        mb.send_keys(Keys.ENTER)
        time.sleep(2)
    except Exception as e:
        logger.error(f"Senden fehlgeschlagen: {e}")


# ── Dialog-Loop ───────────────────────────────────────────────────────────────

def _dialog_loop(driver, provider, modus, kontakt_name, eigentümer,
                 audio_transkription, poll_intervall):
    verlaeufe = {}
    letzte_nachrichten = {}

    # Kalender für Kontext laden
    kalender_kontext = _kalender_als_text()
    heute_dt = datetime.datetime.now()
    heute = heute_dt.strftime("%Y-%m-%d %A")

    system_basis = (
        f"Du bist Ilija, ein freundlicher KI-Assistent von {eigentümer}. "
        f"Du chattest auf WhatsApp mit Kontakten von {eigentümer}. "
        f"Antworte nur mit reinem Text, KEINE Emojis. "
        f"Sei kurz, natürlich und gesprächig – wie ein echter Mensch auf WhatsApp. "
        f"WICHTIG: Beginne JEDE Antwort mit 'KI Ilija: '.\n\n"
        f"Heute ist: {heute}\n\n"
        f"VERHALTEN:\n"
        f"- Führe normale Gespräche – nicht jede Nachricht dreht sich um Termine!\n"
        f"- Antworte auf das was der Kontakt WIRKLICH schreibt\n"
        f"- Biete Termine NUR an wenn der Kontakt explizit danach fragt\n"
        f"- Wenn jemand einfach 'Hallo' schreibt, antworte freundlich und frag was er möchte\n"
        f"- Wenn jemand sagt 'ich möchte keinen Termin' – akzeptiere das sofort\n\n"
        f"KALENDER-ZUGRIFF (nur nutzen wenn Kontakt Termin möchte):\n"
        f"{kalender_kontext}\n\n"
        f"TERMINBUCHUNG – nur wenn explizit gewünscht:\n"
        f"1. Frage kurz worum es geht\n"
        f"2. Berechne freie Slots aus [VERFÜGBAR]-Zeilen für die gewünschte Woche\n"
        f"3. Bereits eingetragene [YYYY-MM-DD] Termine sind BELEGT\n"
        f"4. Biete 3-4 konkrete Optionen an: Wochentag, Datum, Uhrzeit\n"
        f"5. Nach Bestätigung speichere mit: "
        f"TERMIN_SPEICHERN:[YYYY-MM-DD]|[HH:MM]|[Titel + Kontaktname]\n\n"
        f"NACHRICHT HINTERLASSEN – nur wenn Kontakt das explizit möchte:\n"
        f"Bitte um den Text, dann: NACHRICHT_SPEICHERN:[die Nachricht]\n\n"
        f"WICHTIG: Sende NIEMALS interne Befehle (TERMIN_SPEICHERN, NACHRICHT_SPEICHERN) "
        f"sichtbar in der WhatsApp-Nachricht. Diese werden intern verarbeitet."
    )
    if modus == "anrufbeantworter":
        system_basis += (
            f"\nDu bist Anrufbeantworter für {eigentümer}. "
            f"Stelle dich beim ersten Kontakt vor: "
            f"'Hallo, mein Name ist Ilija. Ich bin ein autonomer KI-Assistent von "
            f"{eigentümer}. Vielleicht kann ich dir weiterhelfen? "
            f"Du kannst {eigentümer} auch gerne eine Nachricht hinterlassen.'"
        )

    def get_verlauf(kontakt):
        if kontakt not in verlaeufe:
            früherer_log = _log_lesen(kontakt=kontakt, max_zeilen=20)
            memory = (f"\n\nFrüherer Verlauf mit {kontakt}:\n{früherer_log}"
                      if früherer_log else "")
            verlaeufe[kontakt] = [
                {"role": "system", "content": system_basis + memory}]
        return verlaeufe[kontakt]

    # Medientypen die Ilija nicht lesen kann
    MEDIA_HINWEISE = {
        "[Sprachnachricht]": "Sprachnachricht",
        "[Bild]": "Bild",
        "[Video]": "Video",
        "[Dokument]": "Dokument",
        "[Datei]": "Datei",
        "[GIF]": "GIF",
        "[Sticker]": "Sticker",
    }

    def _ist_medien_nachricht(text: str) -> str:
        """Gibt den Medientyp zurück wenn es kein Text ist, sonst ''."""
        for marker, typ in MEDIA_HINWEISE.items():
            if text.startswith(marker):
                return typ
        return ""

    def _zurueck_zur_chatliste(driver):
        """Navigiert zurück zur WhatsApp Chat-Übersicht."""
        try:
            # Escape schließt oft die Suche/den Chat
            from selenium.webdriver.common.keys import Keys as K
            driver.find_element(By.XPATH, '//body').send_keys(K.ESCAPE)
            time.sleep(0.5)
        except Exception:
            pass

    def verarbeite(kontakt, text, audio_url=""):
        # ── Medien erkennen ──────────────────────────────────────────
        medientyp = _ist_medien_nachricht(text)
        if medientyp or (audio_url and not audio_transkription):
            typ_text = medientyp or "Sprachnachricht"
            direkt_antwort = (
                f"KI Ilija: Ich habe eine {typ_text} erhalten, "
                f"kann aber leider nur Textnachrichten lesen und beantworten. "
                f"Bitte schreib mir dein Anliegen als Text."
            )
            print(f"💬 [{kontakt}]: [{typ_text}]")
            _log_schreiben(kontakt, kontakt, f"[{typ_text}]")
            _sende_nachricht(driver, direkt_antwort)
            print(f"🤖 [Ilija → {kontakt}]: {direkt_antwort}")
            _log_schreiben(kontakt, "KI Ilija", direkt_antwort)
            return

        # ── Audio transkribieren ─────────────────────────────────────
        if audio_url and audio_transkription:
            transkript = _transkribiere_audio(audio_url, driver)
            if transkript:
                text = transkript
            else:
                direkt_antwort = (
                    "KI Ilija: Ich habe eine Sprachnachricht erhalten, "
                    "konnte sie aber leider nicht transkribieren. "
                    "Kannst du mir das als Text schreiben?"
                )
                _sende_nachricht(driver, direkt_antwort)
                _log_schreiben(kontakt, "KI Ilija", direkt_antwort)
                return

        print(f"💬 [{kontakt}]: {text}")
        _log_schreiben(kontakt, kontakt, text)

        verlauf = get_verlauf(kontakt)
        verlauf.append({"role": "user", "content": text})

        try:
            antwort_roh = remove_emojis(provider.chat(verlauf)).strip()

            # ── Spezial-Befehle aus LLM-Antwort parsen ──────────────
            nachricht_gespeichert = False
            termin_gespeichert = False

            # NACHRICHT_SPEICHERN:[text]
            if "NACHRICHT_SPEICHERN:" in antwort_roh:
                import re as _re
                m = _re.search(r'NACHRICHT_SPEICHERN:\[(.+?)\]', antwort_roh)
                if m:
                    _nachricht_hinterlassen(kontakt, m.group(1))
                    nachricht_gespeichert = True
                # Befehl aus sichtbarer Antwort entfernen
                antwort_roh = _re.sub(r'NACHRICHT_SPEICHERN:\[.+?\]', '', antwort_roh).strip()

            # TERMIN_SPEICHERN – Klammern optional (LLM lässt sie oft weg)
            if "TERMIN_SPEICHERN:" in antwort_roh:
                import re as _re
                # Akzeptiert: TERMIN_SPEICHERN:2026-02-24|16:00|Titel
                #         und: TERMIN_SPEICHERN:[2026-02-24]|[16:00]|[Titel]
                m = _re.search(
                    r'TERMIN_SPEICHERN:\[?([0-9]{4}-[0-9]{2}-[0-9]{2})\]?\|'
                    r'\[?([0-9]{2}:[0-9]{2})\]?\|\[?(.+?)\]?(?:\n|$)',
                    antwort_roh
                )
                if not m:
                    m = _re.search(
                        r'TERMIN_SPEICHERN:([0-9]{4}-[0-9]{2}-[0-9]{2})\|([0-9]{2}:[0-9]{2})\|(.+)',
                        antwort_roh
                    )
                if m:
                    datum   = m.group(1).strip("[] ")
                    uhrzeit = m.group(2).strip("[] ")
                    titel   = m.group(3).strip("[] ").strip()
                    # Kontaktname am Ende entfernen falls LLM ihn nochmal anhängt
                    if f"+ {kontakt}" in titel:
                        titel = titel.replace(f"+ {kontakt}", "").strip()
                    if titel.endswith(kontakt):
                        titel = titel[:-len(kontakt)].strip().rstrip("+").strip()
                    ok, grund = _kalender_eintrag_hinzufuegen(kontakt, datum, uhrzeit, titel)
                    if ok:
                        termin_gespeichert = True
                    else:
                        logger.warning(f"Termin-Konflikt blockiert: {grund}")
                        konflikt_antwort = (
                            f"KI Ilija: Entschuldigung, dieser Zeitslot ({datum} um {uhrzeit} Uhr) "
                            f"ist leider bereits vergeben. Bitte wähle einen anderen Termin."
                        )
                        _sende_nachricht(driver, konflikt_antwort)
                        _log_schreiben(kontakt, "KI Ilija", konflikt_antwort)
                        print(f"⚠️  Termin-Konflikt blockiert: {grund}")
                        return
                # Befehl aus sichtbarer Nachricht entfernen
                antwort_roh = _re.sub(r'TERMIN_SPEICHERN:[^\n]+', '', antwort_roh).strip()

            # KI-Prefix sicherstellen
            if not antwort_roh.startswith("KI Ilija:"):
                antwort = f"KI Ilija: {antwort_roh}"
            else:
                antwort = antwort_roh

            verlauf.append({"role": "assistant", "content": antwort})
            _sende_nachricht(driver, antwort)
            print(f"🤖 [Ilija → {kontakt}]: {antwort}")
            _log_schreiben(kontakt, "KI Ilija", antwort)

            if nachricht_gespeichert:
                print(f"📌 Nachricht von {kontakt} gespeichert → {NACHRICHTEN_FILE}")
            if termin_gespeichert:
                print(f"📅 Termin für {kontakt} eingetragen → {KALENDER_FILE}")
        except Exception as e:
            logger.error(f"LLM-Fehler: {e}")

    # ── Modus: spezifischer Kontakt ──────────────────────────────────────────
    if modus == "kontakt":
        letzte_nachrichten[kontakt_name] = _hole_letzte_eingehende(driver)[0]
        print(f"👂 Lausche dauerhaft auf '{kontakt_name}'...")
        while not _stop_flag.is_set():
            try:
                text, audio_url = _hole_letzte_eingehende(driver)
                if text and text != letzte_nachrichten.get(kontakt_name, ""):
                    letzte_nachrichten[kontakt_name] = text
                    verarbeite(kontakt_name, text, audio_url)
            except Exception as e:
                logger.warning(f"[Kontakt-Loop] {e}")
            _stop_flag.wait(timeout=poll_intervall)

    # ── Modus: alle / anrufbeantworter ───────────────────────────────────────
    else:
        print(f"👂 Überwache ALLE WhatsApp-Chats (Modus: {modus})...")

        # Aktuell offener Chat – damit wir wissen wo wir sind
        aktiver_chat = ""

        while not _stop_flag.is_set():
            try:
                chats = _hole_chats_mit_ungelesenen(driver)
                if chats:
                    print(f"🔔 {len(chats)} Chat(s) mit neuen Nachrichten")

                for chat in chats:
                    name = chat["name"]
                    try:
                        # Chat öffnen
                        if chat.get("per_suche") or chat.get("element") is None:
                            _oeffne_kontakt_per_suche(driver, name)
                        else:
                            chat["element"].click()
                            time.sleep(1.5)
                        aktiver_chat = name

                        text, audio_url = _hole_letzte_eingehende(driver)
                        if text and text != letzte_nachrichten.get(name, ""):
                            letzte_nachrichten[name] = text
                            verarbeite(name, text, audio_url)
                            # Gesendete Antwort als letzte Nachricht merken
                            # (verhindert Doppel-Antwort auf eigene Nachricht)
                            time.sleep(1)

                    except Exception as e:
                        logger.warning(f"[Chat {name}] {e}")
                    finally:
                        # ── WICHTIG: Nach jeder Antwort zurück zur Übersicht ──
                        # Nur so sieht der Badge-Scanner beim nächsten Poll
                        # wieder ALLE Chats mit ungelesenen Nachrichten
                        try:
                            _zurueck_zur_chatliste(driver)
                            aktiver_chat = ""
                            time.sleep(0.5)
                        except Exception:
                            pass

                # Wenn gerade kein Chat offen sein muss, Übersicht sicherstellen
                if not chats and aktiver_chat:
                    _zurueck_zur_chatliste(driver)
                    aktiver_chat = ""

            except Exception as e:
                logger.warning(f"[Alle-Loop] {e}")
            _stop_flag.wait(timeout=poll_intervall)

    print("🛑 [WhatsApp-Listener] Gestoppt.")


# ── Öffentliche Skill-Funktionen ──────────────────────────────────────────────

def whatsapp_autonomer_dialog(
    modus: str = "alle",
    kontakt_name: str = "",
    start_nachricht: str = "",
    audio_transkription: bool = True,
    poll_intervall: int = 5
) -> str:
    """
    Startet den WhatsApp-Assistenten – beantwortet eingehende Nachrichten automatisch.
    Eigene WhatsApp-Nachrichten des Nutzers werden beantwortet (kein Zugriff auf fremde Daten).

    WANN NUTZEN:
    - "Starte WhatsApp" / "WhatsApp Assistent" / "beantworte WhatsApp Nachrichten"
      → modus="alle"
    - "Schreib mit [Name]" / "Starte Chat mit [Kontakt]"
      → modus="kontakt", kontakt_name="[Name]"
    - "Anrufbeantworter" / "vertrete mich"
      → modus="anrufbeantworter"

    Parameter:
      modus="alle"             – Beantwortet alle eingehenden Nachrichten im eigenen WhatsApp
      modus="kontakt"          – Führt Chat mit einem bestimmten Kontakt (kontakt_name nötig)
      modus="anrufbeantworter" – Nimmt Nachrichten entgegen, stellt sich als Assistent vor
      kontakt_name             – Name des Kontakts (nur bei modus="kontakt")
      start_nachricht          – Erste Nachricht die gesendet wird (optional)
      audio_transkription      – Sprachnachrichten transkribieren (Standard: True)

    Läuft im Hintergrund bis whatsapp_listener_stoppen() aufgerufen wird.
    """
    global _listener_thread, _stop_flag

    if modus not in ("kontakt", "alle", "anrufbeantworter"):
        return "❌ Modus muss 'kontakt', 'alle' oder 'anrufbeantworter' sein."
    if modus == "kontakt" and not kontakt_name:
        return "❌ Modus 'kontakt' benötigt einen kontakt_name."

    if _listener_thread and _listener_thread.is_alive():
        _stop_flag.set()
        _listener_thread.join(timeout=5)
    _stop_flag = threading.Event()

    # Browser
    try:
        import sys, os as _os
        _skills_dir = _os.path.dirname(_os.path.abspath(__file__))
        if _skills_dir not in sys.path:
            sys.path.insert(0, _skills_dir)
        import browser_oeffnen
        driver = browser_oeffnen.driver
        if driver is None:
            browser_oeffnen.browser_oeffnen("https://web.whatsapp.com")
            driver = browser_oeffnen.driver
        if driver is None:
            return "❌ Browser konnte nicht gestartet werden."
        if "web.whatsapp.com" not in driver.current_url:
            driver.get("https://web.whatsapp.com")
            time.sleep(3)
    except ImportError:
        return "❌ Modul 'browser_oeffnen' nicht gefunden."

    # LLM
    try:
        from providers import select_provider
        _, provider = select_provider("auto")
    except Exception as e:
        return f"❌ LLM Provider Fehler: {e}"

    eigentümer = _eigentümer_aus_gedächtnis()

    # Dateien initialisieren falls noch nicht vorhanden
    _kalender_initialisieren()
    _nachrichten_initialisieren()

    # Kontakt öffnen + Startnachricht
    if modus == "kontakt":
        try:
            wait = WebDriverWait(driver, 60)
            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            _oeffne_kontakt_per_suche(driver, kontakt_name)
        except Exception as e:
            return f"❌ Kontakt konnte nicht geöffnet werden: {e}"
        if start_nachricht:
            clean = remove_emojis(start_nachricht)
            _sende_nachricht(driver, clean)
            _log_schreiben(kontakt_name, "Ilija", clean)
            print(f"🤖 [Ilija startet]: {clean}")

    _listener_thread = threading.Thread(
        target=_dialog_loop,
        args=(driver, provider, modus, kontakt_name, eigentümer,
              audio_transkription, poll_intervall),
        daemon=True,
        name="WhatsApp-Listener"
    )
    _listener_thread.start()

    modus_text = {
        "kontakt": f"Kontakt '{kontakt_name}'",
        "alle": "Alle Chats",
        "anrufbeantworter": f"Anrufbeantworter für {eigentümer}",
    }[modus]

    return (
        f"✅ WhatsApp-Listener aktiv\n"
        f"📋 Modus: {modus_text}\n"
        f"🎙️  Audio-Transkription: {'✅ aktiv' if audio_transkription else '🔇 aus'}\n"
        f"🔄 Prüft alle {poll_intervall}s – kein Zeitlimit\n"
        f"📝 Log: {LOG_FILE}\n"
        f"💡 Stoppen: whatsapp_listener_stoppen()"
    )


def whatsapp_listener_stoppen() -> str:
    """Stoppt den laufenden WhatsApp-Listener."""
    global _listener_thread, _stop_flag
    if not _listener_thread or not _listener_thread.is_alive():
        return "ℹ️  Kein aktiver Listener."
    _stop_flag.set()
    _listener_thread.join(timeout=10)
    return "✅ WhatsApp-Listener gestoppt."


def whatsapp_listener_status() -> str:
    """Gibt Status des Listeners und Größe des Logs zurück."""
    aktiv = _listener_thread and _listener_thread.is_alive()
    status = f"{'✅ Läuft' if aktiv else '💤 Inaktiv'}\n"
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding="utf-8") as f:
            n = len(f.readlines())
        status += f"📝 Log: {n} Einträge ({LOG_FILE})"
    else:
        status += "📝 Noch kein Log."
    return status


def whatsapp_log_lesen(kontakt: str = "", max_zeilen: int = 30) -> str:
    """
    Liest den WhatsApp-Gesprächslog.
    kontakt: Optional – filtert nach einem bestimmten Kontakt.
    """
    inhalt = _log_lesen(kontakt=kontakt or None, max_zeilen=max_zeilen)
    if not inhalt:
        return "📝 Log leer oder Kontakt nicht gefunden."
    return f"📝 WhatsApp-Log{f' [{kontakt}]' if kontakt else ''}:\n\n{inhalt}"


def whatsapp_nachrichten_lesen() -> str:
    """
    Liest alle hinterlassenen Nachrichten aus whatsapp_nachrichten.txt.
    Nutze diesen Skill wenn der User fragt: 'Welche Nachrichten wurden hinterlassen?'
    oder 'Zeig mir die WhatsApp-Nachrichten'.
    """
    try:
        if not os.path.exists(NACHRICHTEN_FILE):
            return "📬 Noch keine Nachrichten hinterlassen."
        with open(NACHRICHTEN_FILE, encoding="utf-8") as f:
            inhalt = f.read().strip()
        if not inhalt:
            return "📬 Noch keine Nachrichten hinterlassen."
        zeilen = len(inhalt.splitlines())
        return f"📬 Hinterlassene Nachrichten ({zeilen} Einträge):\n\n{inhalt}"
    except Exception as e:
        return f"❌ Fehler beim Lesen: {e}"


def whatsapp_kalender_lesen() -> str:
    """
    Liest den WhatsApp-Kalender aus whatsapp_kalender.txt.
    Nutze diesen Skill wenn der User fragt: 'Zeig mir den Kalender' oder
    'Welche Termine habe ich?' oder 'Was steht im WhatsApp-Kalender?'
    """
    eintraege = _kalender_lesen()
    if not eintraege:
        return "📅 Kalender ist leer – noch keine Termine eingetragen."
    return f"📅 WhatsApp-Kalender ({len(eintraege)} Termine):\n\n" + "\n".join(eintraege)


def whatsapp_kalender_eintragen(datum: str, uhrzeit: str,
                                 titel: str, kontakt: str = "manuell") -> str:
    """
    Trägt einen Termin manuell in den WhatsApp-Kalender ein.
    datum:   Format YYYY-MM-DD (z.B. 2026-03-15)
    uhrzeit: Format HH:MM      (z.B. 14:30)
    titel:   Beschreibung des Termins
    kontakt: Wer hat den Termin vereinbart (Standard: 'manuell')
    """
    ok, grund = _kalender_eintrag_hinzufuegen(kontakt, datum, uhrzeit, titel)
    if ok:
        wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                      "Freitag", "Samstag", "Sonntag"]
        try:
            dt = datetime.datetime.strptime(f"{datum} {uhrzeit}", "%Y-%m-%d %H:%M")
            wt = wochentage[dt.weekday()]
        except Exception:
            wt = "?"
        return f"✅ Termin eingetragen:\n📅 {datum} ({wt}) um {uhrzeit} Uhr\n📌 {titel}"
    return f"❌ Termin konnte nicht eingetragen werden: {grund}"


AVAILABLE_SKILLS = [
    whatsapp_autonomer_dialog,
    whatsapp_listener_stoppen,
    whatsapp_listener_status,
    whatsapp_log_lesen,
    whatsapp_nachrichten_lesen,
    whatsapp_kalender_lesen,
    whatsapp_kalender_eintragen,
]
