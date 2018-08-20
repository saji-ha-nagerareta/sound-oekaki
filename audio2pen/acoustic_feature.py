# -*- coding: utf-8 -*-

import numpy as np
import wave
import ffmpeg
import librosa
import subprocess
import os

import fft
import vad


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


def _pitch_librosa(wav, sample_rate):
    pitches, mags = librosa.piptrack(y=wav, sr=sample_rate, n_fft=1024, fmin=0)
    pitches = pitches[mags > np.median(mags)]
    mags = mags[mags > np.median(mags)]

    pitches = pitches[pitches > 0]
    pitche = np.mean(pitches)
    return pitche


def _pitch_reaper(wav_path):
    pitch_path = wav_path.replace('.wav', '.pitch')
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

    os.remove(pitch_path)
    return pitche


def _sound_section(wav, sample_rate):
    frame_len_ms = 25
    frame_step_ms = 15
    pause_len_ms = 50
    frame_len = frame_len_ms * sample_rate // 1000
    frame_step = frame_step_ms * sample_rate // 1000
    pause_len = pause_len_ms * sample_rate // 1000
    th = None

    label = vad.power(wav, frame_len=frame_len, frame_step=frame_step, th=th)
    label = vad.post_filter(label, pause_len=pause_len)
    _write_label(label, sample_rate)

    sect = []
    for l in label:
        sect.append(l['end'] - l['start'])

    return sect


def _write_label(label, sample_rate):
    with open('label.txt', "w") as f:
        for item in label:
            start = item['start'] / sample_rate
            end = item['end'] / sample_rate
            f.write(f"{start:.6f}\t{end:.6f}\tsound\n")


def _read_wave(path):
    with wave.open(str(path), mode='rb') as wif:
        # params = (nchannels, sampwidth, framerate, nframes, comptype, compname)
        params = wif.getparams()
        data = wif.readframes(params.nframes)

    data = np.frombuffer(data, np.int16)
    nframes = len(data) // params.nchannels
    wav = data.reshape(nframes, params.nchannels).T

    return wav, params.framerate


def extract(source_path):
    wav_path = source_path + '.wav'

    stream = ffmpeg.input(source_path)
    stream = ffmpeg.output(stream, wav_path, acodec='pcm_s16le', ac=1)
    stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream, capture_stderr=True)

    wav, fr = _read_wave(wav_path)
    wav = wav[0]

    feat = dict()

    feat['sample_rate'] = fr
    feat['length'] = wav.size
    feat['time_ms'] = wav.size * 1000 // fr

    feat['db'] = _db(wav)
    feat['sound_sect'] = _sound_section(wav, fr)
    feat['power_spec'], feat['freq'], feat['pitch'] = _spectrum(wav, fr)

    nfilt = 16
    high_freq = 8000
    filter_type = 'mel'
    feat['fbank_spec'], feat['fbank_freq'] = _fbank(wav, sample_rate=fr, nfilt=nfilt,
                                                    high_freq=high_freq, type=filter_type)

    feat['pitch_reaper'] = _pitch_reaper(wav_path)

    wav, fr = librosa.load(wav_path)
    feat['pitch_librosa'] = _pitch_librosa(wav, fr)

    os.remove(wav_path)
    return feat


if __name__ == '__main__':
    print(extract('c2.webm'))
