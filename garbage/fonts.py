import os

ASSETS_LOC = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'assets', 'fonts')
FONTS = ['OpenSans']
FONT_STYLES = [
    'Regular',
    'Light',
    'SemiBold',
    'Bold',
    'ExtraBold'
]


def get_font(font=FONTS[0], style=FONT_STYLES[0]):
    return os.path.join(ASSETS_LOC, f'{font}-{style}.ttf')
