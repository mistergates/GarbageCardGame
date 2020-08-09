import os
from enum import Enum

IMAGE_ASSETS = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'assets', 'images')
SOUND_ASSETS = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'assets', 'sounds')

class Player(Enum):
    player = 'Player'
    computer = 'Computer'

class Views(Enum):
    main_menu = 'MainMenu'
    garbage = 'Garbage'
    rules = 'Rules'

class ImageAssets(Enum):
    # Main title image
    title = os.path.join(IMAGE_ASSETS, 'title.png')

    # Rules
    rules_text = os.path.join(IMAGE_ASSETS, 'rules_text.png')

    # Main menu buttons
    play_btn = os.path.join(IMAGE_ASSETS, 'play.png')
    play_btn_hover = os.path.join(IMAGE_ASSETS, 'play_hover.png')
    rules_btn = os.path.join(IMAGE_ASSETS, 'rules.png')
    rules_btn_hover = os.path.join(IMAGE_ASSETS, 'rules_hover.png')
    quit_btn = os.path.join(IMAGE_ASSETS, 'quit.png')
    quit_btn_hover = os.path.join(IMAGE_ASSETS, 'quit_hover.png')
    restart_btn = os.path.join(IMAGE_ASSETS, 'restart.png')
    restart_btn_hover = os.path.join(IMAGE_ASSETS, 'restart_hover.png')
    new_game_btn = os.path.join(IMAGE_ASSETS, 'new_game.png')
    new_game_btn_hover = os.path.join(IMAGE_ASSETS, 'new_game_hover.png')

    # Computer
    computer_hand = os.path.join(IMAGE_ASSETS, 'hand.png')

    # Cards
    discard_placeholder = os.path.join(IMAGE_ASSETS, 'discard.png')
    pile_placeholder = os.path.join(IMAGE_ASSETS, 'pile_placeholder.png')

    # Game Controls
    audio_down = os.path.join(IMAGE_ASSETS, 'audio_down.png')
    audio_up = os.path.join(IMAGE_ASSETS, 'audio_up.png')
    audio_1 = os.path.join(IMAGE_ASSETS, 'audio_1.png')
    audio_2 = os.path.join(IMAGE_ASSETS, 'audio_2.png')
    audio_3 = os.path.join(IMAGE_ASSETS, 'audio_3.png')

class Sounds(Enum):
    music = os.path.join(SOUND_ASSETS, 'music.mp3')
    draw_card = os.path.join(SOUND_ASSETS, 'draw.mp3')
    play_card = os.path.join(SOUND_ASSETS, 'playcard.mp3')
    shuffle = os.path.join(SOUND_ASSETS, 'shuffle.mp3')
    error = os.path.join(SOUND_ASSETS, 'error.mp3')
    round_over = os.path.join(SOUND_ASSETS, 'cuckoo.mp3')
    menu_select = os.path.join(SOUND_ASSETS, 'menu_select.wav')
