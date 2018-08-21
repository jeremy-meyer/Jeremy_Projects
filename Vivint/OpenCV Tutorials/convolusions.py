import cv2
import matplotlib.pyplot as plt
import numpy as np


img = cv2.imread('Ross_Pereira.jpg', 1)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

k = np.array(np.ones((11, 11), np.float32)) / 121

# Convolusion uses a matrix (kernel) operator on the image
k = np.array(([0, -1, 0], [-1, 5, -1], [0, -1, 0]), np.float32)
k2 = np.array(np.ones((3,3), np.float32))

# print(k)

# -1: Depth of output image. Depth output = depth input. Returns convoluted image
output = cv2.filter2D(img, -1, k2)

plt.subplot(1, 2, 1)
plt.imshow(img)
plt.title('Original Image')

plt.subplot(1, 2, 2)
plt.imshow(output)
plt.title('Filtered Image')
plt.show()


def applyConv(img, k):
    output = cv2.filter2D(img, -1, k)
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.title('Original Image')

    plt.subplot(1, 2, 2)
    plt.imshow(output)
    plt.title('Filtered Image')
    plt.show()
    return output


conv = np.array(([1, 1], [1, 1]))
# applyConv(img, conv)

# Examples of kernel convolusions
# 1. Identity
# conv1 = np.array(([0, 0, 0], [0, 1, 0], [0, 0, 0]))

# 2. Edge Dectection
conv1 = np.array(([-1, -1, -1], [-1, 8, -1], [-1, -1, -1]))

# 3. Sharpen
conv1 = np.array(([0, -1, 0], [-1, 5, -1], [0, -1, 0]))

# 4. Gaussian Blur
conv1 = 1/16 * np.array(([1, 2, 1], [2, 4, 2], [1, 2, 1]))
applyConv(img, conv1)

# These Convolusions are calculated by using a 3x3 sliding window over the pixels and taking the element-wise sum of the
# product of the kernel and color values of the matrix
# CNNs only work if the data is arranged in a meaningful order (like images). If the columns can be swapped without
#   affecting the interpretation of the data, CNNs can't be used.
# Filter = pattern detector