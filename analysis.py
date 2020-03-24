 '''
    y, sr = load_librosa('https://www.youtube.com/watch?v=nPoi1_in3tk', codec='wav')
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    R = librosa.segment.recurrence_matrix(mfcc, mode='affinity')

    import matplotlib.pyplot as plt
    plt.figure()
    librosa.display.specshow(R, x_axis='time', y_axis='time')
    plt.title('Binary recurrence (symmetric)')
    plt.savefig('r.png')
    '''


    '''
    D = librosa.stft(y)
    H, P = librosa.decompose.hpss(D, margin=3)
    print('Harmonics', H)
    print('Precussion', P)

    import matplotlib.pyplot as plt
    plt.figure()
    plt.subplot(3, 1, 1)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(D), ref=np.max), y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Full power spectrogram')

    plt.subplot(3, 1, 2)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(H), ref=np.max), y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Harmonic power spectrogram')

    plt.subplot(3, 1, 3)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(P), ref=np.max), y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Percussive power spectrogram')

    plt.tight_layout()
    plt.savefig('spectogram.png')
    '''

        fout = open('power_hour.txt', 'w')
    import json
    song_list = json.loads(f.read())
    for item in song_list.get('items'):
        video_url = 'https://www.youtube.com/watch?v={}'.format(item.get('snippet', {}).get('resourceId', {}).get('videoId'))
        print(video_url)
        fout.write('{}\n'.format(video_url))
