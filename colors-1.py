# colors-1.py

from time import sleep
from pad_lib import Keypad
import random

pad = Keypad()

while True:
    for button in pad.pressed_buttons:
        r, g, b = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        pad.set_color( button, r=r, g=g, b=b )
    sleep(0.1)