"""
Fragt das aktuelle Wetter für Offenburg von wetter.com ab und gibt Temperatur und Beschreibung zurück.

Auto-generiert durch skill_erstellen
Skill-Name: wetter_offenburg_abfragen
"""

# Standard-Imports für Skills
import random
import time
import math
import datetime
import os
import subprocess
import json
from typing import Optional, List, Dict, Any

# Haupt-Skill-Code
import re

def wetter_offenburg_abfragen():
    url = "https://www.wetter.com/deutschland/offenburg/DE0007802.html"
    try:
        html_content = webseiten_inhalt_lesen(url) # Nutzt den Skill webseiten_inhalt_lesen
        if not html_content:
            return "Konnte den Inhalt der Wetterseite nicht abrufen. Möglicherweise ist die URL falsch oder die Seite nicht erreichbar."

        temperatur = "nicht gefunden"
        beschreibung = "nicht gefunden"

        # Versuche, die aktuelle Temperatur zu extrahieren (Beispiel wetter.com Struktur)
        temp_match = re.search(r'<span class="temperature">([^<]+)</span>', html_content)
        if temp_match:
            temperatur = temp_match.group(1).strip()

        # Versuche, die Wetterbeschreibung zu extrahieren (Beispiel wetter.com Struktur)
        desc_match = re.search(r'<span class="weather-text">([^<]+)</span>', html_content)
        if desc_match:
            beschreibung = desc_match.group(1).strip()

        if temperatur != "nicht gefunden" and beschreibung != "nicht gefunden":
            return f"Das aktuelle Wetter in Offenburg: {temperatur}, {beschreibung}."
        elif temperatur != "nicht gefunden":
            return f"Das aktuelle Wetter in Offenburg: {temperatur}. Eine detaillierte Beschreibung konnte nicht extrahiert werden."
        elif beschreibung != "nicht gefunden":
            return f"Das aktuelle Wetter in Offenburg: {beschreibung}. Die Temperatur konnte nicht extrahiert werden."
        else:
            # Fallback, wenn keine der spezifischen Informationen gefunden wurde
            return "Konnte die Wetterinformationen für Offenburg nicht extrahieren. Die Struktur der Webseite könnte sich geändert haben oder die Muster sind nicht mehr gültig."

    except Exception as e:
        return f"Ein unerwarteter Fehler ist beim Abrufen des Wetters aufgetreten: {e}"


# Registrierung für den SkillManager
AVAILABLE_SKILLS = [wetter_offenburg_abfragen]
