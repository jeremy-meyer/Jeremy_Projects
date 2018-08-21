
# This file will draw all bounding boxes picked up by the frontal_face classifier using your webcam.
# It will draw the average bounding box in red if multiple are clustered close enoughtogether.

import numpy as np
import cv2

# Global Varibules
res = [1280, 720]                   # Recording resolution
eps = 1.5                           # Used in groupRectangles (line 38)
MIN_LENGTH = min(res) / 15.0        # This is if you would like to set a minimum length for the width of the bbox

classifierPath = '/Users/jeremy.meyer/opencv/data/haarcascades/haarcascade_frontalface_default.xml'  # Stored locally
face_cascade = cv2.CascadeClassifier(classifierPath)
cap = cv2.VideoCapture(0)           # 0 For Webcam
cap.set(3, res[0])                  # Setting resolution
cap.set(4, res[1])


# Draws bounding box and text from coordinates with a given (x1, y1, x2, y2). Can change displayed text
def bbox(img, x1, y1, x2, y2, base_color=(255, 0, 0), text='Human Detected'):
    x_adj = 12*len(text)    # Length of dark rectangle behind text. Adjusts for longer/shorter texts
    y_adj = 17
    cv2.rectangle(img, (x1, y1), (x2, y2), base_color, 2)
    if y1 > 20:
        cv2.rectangle(img, (x1, y1 - y_adj), (x1 + x_adj, y1 - 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, base_color)
    else:                   # This is if the bbox is towards the top of the screen
        cv2.rectangle(img, (x1, y2 + y_adj), (x1 + x_adj, y2 + 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y2 + y_adj - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, base_color)


while True:
    ret, img = cap.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)            # Convert to grayscale for simpler calculations
    faces = face_cascade.detectMultiScale(gray)             # Detected faces
    grouped = cv2.groupRectangles(list(faces), 1, eps=eps)  # Rectangles that were the result of clustering

    # Draws bboxes on original calculated faces in blue
    for (x, y, w, h) in faces:
        if w > MIN_LENGTH:
            bbox(img, x, y, x + w, y + h, (255, 175, 0))

    # Draws bboxes on cluster-combined rectangles in red
    for (x, y, w, h) in grouped[0]:
        if w > MIN_LENGTH:
            bbox(img, x, y, x + w, y + h, (0, 0, 255), "Human (Averaged)")

    # Shows the frame. Hit ESC to close out.
    cv2.imshow('img', img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
