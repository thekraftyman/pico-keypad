# pad.py
import adafruit_dotstar
import busio
import board
import digitalio as dio
import time
from adafruit_bus_device.i2c_device import I2CDevice
from random import randint

# --------------
# CONTENTS
# 1. Classes
#   a. Key
#   b. Pad (uses Key)
# 2. Functions
# -------------

# 1. Classes ---------

# 1a.
class Key:
    """
    Represents a key on Keypad, with associated value and
    LED behaviours.
    :param number: the key number (0-15) to associate with the key
    :param mask: the value when pressed (2**key number)
    :param pixels: the dotstar instance for the LEDs
    :param full_state: a list of the keypad full keys state (int)
    """
    def __init__(self, number, mask, pixels, full_state):
        self.mask = mask
        self.number = number
        self.full_state = full_state

        self._state = 0
        self.pressed = 0
        self.last_state = None
        self.time_of_last_press = time.monotonic()
        self.time_since_last_press = None
        self.time_held_for = 0
        self.held = False
        self.hold_time = 0.75
        self.modifier = False
        self.rgb = [0, 0, 0]
        self.lit = False
        self.x, self.y = self.xy
        self.pixels = pixels
        self.led_off()
        self.press_function = None
        self.release_function = None
        self.hold_function = None
        self.press_func_fired = False
        self.hold_func_fired = False
        self.debounce = 0.125
        self.key_locked = False

    @attribute
    def is_modifier( self ):
        '''
        Designates a modifier key, so you can hold the modifier
            and tap another key to trigger additional behaviours.
        '''
        return bool( self.modifier )

    @attribute
    def pressed( self ):
        '''
        returns bool of state
        '''
        return bool( self.state )

    @attribute
    def state( self ):
        # returns the state of a key (0=not pressed, 1=pressed)
        return 0 if self.full_state[0] & self.mask else 1

    @attribute
    def xy( self ):
        '''
        Convert a number to an x/y coordinate.
        '''
        if not self.x:
            self.x = self.number % 4
        if not self.y:
            self.y = self.number // 4
        return self.x,self.y

    def led_off( self ):
        '''
        turn off led
        '''
        self.set_led( 0, 0, 0 )

    def led_on( self ):
        '''
        Turn the LED on, using its current RGB value.
        '''
        r,g,b = self.rgb
        self.set_led( r, g, b )

    def led_state( self, state ):
        '''
        Set the LED's state (0=off, 1=on)
        '''
        if int( state ):
            self.led_on()
        else:
            self.led_off()

    def set_led( self, r, g, b ):
        if not r and not g and not b:
            self.lit = False
        else:
            self.lit = True
            self.rgb = [r,g,b]
        self.pixels[self.number] = (r,g,b)

    def time( self ):
        # record elapsed time
        self.time_since_last_press = time.monotonic() - self.time_of_last_press

    def toggle_led( self, rgb=None ):
        if rgb:
            self.rgb = rgb
        if self.lit:
            self.led_off()
        else:
            self.led_on()

    def update( self ):
        '''
        Updates the state of the key and updates all of its
            attributes.
        '''
        self.time()

        # Keys get locked during the debounce time.
        if self.time_since_last_press < self.debounce:
            self.key_locked = True
        else:
            self.key_locked = False

        self._state = self.get_state()
        update_time = time.monotonic()

        # If there's a `press_function` attached, then call it,
        # returning the key object and the pressed state.
        if self.press_function is not None and self.pressed and not self.press_func_fired and not self.key_locked:
            self.press_function(self)
            self.press_func_fired = True

        # If the key has been pressed and releases, then call
        # the `release_function`, if one is attached.
        if not self.pressed and self.last_state:
            if self.release_function is not None:
                self.release_function(self)
            self.last_state = False
            self.press_func_fired = False

        if not self.pressed:
            self.time_held_for = 0
            self.last_state = False

        # If the key has just been pressed, then record the
        # `time_of_last_press`, and update last_state.
        elif self.pressed and not self.last_state:
            self.time_of_last_press = update_time
            self.last_state = True

        # If the key is pressed and held, then update the
        # `time_held_for` variable.
        elif self.pressed and self.last_state:
            self.time_held_for = update_time - self.time_of_last_press
            self.last_state = True

        # If the `hold_time` threshold is crossed, then call the
        # `hold_function` if one is attached. The `hold_func_fired`
        # ensures that the function is only called once.
        if self.time_held_for > self.hold_time:
            self.held = True
            if self.hold_function is not None and not self.hold_func_fired:
                self.hold_function(self)
                self.hold_func_fired = True
        else:
            self.held = False
            self.hold_func_fired = False

    def __int__( self ):
        # gives the key value
        return self.number

    def __str__(self):
        # When printed, show the key's state (0 or 1).
        return self.state

# 1b.
class Keypad(object):
    def __init__( self, brightness=1.0, sleep_time=0.0, keys=16 ):
        '''
        Keypad object for pico keypad

        :arg float brightness: brightness float for pad [0.0 - 1.0]
        :arg float sleep_time: amount of time to sleep between key color updates
        :arg int pins: number of keys on the board (default 16)
        '''
        # LED on the pico board
        self._board_led = dio.DigitalInOut( board.LED )
        self._board_led.direction = dio.Direction.OUTPUT
        self._board_led.value = False

        # set up vars for keys
        self._full_state = [0]
        self._keys = []
        self._nkeys = keys
        self._pins = [2**i for i in self.keys]

        # set up i2c connection and pixels
        self.pixels = adafruit_dotstar.DotStar( board.GP18, board.GP19, 16, brightness=0.1, auto_write=True )
        self._i2c = busio.I2C( board.GP5, board.GP4 )
        self.expander = I2CDevice( self._i2c, 0x20 )

        # set up some other vars
        self._brightness = brightness
        self._led_sleep_enabled = False
        self._led_sleep_time = 60
        self._time_of_last_press = time.monotonic()
        self._time_since_last_press = None
        self.sleeping = False
        self.was_asleep = False
        self.last_led_states = None

        # set up keys
        for i in range( self._nkeys ):
            self._keys.append( Key( i, self._pins[i], self.pixels, self.full_state ) )

    @property
    def keys( self ):
        ''' list of int values for keys on pad ([1,2,3,4,5...]) '''
        return [ i for i in range( self.nkeys ) ]

    @property
    def nkeys( self ):
        ''' int number of keys on pad '''
        return self._nkeys

    @property
    def pressed( self ):
        on = bool( self.state )
        if on:
            # turn the board LED on
            self._board_led.value = True
        else:
            # turn the board LED off
            self._board_led.value = False
        return on

    @property
    def pressed_buttons( self ):
        '''
        returns a list of int values of currently pressed buttons (starting at 0)

        ex. if the first and third buttons are pressed, then the return val is:
            [0,2]
        '''
        # get the current state as an int
        cur_state = self.state

        # convert the state int to a binary string
        bin_val = "{0:b}".format( cur_state )

        # invert the binary string
        inv_bin = []
        for val in bin_val:
            inv_bin.insert(0, val)
        inv_bin = ''.join(inv_bin)

        # use inverted binary string to find pressed buttons
        return [i for i,n in enumerate(inv_bin) if n == '1']

    @property
    def state( self ):
        ''' current button press state value int '''
        self._state = self.get_button_states()
        return self._state

    def check_key( self, key_num ):
        ''' check to see if a key num can exist '''
        if not self.valid_key( key_num ):
            raise Exception( f"Key {key_num} not in current key range {self.nkeys}" )

    def update( self ):
        '''
        Call this in each iteration of your while loop to update
            to update everything's state, e.g. `keybow.update()`
        '''

        with self.expander:
            self.expander.write(bytes([0x0]))
            result = bytearray(2)
            self.expander.readinto(result)
            self.full_state[0] = result[0] | result[1] << 8

        for key in self._keys:
            key.update()

        # Used to work out the sleep behaviour, by keeping track
        # of the time of the last key press.
        if self.any_pressed():
            self._time_of_last_press = time.monotonic()
            self.sleeping = False

        self._time_since_last_press = time.monotonic() - self._time_of_last_press

        # If LED sleep is enabled, but not engaged, check if enough time
        # has elapsed to engage sleep. If engaged, record the state of the
        # LEDs, so it can be restored on wake.
        if self._led_sleep_enabled and not self.sleeping:
            if time.monotonic() - self._time_of_last_press > self._led_sleep_time:
                self.sleeping = True
                self.last_led_states = [k.rgb if k.lit else [0, 0, 0] for k in self._keys]
                self.set_all(0, 0, 0)
                self.was_asleep = True

        # If it was sleeping, but is no longer, then restore LED states.
        if not self.sleeping and self.was_asleep:
            for k in self.keys:
                self._keys[k].set_led(*self.last_led_states[k])
            self.was_asleep = False

    def valid_key( self, key_num ):
        '''
        checks to see if a given key number is valid

        :arg int key_num: key int val

        @return bool
        '''
        return int(key_num) in self.keys

