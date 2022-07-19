# test-3.py

from ducky_engine import DuckyEngine
from pad_lib import MacroPad
from time import sleep

def main():
    # create pad and ducky engine
    pad = MacroPad()
    de = DuckyEngine()

    # define keys
    ## Key 0
    ks_0 = """
    DELAY 50
    STRING  (PDF)
    """
    kc_0 = [0, 255, 0]
    ## Key 1
    ks_1 = """
    DELAY 50
    ALT SPACE
    DELAY 100
    STRING Spotify
    DELAY 100
    ENTER
    DELAY 100
    GUI L
    """
    kc_1 = [255, 0, 0]

    # bind the keys with the scripts & colors
    pad.bind_key( 0, de.run_multiline_string, color=kc_0 )
    pad.bind_key( 1, de.run_multiline_string, color=kc_1 )

    # add options
    options = {
        0 : {
            'kwargs' : { 'in_str' : ks_0 },
        },
        1 : {
            'kwargs' : { 'in_str' : ks_1 },
        }
    }

    # run the loop
    while True:
        if not pad.is_pressed:
            sleep( 0.1 )
            continue
        for button in pad.bound_pressed_buttons:
            pad.call( button, **options[button]['kwargs'] )
        sleep(0.5)

if __name__ == "__main__":
    main()

