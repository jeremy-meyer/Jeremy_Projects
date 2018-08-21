import cv2
import numpy as np

res = [320, 180]

cap = cv2.VideoCapture(0)
cap.set(3, res[0])
cap.set(4, res[1])

ret, frame1 = cap.read()
ret, frame2 = cap.read()

while ret:
    # Calculates the absolute difference between the two frames for each pixel
    d = cv2.absdiff(frame1, frame2)

    # No point in saving the color.
    grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)

    # Makes the motions in a 5x5 area.
    blur = cv2.GaussianBlur(grey, (5, 5), 0)

    # Applies a threshold to filter out low changes (<20) between frames.
    _, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

    # Morphical operations to smooth out and highlight areas w/motion dectection
    dilated = cv2.dilate(th, np.ones((3, 3), np.uint8), iterations=1)
    eroded = cv2.erode(dilated, np.ones((3, 3), np.uint8), iterations=1)

    # Finds and draws appropriate contours on first frame
    _, c, _ = cv2.findContours(eroded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame1, c, -1, (0, 0, 255), 2)

    # cv2.imshow('Thresholding', th)
    # cv2.imshow('Eroded', eroded)
    # cv2.imshow('dilated', dilated)
    cv2.imshow("NewFrame", frame2)
    cv2.imshow("Output", frame1)

    if cv2.waitKey(1) == 27:  # exit on ESC
        break

    frame1 = frame2
    ret, frame2 = cap.read()

cap.release()


