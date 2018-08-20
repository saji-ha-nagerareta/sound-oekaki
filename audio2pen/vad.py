import numpy as np
import fft


def _activity_detect(data, th):
    label = []
    act_frames = np.where(data > th)[0]
    if len(act_frames) > 0:
        start = act_frames[0]
        for i in range(1,len(act_frames)):
            if (act_frames[i] - act_frames[i-1]) > 1:
                label.append({'start': start, 'end': act_frames[i-1]})
                start = act_frames[i]
        label.append({'start': start, 'end': act_frames[-1]})

    return label


def _get_hist(data, resolution=100):
    hist = np.zeros((resolution,), dtype=np.int)
    datamax = data.max()
    unit = datamax / resolution
    for i in range(resolution):
        hist[i] = len(np.where((data >= i * unit) & (data < (i + 1) * unit))[0])

    return hist


def _get_threshold(data, low=0.0, high=1.0):
    hist_num = _get_hist(data, resolution=500)
    hist_val = np.arange(hist_num.size) * hist_num

    separation = np.zeros(hist_num.size)
    for t in range(1 + int(hist_num.size * low), int(hist_num.size * high)):
        num1 = np.sum(hist_num[:t])
        ave1 = np.average(hist_val[:t])
        num2 = np.sum(hist_num[t:])
        ave2 = np.average(hist_val[t:])
        r = num1 * num2 * np.square(ave1 - ave2) / np.square(num1 + num2)

        separation[t] = r
    th = separation.argmax()

    th /= hist_num.size
    return th


def _normalization(data):
    data -= data.min()
    hist_num = _get_hist(data)
    max_num = np.where(hist_num > sum(hist_num) / 1000)[0][-1] / 100 * data.max()
    data /= max_num
    data[data > 1.0] = 1.0

    return data


# def _db(data):
#     db = np.abs(data)
#     db = 20 * np.log10(np.maximum(db, np.finfo(np.float).eps) / np.iinfo(np.int16).max)
#     return db

def _db(data):
    data = np.abs(data)
    positive = np.where(data > 0)
    data = data.astype(np.float)
    data[positive] = np.log10(data[positive])
    data *= 20

    return data


def power(wav, frame_len, frame_step, th=None):
    # data = np.abs(wav).astype(np.float)
    data = _db(wav)

    data = np.average(fft.framesig(data, frame_len, frame_step), axis=1)
    data = _normalization(data)

    if th is None:
        th = _get_threshold(data)

    label = _activity_detect(data, th)
    for l in label:
        l['start'] = l['start']*frame_step
        l['end'] = l['end']*frame_step + frame_len

    return label


def post_filter(label, pause_len):
    if len(label) == 0:
        return label

    filtered_label = []
    start = label[0]['start']
    for i in range(1, len(label)):
        if (label[i]['start'] - label[i-1]['end']) > pause_len:
            filtered_label.append({'start': start, 'end': label[i-1]['end']})
            start = label[i]['start']
    filtered_label.append({'start': start, 'end': label[-1]['end']})

    return filtered_label
