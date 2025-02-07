
import cv2
import numpy as np
import termcolor as tc
import urllib.request


def url_to_image(url):
    resp = urllib.request.urlopen(url)                          # Downloads image
    image = np.asarray(bytearray(resp.read()), dtype="uint8")   # Converts byte sequence to np array
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)               # Reshapes into color format
    return image


# Initial test image
stream_url = 'http://192.168.2.167/image/jpeg.cgi'
f = url_to_image(stream_url)    # Reads 1 image to see if it works

try:
    len(f)                                                      # Checks to make sure the image has been read
    # print("Image read in as a {}".format(type(f)))
    while True:
        f = url_to_image(stream_url)
        cv2.imshow('CGI img', f)
        if cv2.waitKey(1) == 27:                                # Press ESC to exit
            break

except TypeError:
    tc.cprint("ERROR: Did not load image (Numpy array us empty)", 'red')
