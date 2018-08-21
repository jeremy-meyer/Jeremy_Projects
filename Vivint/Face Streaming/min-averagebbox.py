
# This file takes into account multiple detections that are clustered close together and merges/removes them.
# It plots the smallest (min) bbox in the cluster in yellow. Generally, this stream is more continuous because the
#   at least one of the bboxes (usually the smallest) is correct.
# It also plots the average bbox in red to compare.

import numpy as np
import cv2

# Global Varibules
res = [1280, 720]                   # Recording resolution
eps = 1.5                           # Used in groupRectangles (line 45)
MIN_LENGTH = min(res) / 15.0        # This is if you would like to set a minimum length for the width of the bbox
                                    #   (Small boxes tend to be false positives)

face_cascade = cv2.CascadeClassifier('/Users/jeremy.meyer/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)
cap.set(3, res[0])
cap.set(4, res[1])


# Centroid of rectangle given (x, y, w, h). Used for finding which rectangles are clustered together.
def centroid(rect):
    return (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)


# Draws bounding box and text from coordinates with a given (x1, y1, x2, y2). Can change displayed text
def bbox(img, x1, y1, x2, y2, base_color=(255, 0, 0), text='Human Detected'):
    x_adj = 12*len(text)       # Length of dark rectangle behind text. Adjusts for longer/shorter texts
    y_adj = 17
    cv2.rectangle(img, (x1, y1), (x2, y2), base_color, 2)
    if (y1 > 20):
        cv2.rectangle(img, (x1, y1 - y_adj), (x1 + x_adj, y1 - 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, base_color)
    else:
        cv2.rectangle(img, (x1, y2 + y_adj), (x1 + x_adj, y2 + 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y2 + y_adj - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, base_color)


while True:
    ret, img = cap.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray)
    grouped = cv2.groupRectangles(list(faces), 1, eps=eps)

    # Detected face Centroids
    fac = np.array([centroid(f) for f in faces])
    clustered = []      # This list will contain the rectangles that are located in a cluster

    # Finds the smallest bbox in the cluster. Plots it in yellow. Also records the indexes of rectangles in a cluster.
    if len(grouped[0]) != 0:
        for i in range(len(grouped[1][0])):
            face_dist = [sum((f - np.array(centroid(grouped[0][i]))) ** 2) for f in fac]
            inds = np.argsort(face_dist) < grouped[1][i][0]
            clustered.extend(np.where(inds)[0])
            face_clust = faces[inds]
            min_face = face_clust[np.argmin([x[2]*x[3] for x in face_clust])]
            x, y, w, h = min_face
            bbox(img, x, y, x + w, y + h, (0, 215, 255), "Human (min)")

    # Deletes the clustered rectangles
    for i in reversed(range(len(clustered))):
        faces = np.delete(faces, i, 0)

    # Plots the non-clustered rectangles in blue
    for (x, y, w, h) in faces:
        if w > MIN_LENGTH:
            bbox(img, x, y, x + w, y + h, (255, 175, 0))

    # Plots the centroid rectangle of the cluster in red.
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
