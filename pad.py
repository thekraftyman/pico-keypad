# pad.py
import picokeypad as pad
from time import sleep

class Keypad:
    def __init__( self, brightness=1.0, sleep_time=0.0 ):
        '''
        Keypad object for pico keypad

        :arg float brightness: brightness float for pad [0.0 - 1.0]
        :arg float sleep_time: amount of time to sleep between key color updates
        '''
        self.pad = pad
        self.pad.init()
        self.pad.set_brightness( float(brightness) )
        self._brightness = brightness
        self._height = self.pad.get_height()
        self._nkeys = self.pad.get_num_pads()
        self._sleep_time = sleep_time
        self._state = 0
        self._width = self.pad.get_width()

    @property
    def brightness( self ):
        ''' brightness of the keypad (float [0.0 - 1.0] ) '''
        return self._brightness

    @brightness.setter
    def brightness( self, bval ):
        self._brightness = float( bval )
        self.pad.set_brightness( self._brightness )
        self.update()

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
        return bool( self.state )

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
    def sleep_time( self ):
        ''' return current value for sleep time '''
        return self._sleep_time

    @sleep_time.setter
    def sleep_time( self, other ):
        self._sleep_time = float( other )

    @property
    def state( self ):
        ''' current button press state value int '''
        self._state = self.get_button_states()
        return self._state

    def check_key( self, key_num ):
        ''' check to see if a key num can exist '''
        if not self.valid_key( key_num ):
            raise Exception( f"Key {key_num} not in current key range {self.keys}" )

    def get_button_states( self ):
        ''' current button press state value int '''
        return self.pad.get_button_states()

    def set_color( self, key_num, color, update=True):
        '''
        set the value for a given key (0-16) with an rgb value (0-255)
        '''
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        self.pad.illuminate( key_num, r, g, b )
        if update:
            self.update()
        if self.sleep_time:
            sleep( self.sleep_time )

    def update( self ):
        ''' update the pad '''
        self.pad.update()

    def valid_key( self, key_num ):
        '''
        checks to see if a given key number is valid

        :arg int key_num: key int val

        @return bool
        '''
        return int(key_num) in self.keys

