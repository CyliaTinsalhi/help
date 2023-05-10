import requests
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

url = "https://storage.googleapis.com/songcollection/musicS/audio1.mp3"
response = requests.get(url)

if response.status_code == 200:
    audio_data = BytesIO(response.content)
    audio_segment = AudioSegment.from_file(audio_data, format="mp3")
    play(audio_segment)
else:
    print(f"Error: Failed to download media file: {response.status_code} {response.reason}")
