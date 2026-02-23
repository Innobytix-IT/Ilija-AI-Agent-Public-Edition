"""
whatsapp_autonomer_dialog.py – WhatsApp-Skill für Ilija Public Edition

HINWEIS: Diese Datei direkt aus Ilija EVO übernehmen:
    ilija-AI-Agent/Ilija_evo2_full/skills/whatsapp_autonomer_dialog.py

Der WhatsApp-Skill ist bereits by-design sicher (isolierter Dialog-Loop,
kein Zugriff auf Kernel oder Skill-Erstellung).

──────────────────────────────────────────────────────────────────
PLATZHALTER – bitte durch echte Datei aus EVO ersetzen!
──────────────────────────────────────────────────────────────────
"""


def whatsapp_starten(kontakt: str = "alle") -> str:
    """
    Startet den WhatsApp-Listener für einen Kontakt oder alle Chats.
    Beispiel: whatsapp_starten(kontakt="Max Mustermann")
    Benötigt: Google Chrome + WhatsApp Web einmalig eingeloggt.
    """
    return (
        "⚠️ WhatsApp-Skill noch nicht eingerichtet.\n"
        "Kopiere 'whatsapp_autonomer_dialog.py' aus Ilija EVO in diesen skills/-Ordner\n"
        "und lade die Skills neu (reload)."
    )


def whatsapp_kalender_anzeigen() -> str:
    """Zeigt alle geplanten WhatsApp-Termine aus dem Kalender an."""
    import os
    kalender_pfad = os.path.join("data", "whatsapp_kalender.txt")
    if not os.path.exists(kalender_pfad):
        return "📅 Kein WhatsApp-Kalender vorhanden."
    try:
        with open(kalender_pfad, "r", encoding="utf-8") as f:
            inhalt = f.read().strip()
        return f"📅 WhatsApp-Kalender:\n\n{inhalt}" if inhalt else "📅 Kalender ist leer."
    except Exception as e:
        return f"❌ Fehler: {e}"


def whatsapp_nachrichten_abrufen() -> str:
    """Ruft hinterlassene WhatsApp-Nachrichten ab."""
    import os
    log_pfad = os.path.join("data", "whatsapp_log.txt")
    if not os.path.exists(log_pfad):
        return "💬 Keine hinterlassenen WhatsApp-Nachrichten."
    try:
        with open(log_pfad, "r", encoding="utf-8") as f:
            inhalt = f.read().strip()
        return f"💬 Hinterlassene Nachrichten:\n\n{inhalt}" if inhalt else "💬 Keine neuen Nachrichten."
    except Exception as e:
        return f"❌ Fehler: {e}"


AVAILABLE_SKILLS = [
    whatsapp_starten,
    whatsapp_kalender_anzeigen,
    whatsapp_nachrichten_abrufen,
]
