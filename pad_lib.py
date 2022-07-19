# pad_lib.py

__author__ = "thekraftyman"

import adafruit_dotstar
import board
import busio
import digitalio as dio
from adafruit_bus_device.i2c_device import I2CDevice

# --------------
# CONTENTS
# 1. Classes
#   a. LED
#   b. Key (uses LED)
#   c. Pad (uses Key)
#   d. MacroPad (uses Pad)
# 2. Functions
# --------------

# 1. Classes ---

# 1a.
class LED:
    '''
    LED object
    '''
    def __init__( self, number, pixel_array ):
        '''
        :param int array_number: number in the dotstar array that corresponds to the key's led
        :param DotStar pixel_array: adafruit dotstar pixel array
        '''
        self._number = number
        self._pixel_array = pixel_array
        self._value = None
        self._lit = False

    def set( self, r, g, b ):
        '''
        set the led to a given rgb value
        '''
        # save the value if not all 0s
        if r and g and b:
            self._value = [r,g,b]

        # set the led
        self._pixel_array[ self._number ] = (r,g,b)

    def on( self ):
        '''
        turn the led on to the last value, (255,255,255 if no last value)
        '''
        if self._value:
            value = [255,255,255]
        else:
            value = self._value

        self.set( value[0], value[1], value[2] )
        self._lit = True

    def off( self ):
        '''
        turn the led off
        '''
        self.set( 0, 0, 0 )
        self._lit = False


# 1b. Key
class Key:

    def __init__( self, number, pixel_array, expander, rgb=[10,10,10] ):
        '''
        Represents a key on the keypad. Has an LED
        :param int number: the key number
        :param DotStar pixel_array: adafruit dotstar pixel array
        :param list rgb: 3 value list of rgb values for the key's LED
        '''
        # set given vars
        self._number = number
        self._pixel_array = pixel_array
        self._rgb = rgb
        self._expander = expander

        # set other vars
        self.led = LED( number, pixel_array )

        # turn on the led
        self.led.set( rgb[0], rgb[1], rgb[2] )

    @property
    def is_pressed( self ):
        '''
        return true if key is pressed else return false
        IMPORTANT: KEYPAD NUMBERS START AT 0
        '''
        return bool( self.keypad_state[ self._number ] )

    @property
    def keypad_state( self ):
        '''
        uses the expander and finds the state of the keypad and its presses. Returns
          a list of all key states (0 if not pressed, 1 if pressed).
          for example, if the 2nd button is pressed out of 16 buttons, then the return
          value would be

            [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]
        '''

        # get data from i2c expander
        with self._expander as expander:
            expander.write( bytes([0x0]) )
            result = bytearray(2)
            expander.readinto( result )

        # get the inverted state
        inverted_state = result[0] | result[1] << 8
        inverted_state = "{0:b}".format( inverted_state )

        # invert the inverted state, giving the desired state format
        state = []
        for val in inverted_state:
            state_value = '0' if val=='1' else '1'
            state.insert(0, state_value)

        # return the state
        return state

    @property
    def state( self ):
        return self.keypad_state[self._number]

    def __int__( self ):
        return self._number


# 1c.
class Pad:
    '''
    pico keypad instance
    '''

    def __init__( self, nkeys=16 ):
        '''
        :param int nkeys: number of keys on the pad
        '''

        # set up the board led
        self._board_led = dio.DigitalInOut( board.GP17 )
        self._board_led.direction = dio.Direction.OUTPUT
        self._board_led.value = 0

        # create the i2c device
        self._i2c = busio.I2C( board.GP5, board.GP4 )
        self._expander = I2CDevice( self._i2c, 0x20 )

        # create the dotstar pixel array
        self._pixel_array = adafruit_dotstar.DotStar( board.GP18, board.GP19, nkeys, brightness=0.1, auto_write=True )

        # create the keys
        self._nkeys = nkeys
        self._keys = []
        for i in range( nkeys ):
            k = Key( i, self._pixel_array, self._expander )
            self._keys.append( k )

    @property
    def is_pressed( self ):
        state = self.state
        state = [ int(i) for i in state ]
        if any( state ):
            self._board_led_on()
            return True
        else:
            self._board_led_off()
            return False

    @property
    def keys( self ):
        return self._keys

    @property
    def pressed_keys( self ):
        cur_state = self.state
        return [i for i,n in enumerate(''.join(cur_state)) if n=="1"]

    @property
    def state( self ):
        return self._keys[0].keypad_state

    def _board_led_off( self ):
        self._board_led = False

    def _board_led_on( self ):
        self._board_led = True

    def check_key( self, key_num ):
        '''
        check to see if a key num can exist, raise error if not
        '''
        if not self.valid_key( key_num ):
            raise Exception( f"Key {key_num} not in current key range {range(self._nkeys)}" )

    def set_color( self, key_num, r, g, b ):
        '''
        set the rgb value of a key
        '''
        key_num = int( key_num )
        self.check_key( key_num )
        self.keys[ key_num ].led.set( r, g, b )

    def valid_key( self, key_num ):
        '''
        check to see if a given key number is valid
        :arg int key_num: key int value
        @return bool
        '''
        return int(key_num) in range( self._nkeys )


# 1d.
class MacroPad( Pad ):
    '''
    Macro Pad instance
    '''
    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self._bindings = {}

    @property
    def bindings( self ):
        '''
        dictionary where key bindings are defined
        '''
        return self._bindings

    @property
    def bound_pressed_buttons( self ):
        '''
        returns a list of buttons that are both pressed and bound to something
        '''
        bound_pressed = []
        for key_num in self.pressed_keys:
            if key_num in self._bindings:
                bound_pressed.append( key_num )

        return bound_pressed

    def bind_key( self, key_num, callback, color=None ):
        '''
        Binds a callback function to a key to run when the key is pressed

        :arg int key_num: key int val to bind
        :arg FunctionType callback: function to call when the key is pressed
        :arg list color: a list with 3 integers denoting the color of the button
            [r,g,b] from [0-255]
        '''
        # do some error checking
        key_num = int( key_num )
        self.check_key( key_num )
        if key_num in self._bindings:
            raise Exception( f"Key {key_num} is already bound to a function. Use the `drop_key` function to release the binding before rebinding the key" )

        # bind the key
        self._bindings[ key_num ] = callback

        # set the color
        if color:
            self.keys[ key_num ].led.set( color[0], color[1], color[2] )

    def call( self, key_num, **kwargs ):
        '''
        Call a function from the bindings

        :arg int key_num: key int val to call
        '''
        # do some error checking
        key_num = int( key_num )
        self.check_key( key_num )

        # run the function
        self._bindings[ key_num ]( **kwargs )

    def drop_key( self, key_num ):
        '''
        remove the binding on a given key

        :arg int key_num: key int val to drop from bindings
        '''
        # do some error checking
        key_num = int( key_num )
        if key_num not in self._bindings:
            return

        if self.valid_key( key_num ):
            func = self._bindings.pop( key_num )

    def is_bound( self, key_num ):
        '''
        checks to see if a key is bound

        :arg int key_num: key int value to check for binding
        @return bool
        '''
        return int(key_num) in self._bindings

