# -*- coding: utf-8 -*-

import math
from typing import Tuple, Optional, Callable

import numpy as np
from scipy.signal import resample

def framesig(signal, frame_len, frame_step, winfunc=np.hamming):
    siglen = len(signal)
    numframes = 1
    if siglen > frame_len:
        numframes += int(math.ceil((siglen - frame_len) / frame_step))

    padlen = int((numframes - 1) * frame_step + frame_len)
    padsignal = np.zeros((padlen,))
    padsignal[:siglen] = signal

    indices = np.arange(0, frame_len)[np.newaxis, :] + np.arange(0, numframes * frame_step, frame_step)[:, np.newaxis]
    indices = indices.astype(np.int)
    frames = padsignal[indices]

    if winfunc:
        frames *= winfunc(frame_len)[np.newaxis, :]

    return frames


def deframesig(frames, frame_len, frame_step, siglen=None, winfunc=np.hamming, dtype=None):
    numframes = frames.shape[0]
    assert frames.shape[1] == frame_len, '"frames" matrix is wrong size, 2nd dim is not equal to frame_len'

    indices = np.arange(0, frame_len)[np.newaxis, :] + np.arange(0, numframes * frame_step, frame_step)[:, np.newaxis]
    indices = indices.astype(np.int)
    padlen = int((numframes - 1) * frame_step + frame_len)

    signal = np.zeros((padlen,))
    window_correction = np.zeros((padlen,))
    win = winfunc(frame_len)

    for i in range(numframes):
        window_correction[indices[i, :]] += win
        signal[indices[i, :]] += frames[i, :]

    # add a little bit so it is never zero
    window_correction = np.where(window_correction == 0, np.finfo(float).eps, window_correction)
    signal = (signal / window_correction)

    if siglen is None:
        signal = signal[0:siglen]

    if dtype is not None:
        signal = signal.astype(dtype)

    return signal


def stft(signal,
         frame_len: int,
         frame_step: int,
         nfft: Optional[int] = None,
         winfunc: Callable[[int], np.ndarray] = np.hamming) -> Tuple[np.ndarray, np.ndarray]:
    frames = framesig(signal, frame_len, frame_step, winfunc=winfunc)
    if nfft is not None:
        frames = resample(frames, nfft, axis=1)
    complex_spec = np.fft.rfft(frames)
    magnitude_spec = np.absolute(complex_spec)
    phase_spec = np.angle(complex_spec)

    return magnitude_spec, phase_spec


def istft(magnitude_spec, phase_spec, frame_len, frame_step, siglen=None, winfunc=np.hamming, dtype=np.int16):
    complex_spec = magnitude_spec * np.exp(phase_spec * 1j)
    frames = np.fft.irfft(complex_spec)
    frames = resample(frames, frame_len, axis=1)
    signal = deframesig(frames, frame_len, frame_step, siglen=siglen, winfunc=winfunc)

    if dtype is not None:
        signal = signal.astype(dtype)

    return signal


def fbank(signal, samplerate=16000, frame_len=400, frame_step=160, nfilt=26,
          lowfreq=0, highfreq=None, winfunc=np.hamming):
    highfreq = highfreq or samplerate / 2

    magnitude_spec, phase_spec = stft(signal, frame_len, frame_step, nfft=None, winfunc=winfunc)

    fb = _get_filterbanks(nfilt, frame_len, samplerate, lowfreq, highfreq)
    feat = np.dot(magnitude_spec, fb.T)  # compute the filterbank energies
    feat = np.where(feat == 0, np.finfo(float).eps, feat)  # if feat is zero, we get problems with log

    return feat, phase_spec


def ifbank(feat, phase_spec, samplerate=16000, frame_len=400, frame_step=160, nfilt=26,
           lowfreq=0, highfreq=None, winfunc=np.hamming):
    ifb = _get_ifilterbanks(nfilt, frame_len, samplerate, lowfreq, highfreq)
    magnitude_spec = np.dot(ifb, feat.T).T

    signal = istft(magnitude_spec, phase_spec, frame_len, frame_step, winfunc=winfunc)

    return signal


def _hz2mel(hz):
    return 2595 * np.log10(1 + hz / 700)


def _mel2hz(mel):
    return 700 * (10 ** (mel / 2595) - 1)


def _get_filterbanks(nfilt=20, nfft=512, samplerate=16000, lowfreq=0, highfreq=None):
    if highfreq is None:
        highfreq = samplerate / 2
    assert highfreq <= samplerate / 2, "highfreq is greater than samplerate/2"

    # compute points evenly spaced in mels
    # lowmel = _hz2mel(lowfreq)
    # highmel = _hz2mel(highfreq)
    # melpoints = np.linspace(lowmel, highmel, nfilt + 2)
    # our points are in Hz, but we use fft bins, so we have to convert
    #  from Hz to fft bin number
    # bin = np.floor((nfft + 1) * _mel2hz(melpoints) / samplerate)
    bin = np.floor((nfft + 1) * np.linspace(lowfreq, highfreq, nfilt + 2) / samplerate)

    fbank = np.zeros((nfilt, nfft // 2 + 1))
    for j in range(0, nfilt):
        for i in range(int(bin[j]), int(bin[j + 1])):
            fbank[j, i] = (i - bin[j]) / (bin[j + 1] - bin[j])
        for i in range(int(bin[j + 1]), int(bin[j + 2])):
            fbank[j, i] = (bin[j + 2] - i) / (bin[j + 2] - bin[j + 1])

    return fbank


def _get_ifilterbanks(nfilt=20, nfft=512, samplerate=16000, lowfreq=0, highfreq=None):
    fb = _get_filterbanks(nfilt=nfilt, nfft=nfft, samplerate=samplerate, lowfreq=lowfreq, highfreq=highfreq)
    ff = np.dot(fb.T, fb)
    m = np.mean(np.diag(ff)) / 100
    s = np.sum(ff, axis=0)
    w = np.where(s > m, s, m)
    ifb = fb.T / w[:, np.newaxis]

    return ifb
