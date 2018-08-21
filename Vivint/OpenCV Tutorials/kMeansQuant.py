import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

imgpath = 'bird.png'
img = cv2.imread(imgpath)

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)


def kmeans(K, img, criteria):
    Z = np.float32(img.reshape((-1, 3)))  # Shapes the image so the pixels are all in 1 dimension.

    ret, label1, center1 = cv2.kmeans(Z, K, None,
                                      criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    # 10 = Number of iterations for clustering.
    center1 = np.uint8(center1)
    res1 = center1[label1.flatten()]
    return res1.reshape(img.shape)


Ks = [3, 5, 8, 12, 16, 32]
outputs = np.concatenate(([kmeans(x, img, criteria) for x in Ks], [img]))
titles = np.concatenate((["K=" + str(x) for x in Ks], ['Orig']))

for i in range(len(outputs)):
    plt.subplot(1, len(outputs), i+1)
    plt.imshow(outputs[i])
    plt.title(titles[i])
    plt.xticks([])
    plt.yticks([])
plt.show()


def vid(K, criteria, res):
    cap = cv2.VideoCapture(0)
    cap.set(3, res[0])
    cap.set(4, res[1])

    while True:
        ret, frame = cap.read()
        newframe = kmeans(K, frame, criteria)
        cv2.imshow('Color_Reduced', newframe)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cap.release()


vid(16, criteria, [260, 220])