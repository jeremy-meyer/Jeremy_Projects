
import cv2
import matplotlib.pyplot as plt

img = cv2.imread('bird.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Lower/Upper thresholds for edge detection. If between, it is kept if adjacent to high.  L1 absolute, L2 squared
L1 = cv2.Canny(img, 150, 200, L2gradient=False)

L2 = cv2.Canny(img, 150, 200, L2gradient=True)

titles = ['Original Image', 'L1 Norm', 'L2 Norm']

outputs = [img, L1, L2]

for i in range(3):
    plt.subplot(1, 3, i + 1)
    plt.imshow(outputs[i], cmap='gray')
    plt.title(titles[i])
    plt.xticks([])
    plt.yticks([])
plt.show()


def cameraedges(size):

    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        edges = cv2.Canny(frame, size[0], size[1])

        cv2.imshow('OG', frame)
        cv2.imshow('Edges', edges)
        if cv2.waitKey(1) == 27:  # ESC to exit
            break
    cv2.destroyAllWindows()
    cap.release()


cameraedges([100, 60])
