
import cv2
import numpy as np

body_cascade = cv2.CascadeClassifier('/Users/jeremy.meyer/opencv/data/haarcascades/haarcascade_fullbody.xml')
cap = cv2.VideoCapture('jeremy-vids/positive/20170506185655_124_5434.mp4')

fps = 15
playback_multiplier = 2

# while cap.isOpened():
#     ret, frame = cap.read()
#     if ret:
#
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#         humans = body_cascade.detectMultiScale(gray)
#         print(len(humans))
#
#         for (x, y, w, h) in humans:
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
#
#         cv2.imshow('playback', frame)
#
#         if cv2.waitKey(round(1000 / fps * 1 / playback_multiplier)) == ord('q'):
#             break
#     else:
#         break
# cv2.destroyAllWindows()
# cap.release()

cap = cv2.VideoCapture('jeremy-vids/positive/20170606104429_55_14944.mp4')

while 1:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = body_cascade.detectMultiScale(gray)  # Mess with these parameters later

    # Draws bboxes on the faces in blue
    for (x, y, w, h) in faces:

        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Shows the frame. Hit ESC to close out.
    cv2.imshow('img', img)
    k = cv2.waitKey(15) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()

# Doesn't work very well. Too slow fps, doesn't recognize bodies. Things to try:
# - Static image detection