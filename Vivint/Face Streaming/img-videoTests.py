import cv2

body_cascade = cv2.CascadeClassifier('/Users/jeremy.meyer/opencv/data/haarcascades/haarcascade_fullbody.xml')
face_cascade = cv2.CascadeClassifier('/Users/jeremy.meyer/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
#ped_cascade = cv2.CascadeClassifier('/Users/jeremy.meyer/opencv/data/hogcascades/hogcascade_pedestrians.xml')

def testCascade(casc, imgpath, pr = True):

    test = cv2.imread(imgpath)
    bodies = casc.detectMultiScale(test)
    if pr:
        print(len(bodies))
    for (x, y, w, h) in bodies:
        cv2.rectangle(test, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.imshow('img', test)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

testCascade(body_cascade, 'test2.png')


def testCascadeVid(casc, vidpath, pr=True):
    cap = cv2.VideoCapture(vidpath)

    while 1:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = casc.detectMultiScale(gray)  # Mess with these parameters later

        if pr:
            print(len(faces))

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


testCascadeVid(face_cascade, 'jeremy-vids/positive/test1.mp4')

# Static image test doesn't work well either.