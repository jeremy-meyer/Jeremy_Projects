
import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread('bird.png')
noisy = np.zeros(img.shape, np.uint8)
p = 0.2
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        r = np.random.uniform()
        if r < p/2:
            noisy[i][j] = [0,0,0]
        elif r <= p:
            noisy[i][j] = [255,255,255]
        else:
            noisy[i][j] = img[i][j]

# Filters noise from the median of 5x5 area by taking the median pixel
denoised = cv2.medianBlur(noisy, 5)

output = [img, noisy, denoised]
titles = ['Original', 'Noisy', 'denoised']

for i in range(len(output)):
    plt.subplot(1, len(output), i+1)
    plt.imshow(output[i])
    plt.title(titles[i])
    plt.yticks([])
    plt.xticks([])
plt.show()
