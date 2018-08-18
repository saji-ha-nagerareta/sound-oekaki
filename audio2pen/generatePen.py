#!/usr/bin/env python3
import cv2
import numpy as np
import sys
from acoustic_feature import extract

# feature => img
def generateBrush(feature):
    width,height = 32,32    
    PITCH_MAX = 2000

    db = max(feature["db"], -72) + 72 # [0:72]

    img_filter = np.random.rand(width, height)
    thr = db/72 # [0,1.0]
    p = feature["pitch"]
    print(thr)

    img_filter[img_filter > thr] = 255
    img_filter[img_filter < thr] = 0
    img_filter = img_filter.astype(np.uint8)

    print(p)

    h = min(p / PITCH_MAX * 180,180)
    s = np.ones( (width, height), dtype=np.uint8 ) * 255
    v = np.ones( (width, height), dtype=np.uint8 ) * 200
    
    for i in range(height):
      for j in range(width):
        if(img_filter[i,j] == 255):
          s[i,j] = 0
          v[i,j] = 255

    img_hsv = np.ndarray( (width, height, 3), dtype=np.uint8 )
    for i, x in enumerate([h, s, v]):
      img_hsv[:,:,i] = x
    
    img_rgb = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)
    return img_rgb

# for test
if __name__ == '__main__':
    # argc, argv = len(sys.argv), sys.argv
    # if argc != 5:
    #   print("usage: ./generatePen.py [width] [height] [file-name] [audio-name]")
    #   quit()
    argv = ["xxx", "32", "32", "pen.png", "c2.webm"]

    width, height = [int(x) for x in argv[1:3]]
    file_name = argv[3]
    audio_name = argv[4]
    feature = extract(audio_name)
    img = generateBrush(feature)
    cv2.imwrite(file_name,img)
