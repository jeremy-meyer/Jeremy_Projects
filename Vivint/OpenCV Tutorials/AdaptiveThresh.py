
import cv2
import matplotlib.pyplot as plt
import numpy as np

img = cv2.imread('gradientImg.png', 0)


def adapthresh(img, block_size, const):
    # block_size = 51
    # const = 2. 255 = binary max value
    th1 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, const)
    th2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, const)

    output = [img, th1, th2]

    titles = ['Orig:' + str(block_size), 'Mean Adapt', 'Gaussian Adapt']

    for i in range(len(output)):
        plt.subplot(1, len(output), i+1)
        plt.imshow(output[i], cmap='gray')
        plt.title(titles[i])
        plt.xticks([])
        plt.yticks([])
    plt.show()


adapthresh(img, 61, 3)

# Testing for block_size
const = 2
testvals = [11, 31, 61, 101, 151, 221, 301]
output = [cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, b, const) for b in testvals]

titles = np.concatenate((["Orig"], [str(x) for x in testvals]))

output = np.concatenate(([img], output))
for i in range(len(output)):
    plt.subplot(1, len(output), i+1)
    plt.imshow(output[i], cmap='gray')
    plt.title(titles[i])
    plt.xticks([])
    plt.yticks([])
plt.show()

# Testing for constants. These tend to get rid of a lot of the noise esp. if the gradient is small in the neighborhood
testconst = [2,10]
testvals = [11, 31, 61, 101, 151, 221, 301]
for c in range(len(testconst)):
    const = testconst[c]
    output = [cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, b, const) for b in
              testvals]

    titles = np.concatenate((["Const: " + str(testconst[c])], [str(x) for x in testvals]))

    output = np.concatenate(([img], output))
    for i in range(len(output)):
        plt.subplot(len(testconst), len(output), (i+1) + len(output)*c)
        plt.imshow(output[i], cmap='gray')
        plt.title(titles[i])
        plt.xticks([])
        plt.yticks([])
    plt.show()






