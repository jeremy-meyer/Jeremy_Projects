import cv2
import numpy as np


def main():
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False

    while ret:

        ret, frame = cap.read()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Open CV's HSV scale is [0,180], [0,255], [0,255]

        # Blue Filter. ***Where did these colors come from?
        # low = np.array([100, 50, 50])
        # high = np.array([140, 255, 255])

        low = np.array([180, 50, 50])
        high = np.array([250, 255, 255])

        # Green
        # low = np.array([40, 50, 50])
        # high = np.array([80, 255, 255])

        # Red Color
        # low = np.array([140, 150, 0])
        # high = np.array([180, 255, 255])

        image_mask = cv2.inRange(hsv, low, high)  # Binary image. White = TRUE, Black = False

        output = cv2.bitwise_and(frame, frame, mask=image_mask)  # Only shows parts of mask that have color

        cv2.imshow("Image mask", image_mask)
        cv2.imshow("Original Webcam Feed", frame)
        cv2.imshow("Color Tracking", output)
        if cv2.waitKey(1) == 27:  # exit on ESC
            break

    cv2.destroyAllWindows()
    cap.release()


if __name__ == "__main__":
    main()