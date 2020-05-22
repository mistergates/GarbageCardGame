'''
Button image assets obtained from Kenney.nl:
www.kenney.nl
'''
import os

ASSETS_LOC = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'assets', 'buttons')
BUTTON_DIMENSIONS = (190, 45)
BUTTON_COLORS = ['blue', 'green', 'grey', 'red', 'yellow']
BUTTON_VERSIONS = ['00', '01', '02', '03', '04', '05']

def get_button(color, version='00'):
    return os.path.join(ASSETS_LOC, f'{color}_button{version}.png')
