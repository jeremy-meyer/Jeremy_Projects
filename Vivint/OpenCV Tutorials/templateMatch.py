
import cv2
import numpy as np
from matplotlib import pyplot as plt

img_rgb = cv2.imread('tutorials/mario.png')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) # Converts to grayscale. Color isn't too important
template = cv2.imread('tutorials/coin.png',0) # Reads in the coin template
w, h = template.shape[::-1] # Dimensions of template

res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
threshold = 0.8
loc = np.where( res >= threshold)
for pt in zip(*loc[::-1]):  # Loops through every x, y pair
    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 1)  # Remember that w and h came from template

plt.imshow(res, cmap='gray')

cv2.imshow('test', img_rgb)
cv2.waitKey(0)
# cv2.imwrite('res.png',img_rgb)
