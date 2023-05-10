import Ice
import csv
import vlc
import time
import sys
import pyglet
import requests
import io
from tempfile import NamedTemporaryFile
import tempfile
from google.cloud import storage
import app
from io import BytesIO
import urllib.request
from pydub import AudioSegment
from pydub.playback import play as pydub_play
Ice.loadSlice("ICEinter.ice")

class MusicServerI(app.MusicServer):
    def __init__(self, bucket_name):
        self.songs = []
        self.library = {}
        self.bucket_name = "songcollection"
        self.vlc_instance = vlc.Instance()
        self.client = storage.Client.from_service_account_json("Key.json")
        self.bucket = self.client.bucket(self.bucket_name)
        self.load_songs_from_bucket()
        print(">> Server started.")

    def load_songs_from_bucket(self):
        blob = self.bucket.get_blob('songCollection.csv')
        if blob is not None:
            content = blob.download_as_text()
            reader = csv.reader(content.split('\n'), delimiter=';')
            for row in reader:
                if len(row) == 3:
                    song = app.Song()
                    song.artist = row[0]
                    song.titre = row[1]
                    song.audio = row[2]
                    self.songs.append(song)

    def upload(self, s, current=None):
        self.songs.append(s)
        self.update_songs_file()
        return True

    def delete(self, titre, current=None):
        for song in self.songs:
            if song.titre == titre:
                self.songs.remove(song)
                self.update_songs_file()
                return True
        return False

    def modify(self, s, current=None):
        for song in self.songs:
            if song.titre == s.titre:
                song.artist = s.artist
                song.audio = s.audio
                self.update_songs_file()
                return True
        return False

    def findByName(self, titre, current=None):
        result = []
        for song in self.songs:
            if song.titre == titre:
                result.append(song)
        return result

    def findByArtist(self, artist, current=None):
        result = []
        for song in self.songs:
            if song.artist == artist:
                result.append(song)
        return result

    def getAll(self, current=None):
        return self.songs

    def update_songs_file(self):
        blob = self.bucket.blob('songCollection.csv')
        content = "artist;titre;audio\n"
        for song in self.songs:
            content += song.artist + ";" + song.titre + ";" + song.audio + "\n"
        blob.upload_from_string(content)

    def play(self, song, current=None):
        media_url = None
        try:
            blob = self.bucket.get_blob('songCollection.csv')
            if blob is not None:
                content = blob.download_as_text()
                reader = csv.reader(content.split('\n'), delimiter=';')
                for row in reader:
                    if row and row[1] == song.titre:
                        media_url = row[2]
                        break
        except Exception as e:
            print(f"Error: {e}")
            return None

        if media_url is None:
            print("Error: No media URL found")
            return None

        print("Playing:", song, media_url)

        
        try:
            # Download the audio content and save it to a temporary file
            audio_content = requests.get(media_url).content
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(audio_content)
                audio_path = f.name

            # Create a new VLC media instance and add the audio file to it
            media = self.vlc_instance.media_new(audio_path)

            # Create a new VLC media player instance and play the media
            player = self.vlc_instance.media_player_new()
            player.set_media(media)
            player.play()

            # Wait for the music to start playing
            time.sleep(0.5)

            # Monitor for user input to stop the music
            while True:
                if input("Enter any input to stop the music: "):
                    player.stop()
                    break

            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
             
    def pause(self, session_id, current=None):
        if session_id in self.library:
            player = self.library[session_id]
            player.pause()
            return True
        else:
            return False

    def stop(self, session_id, current=None):
        if session_id in self.library:
            player = self.library[session_id]
            player.stop()
            del self.library[session_id]
            return True
        else:
            return False

    def resume(self, session_id, current=None):
        if session_id in self.library:
            player = self.library[session_id]
            player.play()
            return True
        else:
            return False



class MusicClientI(app.MusicClient):
    def __init__(self):
        super().__init__()
        self.ping()
    
    def ping(self, current=None):
        print("Ping!")

    def getServer(self, ip, current=None):
        proxy = self.ic.stringToProxy("MusicServer:default -h {} -p 10000".format(ip))
        return app.MusicServerPrx.checkedCast(proxy)
    
with Ice.initialize(sys.argv) as communicator:
	adapter = communicator.createObjectAdapterWithEndpoints("Serveur", "default -p 10000")
	object = MusicServerI("songcollection")
	adapter.add(object, communicator.stringToIdentity("Serveur"))
	adapter.activate()
	
	# asyncio.run(checkClientsEnVie())
	
	communicator.waitForShutdown()

