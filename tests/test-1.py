# test-1.py

from time import sleep
from pad_lib import MacroPad
import random

pad = MacroPad()

while True:
    for button in pad.pressed_keys:
        r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        pad.set_color( button, r, g, b )
    sleep(0.3)
