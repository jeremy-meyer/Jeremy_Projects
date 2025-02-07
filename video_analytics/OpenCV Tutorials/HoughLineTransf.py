import cv2
import numpy as np

#  Used to detect lines from an edge dectector.


windowName = "Preview"
cv2.namedWindow(windowName)
cap = cv2.VideoCapture(0)

if cap.isOpened():
    ret, frame = cap.read()
else:
    ret = False

while ret:

    ret, frame = cap.read()

    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # For faster processing
    edges = cv2.Canny(grey, 50, 250, apertureSize=5, L2gradient=True)  # Edge dectection

    lines = cv2.HoughLines(edges, 1, np.pi / 180, 250)    # Dectected lines

    if lines is not None:
        for rho, theta in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)   # Red Color, 2 thickness

    cv2.imshow(windowName, frame)

    if cv2.waitKey(1) == 27:  # exit on ESC
        break

cv2.destroyAllWindows()
cap.release()