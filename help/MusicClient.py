import Ice
import app
import vlc
import time

def print_song(song):
    print(song.artist, song.titre, song.audio)

def print_song_list(songs):
    if not songs:
        print("No songs found.")
    else:
        print("Found {} song(s):".format(len(songs)))
        for song in songs:
            print_song(song)

def play_song(song):
    instance = vlc.Instance('--no-xlib')
    media = instance.media_new(song.audio)
    player = instance.media_player_new()
    player.set_media(media)
    player.play()
    session_id = str(int(time.time()))
    return session_id, player

def stop_song(session_id, library):
    if session_id in library:
        player = library[session_id]
        player.stop()
        del library[session_id]

def resume_song(session_id, library):
    if session_id in library:
        player = library[session_id]
        player.play()

with Ice.initialize() as ic:
    # Replace "SERVER_IP" with the actual IP address of the server
    proxy = ic.stringToProxy("Serveur:default -h 127.0.0.1 -p 10000")
    music_server = app.MusicServerPrx.checkedCast(proxy)
    if not music_server:
        raise RuntimeError("Invalid proxy")

    identity = proxy.ice_getIdentity()
    print("Connected to server at {}:{}".format(identity.name, identity.category))

    library = {}

    while True:
        print("Available functions:")
        print("1. getAll")
        print("2. findByName")
        print("3. findByArtist")
        print("4. upload")
        print("5. modify")
        print("6. delete")
        print("7. play")
        print("8. stop")
        print("9. resume")
        print("0. Quit")

        try:
            choice = int(input("Choose a function to call: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if choice == 0:
            break

        elif choice == 1:
            songs = music_server.getAll()
            print_song_list(songs)

        elif choice == 2:
            name = input("Enter the song name: ")
            songs = music_server.findByName(name)
            print_song_list(songs)

        elif choice == 3:
            artist = input("Enter the artist name: ")
            songs = music_server.findByArtist(artist)
            print_song_list(songs)

        elif choice == 4:
            song = app.Song()
            song.titre = input("Enter the song title: ")
            song.artist = input("Enter the artist name: ")
            song.audio = input("Enter the audio file path: ")
            success = music_server.upload(song)
            if success:
                print("Song uploaded successfully.")
            else:
                print("Upload failed.")

        elif choice == 5:
            song = app.Song()
            song.titre = input("Enter the song title: ")
            song.artist = input("Enter the artist name: ")
            song.audio = input("Enter the audio file path: ")
            success = music_server.modify(song)
            if success:
                print("Song modified successfully.")
            else:
                print("Modification failed.")

        elif choice == 6:
            titre = input("Enter the song title: ")
            success = music_server.delete(titre)
            if success:
                print("Song deleted successfully.")
            else:
                print("Deletion failed.")

        elif choice == 7:
            song = app.Song()
            song.titre = input("Enter the song title to play: ")
            success = music_server.play(song)
            if success:
                print("Song played successfully.")
            else:
                print("Playback failed.")
    
        elif choice == 8:
            titre = input("Enter the song title to stop: ")
            success = music_server.stop(titre)
            if success:
                print("Playback stopped successfully.")
            else:
                print("Stop failed.")
        
        elif choice == 9:
            titre = input("Enter the song title to resume: ")
            success = music_server.resume(titre)
            if success:
                print("Playback resumed successfully.")
            else:
                print("Resume failed.")

        else:
            print("Invalid choice. Please enter a number between 0 and 6.")
