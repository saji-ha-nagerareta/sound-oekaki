# -*- coding: utf-8 -*-

import numpy as np
import wave
import ffmpeg
import fft

def _db(wav):
    db = wav ** 2.0
    db = np.mean(db)
    db = np.sqrt(db)
    db = 20 * np.log10(np.maximum(db, np.finfo(np.float).eps) / np.iinfo(np.int16).max)

    return db


def _spectrum(wav, sample_rate):
    frame_len_ms = 100
    frame_step_ms = 50
    frame_len = frame_len_ms * sample_rate // 1000
    frame_step = frame_step_ms * sample_rate // 1000

    freq = np.fft.rfftfreq(frame_len, d=1./sample_rate)
    magnitude_spec,_ = fft.stft(wav, frame_len=frame_len, frame_step=frame_step)
    power_spec = np.square(magnitude_spec)
    power_spec = np.where(power_spec == 0, np.finfo(float).eps, power_spec)
    power_spec = np.log10(power_spec)

    power_spec = np.mean(power_spec, axis=0)

    pitch = freq[np.argmax(power_spec)]

    return power_spec, freq, pitch


def _read_wave(path):
    with wave.open(str(path), mode='rb') as wif:
        # params = (nchannels, sampwidth, framerate, nframes, comptype, compname)
        params = wif.getparams()
        data = wif.readframes(params.nframes)

    data = np.frombuffer(data, np.int16)
    nframes = len(data) // params.nchannels
    wav = data.reshape(nframes, params.nchannels).T

    return wav, params.framerate


def extract(webm_path):
    wav_path = webm_path.replace('.webm', '.wav')
    stream = ffmpeg.input(webm_path)
    stream = ffmpeg.output(stream, wav_path)
    ffmpeg.run(stream)

    wav, fr = _read_wave(wav_path)
    wav = wav[0]

    feat = dict()
    feat['db'] = _db(wav)
    feat['power_spec'], feat['freq'], feat['pitch'] = _spectrum(wav, fr)

    return feat


if __name__ == '__main__':
    # stream = ffmpeg.input('big-buck-bunny_trailer.webm')
    # stream = ffmpeg.output(stream, 'big-buck-bunny_trailer.wav')
    # ffmpeg.run(stream)

    # audio = sonar.io.audio.read('big-buck-bunny_trailer.wav')
    # audio = sonar.io.audio.read('c.wav')
    # wav = audio[0]
    # print(_db(wav))
    # print("def", audio.rms_dbfs)
    # print(_sound_section(audio))
    # print(_spectrum(wav, audio.framerate))

    result = extract('c.webm')
    print(result)
    
    f = open("feature.txt", "wt")
    f.write(str(result))
    f.close()