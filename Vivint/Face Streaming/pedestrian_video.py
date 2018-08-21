import os
import cv2
import numpy as np

# Initialize HOG parameters
winSize = (64, 128)
blockSize = (16, 16)
blockStride = (8, 8)
cellSize = (8, 8)
nbins = 9
derivAperture = 1
winSigma = -1
histogramNormType = 0
L2HysThreshold = 0.2
gammaCorrection = True
nlevels = 64
signedGradient = False

hogDefault = cv2.HOGDescriptor(winSize, blockSize, blockStride,
                               cellSize, nbins, derivAperture,
                               winSigma, histogramNormType, L2HysThreshold,
                               gammaCorrection, nlevels, signedGradient)
svmDetectorDefault = cv2.HOGDescriptor_getDefaultPeopleDetector()
hogDefault.setSVMDetector(svmDetectorDefault)


finalHeight = 400

cap = cv2.VideoCapture('jeremy-vids/negative/test9.mp4')


def bbox(img, x1, y1, x2, y2, base_color=(255, 0, 0), text='Human Detected'):
    x_adj = 8*len(text)
    y_adj = 13
    font = .36
    cv2.rectangle(img, (x1, y1), (x2, y2), base_color, 2)
    if y1 > 20:
        cv2.rectangle(img, (x1, y1 - y_adj), (x1 + x_adj, y1 - 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, font, base_color)
    else:
        cv2.rectangle(img, (x1, y2 + y_adj), (x1 + x_adj, y2 + 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y2 + y_adj - 4), cv2.FONT_HERSHEY_SIMPLEX, font, base_color)


while cap.isOpened():
    ret, frame = cap.read()
    scale = finalHeight / frame.shape[0]
    im2 = cv2.resize(frame, None, fx=scale, fy=scale)

    bboxes, weights = hogDefault.detectMultiScale(im2, winStride=(4, 4), padding=(16, 16),
                                                  scale=1.05, finalThreshold=2,
                                                  hitThreshold=0)
    for b in bboxes:
        x, y, w, h = b
        # cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 0, 255), 2)
        bbox(im2, x, y, x+w, y+h, (255,150,0))

    cv2.imshow('Video', im2)
    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
cap.release()
