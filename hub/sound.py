import soundfile as sf
import soundcard as sc


def speaker():
    speakers = sc.all_speakers()
    for s in speakers:
        if 'Simultaneous' in s.name:
            return s
    print('WARN -- choosing default speaker, no "Simultaneous" speaker found')
    return speakers[0]

    
def sound_asset(room, phase):
    """
    room -- from 0 to 5
    phase -- from 0 to 1 
    """

    return './assets/room_0%d_%d.mp3' % (room, phase)


def soundcheck():
    data, sr = sf.read(sound_asset(room=0, phase=0))  # test sound
    speaker().play(data[: sr * 2], sr)  # plays 2 secs
    print('>>> SOUNDCHECK DONE <<<')