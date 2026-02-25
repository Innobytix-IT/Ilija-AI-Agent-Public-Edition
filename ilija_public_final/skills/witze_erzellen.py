
"""
Erzählt Witze und Sprüche aus verschiedenen Kategorien.
"""
import random
import time
import math
import os

import random

def witze_erzellen():
	witze = ['Warum ging der Computer zum Arzt? Weil er ein Virus hatte.', 'Warum ist das Eis so sauer? Weil es den ganzen Tag im Schrank lag.', 'Wieso liegen die Zahlen falsch? Weil sie eine Fehlerquelle waren.'];
	return random.choice(witze);

# Automatische Registrierung
AVAILABLE_SKILLS = [witze_erzellen]
