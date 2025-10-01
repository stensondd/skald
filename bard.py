import os
import threading
import vlc
import yt_dlp
import socket
import time
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
instance = vlc.Instance()
player = instance.media_player_new()
player.audio_set_volume(30)

# Generates a custom tile with run-time generated text and custom image via the
# PIL module.
def render_key_image(deck, icon_filename):
    # Create new key image of the correct dimensions, black background.
    key_width, key_height = deck.key_image_format()['size']
    image = Image.open(icon_filename).resize((key_width, key_height)).convert("RGB")
    image_data = PILHelper.to_native_format(deck, image)

    return PILHelper.to_native_format(deck, image)

#STAR WARS LIST
# qMFH8K0dhC8 Taris Apartments (Calm)
# cz2wR2CFtrU Taris Hideout (Calm)
# 1XE5OuJmPuo Dantooine Hideout (Calm)
# Zxp4XNPiYsU Dantooine Outback (Calm)
# GM5NnpFujf0 Citadel Staion (Calm Spooky)
# 01e3zqWkSHQ Jungle Landing (Suspicious Exploration)
# JcS6VezinNg Ravager (Tension Spooky)
# IPT0jXvonyQ Stealing the Shuttle (Action)
# wuGf1_e-btU Mandalorian Honor (Action Duel)
# SsG8vowl8cE Sith Fleet (Tense)
# f089GGNtQYM Infiltration (Tension)
# VhfmLIozp8k Andor (Tension)
# YhkreSzRQts Hyperspace


# Returns styling information for a key based on its position and state.
def get_key_style(deck, key, state):
    # Last button in the example application is the exit button.
    exit_key_index = deck.key_count() - 1
    
    songs = ['qMFH8K0dhC8', 'cz2wR2CFtrU', '1XE5OuJmPuo', 'Zxp4XNPiYsU', 'GM5NnpFujf0','01e3zqWkSHQ', "JcS6VezinNg", 'IPT0jXvonyQ', 'wuGf1_e-btU', "SsG8vowl8cE", "f089GGNtQYM", 'VhfmLIozp8k', 'YhkreSzRQts']

    if key == exit_key_index:
        name = "exit"
        icon = "{}.png".format("Exit")
    else:
        name = ""
        icon = "{}.png".format("Released")
    if key < 13:
        name = songs[key]
        icon = songs[key]+'-MQ.jpg'


    return {
        "name": name,
        "icon": os.path.join(ASSETS_PATH, icon),
    }


# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(deck, key, state)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"])

    # Update requested key with the generated image.
    deck.set_key_image(key, image)


# Prints key state change information, updates rhe key image and performs any
# associated actions when a key is pressed.
def key_change_callback(deck, key, state):
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    # Update the key image based on the new key state.
    update_key_image(deck, key, state)

    # Check if the key is changing to the pressed state.
    if state:
        key_style = get_key_style(deck, key, state)

        # When an exit button is pressed, close the application.
        if key_style["name"] == "exit":
            # Reset deck, clearing all button images.
            deck.reset()

            # Close deck handle, terminating internal worker threads.
            deck.close()
        else:
            play_youtube_audio(key_style["name"])

def play_youtube_audio(url):
    """
    Plays the audio stream of a given YouTube URL.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:  # Handle playlists
            audio_url = info['entries'][0]['url']
        else:
            audio_url = info['url']

    # Initialize VLC player
    media = instance.media_new(audio_url)
    newInstance = vlc.Instance()
    newPlayer = newInstance.media_player_new()
    newPlayer.audio_set_volume(30)
    newPlayer.set_media(media)
    newPlayer.play()
    global player

    while not newPlayer.is_playing():
        time.sleep(.25)
    player.stop()
    player = newPlayer

    # Keep the script running while audio plays
    # You might want to add more sophisticated controls here
    #try:
        #while True:
           #pass # Or add a timer/event listener to stop playback
    #except KeyboardInterrupt:
        #player.stop()

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        deck.open()
        #deck.reset()

        print("Opened '{}' device (serial number: '{}')".format(deck.deck_type(), deck.get_serial_number()))

        # Set initial screen brightness to 30%.
        deck.set_brightness(30)

        # Set initial key images.
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            if t is threading.current_thread():
                continue

            if t.is_alive():
                t.join()