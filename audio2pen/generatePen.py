#!/usr/bin/env python3
from cv2 import cv2
import numpy as np
import sys
from acoustic_feature import extract
from createFilter import createFilter
from math import cos, sin, degrees, radians, log10

WIDTH, HEIGHT = 33, 33
PITCH_MIN = 40
PITCH_MAX = 500

# feature => img(rgba)
def powerSpectrum2Brush(feature):
    SAMPLING_RATE = feature["sample_rate"]
    ps = feature["power_spec"]
    db = int(max(feature["db"], -72) + 72)  # [0:72]

    print(feature['pitch_reaper'])
    p = max(feature['pitch_reaper'], 1)
    if np.isnan(p):
        p = 1
    p = (log10(p) - log10(PITCH_MIN)) / \
        (log10(PITCH_MAX) - log10(PITCH_MIN))  # p:[0,1]
    print(p)

    img = np.ones((HEIGHT, WIDTH), dtype=np.uint8)*255
    deg = 45
    degdiff = max(db-30, 0)
    step = int(SAMPLING_RATE / ((WIDTH-1) * 10))

    for t in range(deg-degdiff, deg+degdiff):
        for r in range(0, int(WIDTH/2)):
            x = int(r * cos(radians(t)) + WIDTH/2)
            y = int(r * sin(radians(t)) + HEIGHT/2)
            img[y, x] = 255-int(ps[r*step]*255)
            x = int(r * cos(radians(t+180)) + WIDTH/2)
            y = int(r * sin(radians(t+180)) + HEIGHT/2)
            img[y, x] = 255-int(ps[r*step]*255)

    # HSV時計周り方向に 青->緑->黄->赤 で色がつくイメージ
    h = int(120 - min(max(p, 0) * 120, 120)) % 180
    s = img
    v = np.ones((WIDTH, HEIGHT), dtype=np.uint8) * 255

    img_hsv = np.ndarray((WIDTH, HEIGHT, 3), dtype=np.uint8)
    for i, x in enumerate([h, s, v]):
        img_hsv[:, :, i] = x

    img_rgb = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)

    img_rgba = np.ndarray((WIDTH, HEIGHT, 4), dtype=np.uint8)
    for i, x in enumerate([img_rgb[:, :, 2], img_rgb[:, :, 1], img_rgb[:, :, 0]]):
        img_rgba[:, :, i] = x

    img_rgba[:, :, 3] = 255-img

    return img_rgba

# feature => img(rgb)
def generateBrush(feature):
    db = max(feature["db"], -72) + 72  # [0:72]

    img_filter = np.random.rand(WIDTH, HEIGHT)

    thr = db/72  # [0,1.0]

    p = max(feature['pitch_reaper'], 1)
    if np.isnan(p):
        p = 1
    p = (log10(p) - log10(PITCH_MIN)) / \
        (log10(PITCH_MAX) - log10(PITCH_MIN))  # p:[0,1]

    print(thr)

    img_filter[img_filter > thr] = 255
    img_filter[img_filter < thr] = 0
    img_filter = img_filter.astype(np.uint8)


    img_filter = cv2.bitwise_not(cv2.bitwise_and(createFilter(4,1),img_filter))
    


    print(p)

    h = int(120 - min(max(p, 0) * 120, 120)) % 180
    s = np.ones((WIDTH, HEIGHT), dtype=np.uint8) * 255
    v = np.ones((WIDTH, HEIGHT), dtype=np.uint8) * 255

    for i in range(HEIGHT):
        for j in range(WIDTH):
            if(img_filter[i, j] == 255):
                s[i, j] = 0
                v[i, j] = 255

    img_hsv = np.ndarray((WIDTH, HEIGHT, 3), dtype=np.uint8)
    for i, x in enumerate([h, s, v]):
        img_hsv[:, :, i] = x

    img_rgb = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)
    img_rgba = np.ndarray((WIDTH, HEIGHT, 4), dtype=np.uint8)

    for i, x in enumerate([img_rgb[:, :, 2], img_rgb[:, :, 1], img_rgb[:, :, 0]]):
        img_rgba[:, :, i] = x

    img_rgba[:, :, 3] = 255-img_filter


    return img_rgba

# for test
if __name__ == '__main__':
    # argc, argv = len(sys.argv), sys.argv
    # if argc != 5:
    #   print("usage: ./generatePen.py [WIDTH] [HEIGHT] [file-name] [audio-name]")
    #   quit()

    audio_name = "c2.webm"
    argv = ["xxx", "33", "33", audio_name.replace(".webm", ".png"), audio_name]
    image_name = argv[3]
    audio_name = argv[4]
    feature = extract(audio_name)
    # img = powerSpectrum2Brush(feature)
    img = generateBrush(feature)
    cv2.imwrite("geneb.png", img)

