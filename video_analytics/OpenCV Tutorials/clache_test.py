
import cv2
import numpy as np

# Global Varibules
res = [1280, 720]
eps = 1.5

face_cascade = cv2.CascadeClassifier('/Users/jeremy.meyer/opencv/data/haarcascades/haarcascade_frontalface_default.xml')


# Draws bounding box and text from coordinates.
def bbox(img, x1, y1, x2, y2, base_color=(255, 0, 0), text='Human Detected'):
    x_adj = 12*len(text)
    y_adj = 17
    cv2.rectangle(img, (x1, y1), (x2, y2), base_color, 2)
    if (y1 > 20):
        cv2.rectangle(img, (x1, y1 - y_adj), (x1 + x_adj, y1 - 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, base_color)
    else:
        cv2.rectangle(img, (x1, y2 + y_adj), (x1 + x_adj, y2 + 1), np.array(base_color) / 5, -1)
        cv2.putText(img, text, (x1, y2 + y_adj - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, base_color)


def readvideo(filepath, fps, playback_multiplier=1, res=[640, 360]):

    cap = cv2.VideoCapture(filepath)
    cap.set(3, res[0])
    cap.set(4, res[1])

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            # cl1 = clahe.apply(gray)
            # faces1 = face_cascade.detectMultiScale(cl1)
            histeq = cv2.equalizeHist(gray)
            faces1 = face_cascade.detectMultiScale(histeq)
            faces2 = face_cascade.detectMultiScale(gray)
            # grouped = cv2.groupRectangles(list(faces), 1, eps=eps)

            # Draws bboxes on original calculated faces in blue
            for (x, y, w, h) in faces1:
                    bbox(histeq, x, y, x + w, y + h, (255, 175, 0))

            for (x, y, w, h) in faces2:
                    bbox(gray, x, y, x + w, y + h, (255, 175, 0))


            # Draws bboxes on combined rectangles in red
            # for (x, y, w, h) in grouped[0]:
            #         bbox(cl1, x, y, x + w, y + h, (0, 0, 255), "Human (Averaged)")
            #         bbox(gray, x, y, x + w, y + h, (255, 175, 0))

            cv2.imshow('Hist-Eq', histeq)
            cv2.imshow('BW', gray)

            if cv2.waitKey(1) == ord('q'):
                break
        else:
            break
    cv2.destroyAllWindows()
    cap.release()

#readvideo('testVid.mp4', 15, 10)
readvideo('jeremy-vids/positive/test1.mp4', 15, 12)


