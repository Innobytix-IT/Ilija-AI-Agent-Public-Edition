"""
Öffnet einen Chrome Browser, der offen bleibt.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Wir definieren den driver global, damit er nicht gelöscht wird
driver = None

def browser_oeffnen(url: str):
    global driver
    try:
        # Chrome Optionen: Detach sorgt dafür, dass das Fenster offen bleibt!
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        # Falls du als root arbeitest oder in einem Container:
        # options.add_argument("--no-sandbox") 

        print(f"🚀 Starte Browser für {url}...")
        
        # Initialisiere den Driver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        driver.get(url)
        return f"✅ Browser gestartet und auf {url} navigiert. Das Fenster sollte nun offen sein."
    except Exception as e:
        return f"❌ Fehler beim Browser-Start: {str(e)}"

AVAILABLE_SKILLS = [browser_oeffnen]
