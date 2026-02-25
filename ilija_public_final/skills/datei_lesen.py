"""
Liest den Inhalt einer Datei
"""
import random
import time
import math
import datetime
import os

def datei_lesen(pfad): return open(pfad, 'r').read()

AVAILABLE_SKILLS = [datei_lesen]
