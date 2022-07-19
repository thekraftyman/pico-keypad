# test-2.py

import os
from macro_pad import MacroPad
from time import sleep

def main():
    # init the macro pad
    pad = MacroPad()

    # bind some keys
    pad.bind_key( 0, say_hello, color=[100,0,0] )
    pad.bind_key( 1, say_hello, color=[0,0,100] )

    # add some options
    options = {
        1 : {
            'kwargs' : { 'name' : 'thekraftyman' },
            'held' : False
        }
    }

    # run the loop
    while True:
        # see if any buttons are being pressed
        if not pad.is_pressed:
            sleep( 0.1 )
            continue

        # iterate through pressed buttons
        for button in pad.bound_pressed_buttons:
            if button in options and 'kwargs' in options[button]:
                if 'held' in options[button] and options[button]['held']:
                    pad.call( button, **options[button]['kwargs'] )
                    while button in pad.bound_pressed_buttons:
                        sleep(0.05)
                else:
                    pad.call( button, **options[button]['kwargs'] )
            else:
                pad.call( button )

        # sleep to make sure we don't run the button too many times
        sleep( 0.5 )

def say_hello( name=None ):
    tosay = "Hello"
    if name:
        tosay = tosay + f" {name}"
    tosay = tosay + ", how are you?"
    print( tosay )

if __name__ == "__main__":
    main()
