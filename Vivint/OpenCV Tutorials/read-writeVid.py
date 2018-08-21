
import cv2
import matplotlib.pyplot as plt


def imagecapture(plotit=True):
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False

    img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if plotit:
        plt.imshow(img1)
        plt.title("Image captured!")
        plt.xticks([])
        plt.yticks([])
        plt.show()

    return(frame)
    cap.release()


def livestream(gray=False):
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        print("Resolution Width: {}, Height: {}".format(cap.get(3), cap.get(4)))  # How to get resolution
        # Set resolution by doing cap.set(3, newWidth)
    else:
        ret = False
        print("Cannot open video stream")

    while ret:
        ret, frame = cap.read()
        if gray:
            cv2.imshow('Video-BW', cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        cv2.imshow('video', frame)
        if cv2.waitKey(1) == ord('q'):  # Press q to quit. Also, ESC key = 27
            break

    cv2.destroyAllWindows()
    cap.release()

livestream(True)


def writevideo(filename):  #Example filename: "test.mp4"

    codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    fps = 30
    res = (1280, 720)
    videoOutput = cv2.VideoWriter(filename, codec, fps, res)

    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False
        print("Cannot open video stream")

    while ret:
        ret, frame = cap.read()
        videoOutput.write(frame)
        cv2.imshow('video', frame)
        if cv2.waitKey(1) == ord('q'):  # Press q to quit. Also, ESC key = 27
            break

    cv2.destroyAllWindows()
    videoOutput.release()
    cap.release()


def readvideo(filepath, fps, playback_multiplier=1):

    cap = cv2.VideoCapture(filepath)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow('playback', frame)

            if cv2.waitKey(round(1000/fps * 1/playback_multiplier)) == ord('q'):
                break
        else:
            break
    cv2.destroyAllWindows()
    cap.release()


readvideo('testVid.mp4', 30, 1)




