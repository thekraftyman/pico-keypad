# ducky_engine.py

__author__ = "thekraftyman"
__version__ = "1.1.0"

'''
Ducky engine repo found at:
    https://github.com/thekraftyman/advanced-pico-ducky/blob/main/ducky_engine.py
'''

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode
import supervisor
import time
import digitalio
import pwmio
from board import *
import board

class DuckyEngine:
    ''' used to interpret/run ducky scripts '''

    def __init__( self ):
        self.default_delay = 0
        self.duckyCommands = {
            'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
            'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
            'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
            'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
            'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
            'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
            'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
            'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
            'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
            'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
            'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
            'BACKSPACE': Keycode.BACKSPACE,
            'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
            'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
            'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
            'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
            'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
            'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
            'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
            'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
            'F12': Keycode.F12,
        }
        self.kbd = Keyboard( usb_hid.devices )
        self.layout = KeyboardLayout( self.kbd )

        # init some modules
        supervisor.disable_autoreload()

        # sleep to allow the device to register on the host
        time.sleep(.5)

    def convert_line( self, line ):
        newline = []
        # loop on each key - the filter removes empty values
        for key in filter(None, line.split(" ")):
            # find the keycode
            command_keycode = self.duckyCommands.get( key.upper(), None )
            if command_keycode is not None:
                # if it exists in the list, use it
                newline.append( command_keycode )
            elif hasattr( Keycode, key ):
                # if it's in the Keycode module, use it (allows any valid keycode)
                newline.append( getattr(Keycode, key) )
            else:
                # if it's not a known key name, show the error for diagnosis
                print( f"Unknown key: <{key}>" )
        return newline

    def get_programming_status( self ):
        # check GP0 for setup mode
        # see setup mode for instructions
        progStatusPin = digitalio.DigitalInOut(GP0)
        progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
        return not progStatusPin.value

    def parse_line( self, line ):
        if line[0:3] == "REM":
            pass
        elif line[0:5] == "DELAY":
            time.sleep( float(line[6:])/1000 )
        elif line[0:6] == "STRING":
            self.layout.write( line[7:] )
        elif line[0:5] == "PRINT":
            print( f"[SCRIPT]: {line[6:]}" )
        elif line[0:13] == "DEFAULT_DELAY":
            self.default_delay = int( line[14:] ) * 10
        elif line[0:13] == "DEFAULTDELAY":
            self.default_delay = int( line[13:] ) * 10
        elif line[0:3] == "LED":
            if self.led.value:
                self.led.value = False
            else:
                self.led.value = True
        else:
            new_script_line = self.convert_line( line )
            self.run_line( new_script_line )

    def run_file( self, filename ):
        try:
            with open( filename, "r", encoding="utf-8" ) as infile:
                previous = ""
                for line in infile:
                    line = line.rstrip()
                    if line[0:6] == "REPEAT":
                        for i in range( int(line[7:]) ):
                            # repeat the last command
                            self.parse_line( previous )
                            self.sleep()
                    else:
                        self.parse_line( line )
                        previous = line
                    self.sleep()
        except OSError:
            print("Unable to open file ", file)

    def run_line( self, line ):
        for k in line:
            self.kbd.press( k )
        self.kbd.release_all()

    def run_multiline_string( self, in_str ):
        # parse for each line
        split_lines = in_str.split( "\n" )
        lines = []
        for line in split_lines:
            if line:
                lines.append( line.strip() )

        # run each line
        previous = ""
        for line in lines:
            line = line.rstrip()
            if line[0:6] == "REPEAT":
                for i in range( int(line[7:]) ):
                    # repeat the last command
                    self.parse_line( previous )
                    self.sleep()
            else:
                self.parse_line( line )
                previous = line
            self.sleep()

    def sleep( self ):
        time.sleep( float(self.default_delay) / 1000 )

