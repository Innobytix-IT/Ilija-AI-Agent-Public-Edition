"""
webseiten_inhalt_lesen.py – Webseiten lesen & Internetrecherche für Ilija Public Edition
"""

import re
import requests
from urllib.parse import quote_plus


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 12


def webseite_lesen(url: str) -> str:
    """
    Liest den Textinhalt einer Webseite.
    Beispiel: webseite_lesen(url="https://example.com")
    """
    try:
        r    = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        r.encoding = "utf-8"

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")

        # Störende Elemente entfernen
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        # Leerzeilen reduzieren
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text[:8000] if len(text) > 8000 else text
    except Exception as e:
        return f"❌ Fehler beim Laden von {url}: {e}"


def internet_suche(suchanfrage: str, max_ergebnisse: int = 5) -> str:
    """
    Führt eine Internetsuche durch und gibt die Top-Ergebnisse zurück.
    Nutzt DuckDuckGo (kein API-Key nötig).
    Beispiel: internet_suche(suchanfrage="Wetter München heute")
    """
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(suchanfrage)}"
        r   = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()

        from bs4 import BeautifulSoup
        soup    = BeautifulSoup(r.text, "lxml")
        results = soup.find_all("div", class_="result", limit=max_ergebnisse)

        if not results:
            return f"🔍 Keine Ergebnisse gefunden für: '{suchanfrage}'"

        output = [f"🔍 Suchergebnisse für: '{suchanfrage}'\n"]
        for i, result in enumerate(results, 1):
            title_tag = result.find("a", class_="result__a")
            snip_tag  = result.find("a", class_="result__snippet")
            title     = title_tag.get_text(strip=True) if title_tag else "Kein Titel"
            snip      = snip_tag.get_text(strip=True)  if snip_tag  else ""
            href      = title_tag.get("href", "")       if title_tag else ""
            output.append(f"{i}. **{title}**\n   {snip}\n   {href}")

        return "\n\n".join(output)
    except Exception as e:
        return f"❌ Suche fehlgeschlagen: {e}"


def news_abrufen(thema: str = "Deutschland") -> str:
    """
    Ruft aktuelle Nachrichten zu einem Thema ab.
    Beispiel: news_abrufen(thema="Technologie")
    """
    return internet_suche(f"{thema} aktuell news heute", max_ergebnisse=6)


def wikipedia_suche(suchbegriff: str, sprache: str = "de") -> str:
    """
    Sucht einen Begriff auf Wikipedia und gibt eine Zusammenfassung zurück.
    Beispiel: wikipedia_suche(suchbegriff="Künstliche Intelligenz")
    """
    try:
        api_url = (
            f"https://{sprache}.wikipedia.org/api/rest_v1/page/summary/"
            f"{quote_plus(suchbegriff)}"
        )
        r = requests.get(api_url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()

        titel   = data.get("title", suchbegriff)
        extract = data.get("extract", "Keine Zusammenfassung verfügbar.")
        url     = data.get("content_urls", {}).get("desktop", {}).get("page", "")

        return (
            f"📖 **{titel}** (Wikipedia)\n\n"
            f"{extract[:2000]}"
            + (f"\n\n🔗 {url}" if url else "")
        )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"❌ '{suchbegriff}' nicht auf Wikipedia gefunden."
        return f"❌ Wikipedia-Fehler: {e}"
    except Exception as e:
        return f"❌ Fehler: {e}"


AVAILABLE_SKILLS = [
    webseite_lesen,
    internet_suche,
    news_abrufen,
    wikipedia_suche,
]
