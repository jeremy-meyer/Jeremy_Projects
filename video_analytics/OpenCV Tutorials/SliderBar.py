import cv2
import numpy as np

# Used everytime trackbar changes. (We don't want to do anything)
def emptyFunction(self):
    pass


windowName = 'BGR color pallette'
cv2.namedWindow(windowName)
img1 = np.zeros((512, 512, 3), np.uint8)

cv2.createTrackbar('B', windowName, 0, 255, emptyFunction)  # Name, lowerbound, upperbound, function when switched
cv2.createTrackbar('G', windowName, 0, 255, emptyFunction)
cv2.createTrackbar('R', windowName, 0, 255, emptyFunction)

# create switch for ON/OFF functionality
switch = '0: Normal \n1 : Invert'
cv2.createTrackbar(switch, windowName, 0, 1, emptyFunction)

while True:
    cv2.imshow(windowName, img1)

    if cv2.waitKey(1) == 27:  # ESC to exit
        break

    blue = cv2.getTrackbarPos('B', windowName)
    green = cv2.getTrackbarPos('G', windowName)
    red = cv2.getTrackbarPos('R', windowName)
    if cv2.getTrackbarPos(switch, windowName):
        img1[:] = abs(255 - np.array([blue, green, red]))
    else:
        img1[:] = [blue, green, red]

cv2.destroyAllWindows()


# HSV Pallette

windowName = 'HSV color pallette'
cv2.namedWindow(windowName)
img1 = np.zeros((512, 512, 3), np.uint8)  # Window Size: 512x512

cv2.createTrackbar('H', windowName, 0, 180, emptyFunction)  # Name, lowerbound, upperbound, ?
cv2.createTrackbar('S', windowName, 0, 255, emptyFunction)
cv2.createTrackbar('V', windowName, 0, 255, emptyFunction)

# create switch for ON/OFF functionality
switch = '0: Normal \n1 : Invert'
cv2.createTrackbar(switch, windowName, 0, 1, emptyFunction)

while True:
    cv2.imshow(windowName, cv2.cvtColor(img1, cv2.COLOR_HSV2BGR))

    if cv2.waitKey(1) == 27:  # ESC to exit
        break

    hue = cv2.getTrackbarPos('H', windowName)
    saturation = cv2.getTrackbarPos('S', windowName)
    value = cv2.getTrackbarPos('V', windowName)
    if cv2.getTrackbarPos(switch, windowName):
        img1[:, :, 1:] = abs(255 - np.array([saturation, value]))
        img1[:, :, 0] = abs(180 - np.array([hue]))
    else:
        img1[:] = [hue, saturation, value]

cv2.destroyAllWindows()
