import cv2
import matplotlib.pyplot as plt
import numpy as np


img = cv2.imread('bird.png', 0)

#    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

th = 0
max_val = 255

ret, binary_inv = cv2.threshold(img, th, max_val, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

#    k = np.ones((5, 5), np.uint8)

#    k = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
#    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5, 5))
k = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))  # Kernel

erosion = cv2.erode(binary_inv, k, iterations=1)

dilation = cv2.dilate(binary_inv, k, iterations=1)

gradient = cv2.morphologyEx(binary_inv, cv2.MORPH_GRADIENT, k) # Difference between two. Can be used for edge detection

print(k)

output = [img, binary_inv, erosion, dilation, gradient]

titles = ['Original', 'Binary Inv', 'Erosion', 'Dilation', 'Gradient']

for i in range(5):
    plt.subplot(3, 2, i + 1)
    plt.imshow(output[i], cmap='gray')
    plt.title(titles[i])
    plt.xticks([])
    plt.yticks([])

plt.show()
