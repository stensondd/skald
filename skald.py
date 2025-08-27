import vlc
import yt_dlp
import socket
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image

HOST = '127.0.0.1'  # Listen on all interfaces
PORT = 8000      # You can change this to any port above 1024
instance = vlc.Instance()
player = instance.media_player_new()
player.audio_set_volume(30)

def key_change_callback(deck, key, state):
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    # Don't try to draw an image on a touch button
    if key >= deck.key_count():
        return

    # Update the key image based on the new key state.
    update_key_image(deck, key, state)

    # Check if the key is changing to the pressed state.
    if state:
        key_style = get_key_style(deck, key, state)

        # When an exit button is pressed, close the application.
        if key_style["name"] == "exit":
            # Use a scoped-with on the deck to ensure we're the only thread
            # using it right now.
            with deck:
                # Reset deck, clearing all button images.
                deck.reset()

                # Close deck handle, terminating internal worker threads.
                deck.close()

def set_playlist():
    # Get a list of all connected Stream Deck devices
    streamdecks = DeviceManager().enumerate()

    print(f"Found {len(streamdecks)} Stream Deck(s).")

    for index, deck in enumerate(streamdecks):
        deck.open()
        deck.reset()

        print(f"Opened StreamDeck {index}: {deck.id()} (Firmware: {deck.get_firmware_version()}, Serial: {deck.get_serial_number()})")

        # Set the brightness of the Stream Deck
        deck.set_brightness(50)

        # Example: Set a specific key image
        #print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

        key_width, key_height = deck.key_image_format()['size']
        image = Image.open("Warhammer.jpg").resize((key_width, key_height)).convert("RGB")
        image_data = PILHelper.to_native_format(deck, image)
        
        update_key_image(deck, 1, False)
        deck.set_key_image(0, image_data)
        deck.set_key_image(1, image_data)
        deck.set_key_callback(key_change_callback)

        deck.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)  # Listen for incoming connections

        print(f"Server listening on {HOST}:{PORT}...")
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                with client_socket:
                    # Replace with your desired YouTube URL
                    print(f"Connected by {client_address}")
                    data = client_socket.recv(1024)  # Receive up to 1024 bytes
                    if data:
                        print(f"Received data: {data.decode('utf-8')}")
                        play_youtube_audio(data.decode('utf-8'))
                    else:
                        print("No data received.")
                    print(f"Closing connection with {client_address}")
                    client_socket.close()
                set_playlist()
            except KeyboardInterrupt:
                break

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
    player.set_media(media)

    # Play the audio
    player.play()

    # Keep the script running while audio plays
    # You might want to add more sophisticated controls here
    #try:
        #while True:
           #pass # Or add a timer/event listener to stop playback
    #except KeyboardInterrupt:
        #player.stop()

if __name__ == "__main__":
    set_playlist()
    start_server()