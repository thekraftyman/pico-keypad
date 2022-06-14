# pad_lib.py
import picokeypad as pad

class Keypad:
    def __init__( self, brightness=1.0 ):
        self.pad = pad
        self.pad.init()
        self.pad.set_brightness( float(brightness) )
        self._brightness = brightness
        self._width = self.pad.get_width()
        self._height = self.pad.get_height()
        self._last_state = 0
        self._state = 0
    
    @property
    def brightness( self ):
        return self._brightness
    
    @brightness.setter
    def brightness( self, bval ):
        self._brightness = float( bval )
        self.pad.set_brightness( self._brightness )
        self.update()
    
    @property
    def state( self ):
        self._state = self.get_button_states()
        return self._state
    
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
    
    def get_button_states( self ):
        return self.pad.get_button_states()
        
    def set_color( self, key_num, r=0, g=0, b=0, update=True):
        '''
        set the value for a given key (0-16) with an rgb value (0-255)
        '''
        r, g, b = int(r), int(g), int(b)
        self.pad.illuminate( key_num, r, g, b )
        if update:
            self.update()
        
    def update( self ):
        ''' update the pad '''
        self.pad.update()