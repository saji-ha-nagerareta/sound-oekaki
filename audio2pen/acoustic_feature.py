# -*- coding: utf-8 -*-

import numpy as np
import wave
import ffmpeg
import librosa
import subprocess

from audio2pen import fft


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


def _fbank(wav, sample_rate, nfilt=26, high_freq=None, type='mono'):
    frame_len_ms = 100
    frame_step_ms = 50
    frame_len = frame_len_ms * sample_rate // 1000
    frame_step = frame_step_ms * sample_rate // 1000

    magnitude_spec,_,freq = fft.fbank(wav, samplerate=sample_rate, frame_len=frame_len, frame_step=frame_step,
                                      nfilt=nfilt, highfreq=high_freq, type=type)
    power_spec = np.square(magnitude_spec)
    power_spec = np.where(power_spec == 0, np.finfo(float).eps, power_spec)
    power_spec = np.log10(power_spec)

    power_spec = np.mean(power_spec, axis=0)

    return power_spec, freq


def _pitch(wav, sample_rate):
    pitches, mags = librosa.piptrack(y=wav, sr=sample_rate, n_fft=1024, fmin=0)
    pitches = pitches[mags > np.median(mags)]
    mags = mags[mags > np.median(mags)]
    print(np.sort(pitches))
    print(mags[np.argsort(pitches)])

    print(pitches[np.argsort(mags)])
    print(np.sort(mags))

    print(pitches.shape, np.max(pitches), np.min(pitches), np.median(pitches))
    return pitches


def _pitch_reaper(wav_path):
    pitch_path = wav_path.replace('.webm', '.wav')
    cmd = ['reaper', '-i', wav_path, '-f', pitch_path, '-a']
    subprocess.run(cmd)

    pitches =[]
    with open(pitch_path, 'r') as file:
        line = file.readlines()
        for l in line[7:]:
            l = l.strip()
            pitches.append(np.float(l.split(' ')[2]))
    pitches = np.array(pitches)
    pitches = pitches[pitches > 0]
    pitche = np.mean(pitches)
    return pitche


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

    nfilt = 16
    high_freq = 8000
    filter_type = 'mel'
    feat['fbank_spec'], feat['fbank_freq'] = _fbank(wav, sample_rate=fr, nfilt=nfilt, high_freq=high_freq, type=filter_type)

    feat['pitch_reaper'] = _pitch_reaper(wav_path)

    return feat


if __name__ == '__main__':
    print(extract('c2.webm'))