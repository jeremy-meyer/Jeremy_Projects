
# This file conveniently draws the bboxes from a given video file instead of your webcam. It's all ran from 1 function.
# It will plot the centroid bounding box in red and the original detected faces in blue.

import cv2
import numpy as np

# Used for clustering ( groupRectangles() )
eps = 1.5

face_cascade = cv2.CascadeClassifier('/Users/jeremy.meyer/opencv/data/haarcascades/haarcascade_frontalface_default.xml')


# Draws bounding box and text from coordinates.
def bbox(img, x1, y1, x2, y2, base_color=(255, 0, 0), text='Human Detected'):
    x_adj = 12*len(text)
    y_adj = 17
    cv2.rectangle(img, (x1, y1), (x2, y2), base_color, 2)
    if y1 > 20:
        cv2.rectangle(img, (x1, y1 - y_adj), (x1 + x_adj, y1 - 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, base_color)
    else:
        cv2.rectangle(img, (x1, y2 + y_adj), (x1 + x_adj, y2 + 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y2 + y_adj - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, base_color)


def readvideo(filepath, fps, playback_multiplier=1):

    cap = cv2.VideoCapture(filepath)

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray)
            grouped = cv2.groupRectangles(list(faces), 1, eps=eps)

            # Draws bboxes on original calculated faces in blue
            for (x, y, w, h) in faces:
                    bbox(frame, x, y, x + w, y + h, (255, 175, 0))

            # Draws centroid rectangle in red
            for (x, y, w, h) in grouped[0]:
                    bbox(frame, x, y, x + w, y + h, (0, 0, 255), "Human (Averaged)")

            cv2.imshow('playback', frame)

            if cv2.waitKey(round(1000/fps * 1/playback_multiplier)) == ord('q'):
                break
        else:
            break
    cv2.destroyAllWindows()
    cap.release()


# Example:
readvideo('testVid.mp4', 15, 2)
