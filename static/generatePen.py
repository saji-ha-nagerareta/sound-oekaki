#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import sys

if __name__ == '__main__':
  argc, argv = len(sys.argv), sys.argv
  if argc != 4:
    print("usage: ./generatePen.py [width] [height] [file-name]")
    quit()

  width, height = [ int(x) for x in argv[1:3] ]
  file_name = argv[3]

  img = np.random.rand(width, height)
  img[img > img.mean()] = 255
  img[img < img.mean()] = 0
  img = img.astype(np.uint8)

  cv2.imwrite(file_name, img)
