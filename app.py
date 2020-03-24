import os
import pickle
import random
import urllib
import pydub
import librosa
import youtube_dl
import warnings
import numpy as np

import librosa.display

warnings.filterwarnings('ignore')

def download_song(link, codec='mp3'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': codec
        }],
        'outtmpl': 'songs/%(title)s.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(link, download=False)
        song_location = 'songs/' + video_info.get('title').replace('|', '_') + '.{}'.format(codec)
        if os.path.exists(song_location):
            return video_info
        else:
            return ydl.extract_info(link)

def calculate_beat(song, meter=8):
    y, sr = librosa.load(song)
    #y, index = librosa.effects.trim(y, frame_length=2, hop_length=1)
    end_time = librosa.get_duration(y, sr=sr)

    onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    print('Estimated Tempo:', tempo)

    adjusted_tempo = tempo - random.uniform(1,2)
    adjusted_tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, bpm=adjusted_tempo)
    print('Adjusted Tempo:', adjusted_tempo)

    measures = (len(beat_frames) // meter)
    beat_strengths = onset_env[beat_frames]
    measure_beat_strengths = beat_strengths[:measures * meter].reshape(-1, meter)
    beat_pos_strength = np.sum(measure_beat_strengths, axis=0)
    downbeat_pos = np.argmax(beat_pos_strength)
    full_measure_beats = beat_frames[:measures * meter].reshape(-1, meter)
    downbeat_frames = full_measure_beats[:, downbeat_pos]

    #print('Downbeat frames: {}'.format(downbeat_frames))
    downbeat_times = librosa.frames_to_time(downbeat_frames, sr=sr)
    #downbeat_times = downbeat_times + downbeat_times[0]
    downbeat_times = np.insert(downbeat_times, 0, 0)
    downbeat_times = np.append(downbeat_times, [end_time])
    print('Downbeat times in s: {}'.format(downbeat_times))

    return downbeat_times

def trim_song(song_file, timestamp=None, length=60):
    fade_duration = 1250
    
    beat_times = calculate_beat(song_file)

    if timestamp != None:
        start_cut = min(beat_times, key=lambda x:abs(x-timestamp))
        end_cut = min(beat_times, key=lambda x:abs(x-(start_cut+length)))
    else:
        valid_beat_times = [i for i in beat_times if i < (beat_times[-2]-length)]
        start_cut = random.choice(valid_beat_times)
        end_cut = min(beat_times, key=lambda x:abs(x-(start_cut+length)))

    print(start_cut, end_cut)
        
    song = pydub.AudioSegment.from_file(song_file, format='mp3')
    trimmed_song = song[start_cut*999:end_cut*999].fade_in(500).fade_out(fade_duration)

    if song_file == 'songs/My Hero Academia – Opening Theme – The Day.mp3':
        trimmed_song += 12

    return trimmed_song

def load_pydub(song):
    info = download_song(song, codec)
    filename = 'songs/' + info.get('title').replace('|', '_') + '.mp3'
    return pydub.AudioSegment.from_file(filename, format='mp3')

def load_librosa(song, codec='mp3'):
    info = download_song(song, codec)
    filename = 'songs/' + info.get('title').replace('|', '_') + '.{}'.format(codec)
    return librosa.load(filename)

def generate_power_hour(song_list, transitions, intro=None, intro_length=120):
    if intro:
        info = download_song(intro)
        filename = 'songs/' + info.get('title').replace('|', '_') + '.mp3'
        mix = trim_song(filename, timestamp=0, length=intro_length)
    else:
        mix = pydub.AudioSegment.empty()
        
    horn = pydub.AudioSegment.from_file(transitions[0], format='mp3') + 6

    for song in song_list:
        info = download_song(song)
        filename = 'songs/' + info.get('title').replace('|', '_').replace(':', ' -').replace('?', '').replace('/', '_') + '.mp3'
        query_string = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(song).query))
        print(query_string)
        timestamp = int(query_string.get('t')) if query_string.get('t') != None else None
        cut_song = trim_song(filename, timestamp=timestamp)

        if len(mix) == 0:
            mix += cut_song
        else:
            mix = mix.overlay(horn[0:len(horn)/2], position=len(mix)-len(horn)/2) + cut_song.overlay(horn[len(horn)/2:len(horn)])
    return mix

def main():
    f = open('fixed.txt', 'r')
    song_list = f.read().splitlines()
    '''
    randomized_song_list = song_list[1:]
    random.shuffle(randomized_song_list)
    randomized_song_list.insert(0, song_list[0])
    '''

    intro_song = 'https://www.youtube.com/watch?v=S9wP5rCTrko'
    power_hour = generate_power_hour(song_list, ['transitions/airhorn.mp3'], intro=intro_song)

    horn = pydub.AudioSegment.from_file('transitions/airhorn.mp3', format='mp3') + 6
    end_song = pydub.AudioSegment.from_file('songs/enddave.mp3', format='mp3')
    power_hour = power_hour.overlay(horn[0:len(horn)/2], position=len(power_hour)-len(horn)/2) + end_song.overlay(horn[len(horn)/2:len(horn)])
    power_hour.export("power_hour_enddave2.mp3", format='mp3')

    #download_song('https://www.youtube.com/watch?v=K3hBMy6BbOo')
    

if __name__ == '__main__':
    main()