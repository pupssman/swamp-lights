import time
import queue
import threading
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


class Player():
    """
    home-brewn custom continuous player
    plays given track in a loop
    when new track is given -- plays it instead
    assumes samplerate is 44100 just for ease of use
    """
    def __init__(self, speaker):
        self.speaker = speaker
        self.track = None
        self.samplerate = None
        self._queue = queue.Queue()
        self._thread = None
        self._lock = threading.RLock()
        self._player = None  # the speaker's player
        self._pos = 0  # offset in track
        self._chunk = .1  # seconds, for later tuning

        self.start()

    def _run(self):
        while True:
            try:
                try:
                    next_t = self._queue.get_nowait()
                    if next:
                        print('>>> changing to new track')
                        self.track, self.samplerate = next_t
                        self._pos = 0
                except queue.Empty:
                    pass  # no big deal

                if self.track is not None:
                    if not self._player:
                        # prepare the player, it should be exited and destroyed outside
                        self._player = self.speaker.player(self.samplerate)
                        self._player.__enter__()  # so we can start pushing data there

                    # take chunk of data
                    step = int(self.samplerate * self._chunk)
                    data_chunk = self.track[self._pos: self._pos + step]
                    self._player.play(data_chunk)  # dont wait here, we sleep outside

                    # move the _pos so we don overrun track)
                    self._pos += step
                    if self._pos > len(self.track):
                        self._pos -= len(self.track)
                else:
                    time.sleep(.1)  # nothing to play yet, wait for next queue read
            except Exception as e:
                print('OUCH in player: %s' % e)
                time.sleep(self._chunk)

    def start(self):
        """
        starts the playback thread
        """
        self._thread = threading.Thread(target=self._run, name='Player')
        self._thread.start()

    def set_track(self, track, samplerate):
        """
        :param track: stereo track
        """
        print(f'>>> in lock a')
        self._queue.put((track, samplerate))
        print(f'>>> in lock a done')

    def set_room_track(self, room, phase):
        print(f'>>> Changing track to room {room} phase {phase}')
        track, samplerate = sf.read(sound_asset(room=room, phase=phase))
        self.set_track(track, samplerate)

PLAYER = Player(speaker())  # prepare the default player

def soundcheck():
    data, sr = sf.read(sound_asset(room=0, phase=0))  # test sound
    speaker().play(data[: sr * 2], sr)  # plays 2 secs
    print('>>> SOUNDCHECK DONE <<<')
