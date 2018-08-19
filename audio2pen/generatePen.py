#!/usr/bin/env python3
import cv2
import numpy as np
import sys
from acoustic_feature import extract
from math import cos, sin, degrees, radians

WIDTH,HEIGHT = 33,33  

def powerSpectrum2Brush(ps):
  img = np.ones((HEIGHT,WIDTH),dtype=np.uint8)*255
  for t in range(0,360):
    for r in range(0,int(WIDTH/2)):
      x = int(r * cos(radians(t)) + WIDTH/2)
      y = int(r * sin(radians(t)) + HEIGHT/2)
      img[y,x] = 255 - int(ps[r*150]*255)

  return img

# feature => img
def generateBrush(feature):
    PITCH_MAX = 2000

    db = max(feature["db"], -72) + 72 # [0:72]

    img_filter = np.random.rand(WIDTH, HEIGHT)
    thr = db/72 # [0,1.0]
    p = feature["pitch"]
    print(thr)

    img_filter[img_filter > thr] = 255
    img_filter[img_filter < thr] = 0
    img_filter = img_filter.astype(np.uint8)

    print(p)

    h = min(p / PITCH_MAX * 180,180)
    s = np.ones( (WIDTH, HEIGHT), dtype=np.uint8 ) * 255
    v = np.ones( (WIDTH, HEIGHT), dtype=np.uint8 ) * 200
    
    for i in range(HEIGHT):
      for j in range(WIDTH):
        if(img_filter[i,j] == 255):
          s[i,j] = 0
          v[i,j] = 255

    img_hsv = np.ndarray( (WIDTH, HEIGHT, 3), dtype=np.uint8 )
    for i, x in enumerate([h, s, v]):
      img_hsv[:,:,i] = x
    
    img_rgb = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)
    return img_rgb

# for test
if __name__ == '__main__':
    # argc, argv = len(sys.argv), sys.argv
    # if argc != 5:
    #   print("usage: ./generatePen.py [WIDTH] [HEIGHT] [file-name] [audio-name]")
    #   quit()
    argv = ["xxx", "32", "32", "pen_ps.png", "c2.webm"]

    # WIDTH, HEIGHT = [int(x) for x in argv[1:3]]
    file_name = argv[3]
    audio_name = argv[4]
    feature = extract(audio_name)
    # img = generateBrush(feature)
    img = powerSpectrum2Brush(feature["power_spec"])
    cv2.imwrite(file_name,img)
