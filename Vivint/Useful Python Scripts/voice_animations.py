import cv2
import numpy as np
import urllib.request
import json, base64, time
from datetime import datetime
import os, sys
from queue import Queue
from threading import Thread

fps = 10
font = cv2.FONT_HERSHEY_SIMPLEX
video_q = Queue(maxsize=4)
result_q = Queue(maxsize=4)
color_map = {'person': (0, 255, 0), 'face': (0, 0, 255)}
face_thresh = 0.475
wd = 0.9  # Percent of image above the voice text

sample = 'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
current_state = {'isperson': False, 'personId': ""}
clear_screen = lambda: os.system('clear')


def post(image):
  success, img_jpg = cv2.imencode('.jpg', image)
  image_string = base64.b64encode(img_jpg.tobytes()).decode()
  body = {'image': image_string}
  myurl = "http://192.168.2.195:8765/request"  # 69.58.93.10
  # myurl = "http://69.58.93.10:8765/request"
  req = urllib.request.Request(myurl)
  req.add_header('Content-Type', 'application/json; charset=utf-8')
  jsondata = json.dumps(body)
  jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
  req.add_header('Content-Length', len(jsondataasbytes))
  # print(jsondataasbytes)
  t0 = time.time()
  response = urllib.request.urlopen(req, jsondataasbytes)
  result_msg = response.read().decode()
  result_json = json.loads(result_msg)
  # print(result_msg)
  result_q.put([image, result_msg])
  # handle_message(result_json,current_state)
  print("time elapsed: ", time.time() - t0)


# Function that draws a translucent box on an image with given coordinates, text, font size, box color, and thickness
# If you supply "centered" as the first element of cords, you'll center it horizontally on the image.
# Ex. ("centered", 200) will center the box horizontally at 200 pixels from the top
# You can also raise the alpha parameter to make the boxes less transparent (Between 0 and 1)

def draw_transluc_box(img, cords, text, fsize, col, fthick=2):
  alpha = 0.6
  eps = 5
  dims = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fsize, fthick)[0]

  if cords[0] == 'centered':
      pt1 = (int((img.shape[1] - dims[0])/2), cords[1]+5)
  else:
      pt1 = (cords[0], cords[1] + eps)
  pt2 = (pt1[0] + dims[0], pt1[1] - dims[1] - eps * 2)

  overlay = img.copy()
  cv2.rectangle(overlay, pt1, pt2, col, -1)
  cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
  if cords[0] == 'centered':
    cv2.putText(img, text, (pt1[0], cords[1]), cv2.FONT_HERSHEY_SIMPLEX, fsize, (255, 255, 255), fthick)
  else:
    cv2.putText(img, text, (cords[0] + 1, cords[1]), cv2.FONT_HERSHEY_SIMPLEX, fsize, (255, 255, 255), fthick)


def draw_box(img, result):
  print(result)
  objs = json.loads(result)
  mismatch = False
  voice_match = False
  face_match = False
  for obj in objs['objects']:
    box = obj['box']
    obj_confidence = obj['confidence']
    if obj_confidence < 0.9:
      continue
    if 'face' in obj:
      print('we found a face')
      face = obj['face']
      face_box = face['box']
      face_confidence = face['confidence']
      box = [box[0] + face_box[0], box[1] + face_box[1], box[0] + face_box[2], box[1] + face_box[3]]
      face_id = face['id']
      color = color_map.get('face')
      annotation = "Unknown_Face (%.3f)" % face_confidence
      if face_confidence > face_thresh:
        face_match = True
        annotation = "Match: %s %.3f" % (face_id, face_confidence)
        color = (0,255,0)
      t_size = cv2.getTextSize(annotation, font, 0.6, 2)
      cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), color, 2)
      cv2.rectangle(img, (box[0], box[1]), (box[0] + t_size[0][0], box[1] - t_size[0][1] - 12), color, cv2.FILLED)
      cv2.putText(img, annotation, (box[0] + 1, box[1] - 10), font, 0.6, (255, 255, 255), 2)
      # face_cords = (box[0], int(img.shape[0] * wd))

  # Most of the animations are here:
  key = cv2.waitKey(1)
  if key == ord('q'):
    voice_match = True
  # Mismatch = Identified both voice and face, but the person IDs don't match.
  elif key == ord('w'):
    mismatch = True

  voice_cords = ("centered", int(img.shape[0] * wd) + 1)
  if voice_match:
    word = "vivint"
    text = 'Voice Match Found! Word "%s" detected' % word
    col = (0, 255, 0)
  elif mismatch:
    text = "Voice/Face Mismatch"
    col = (0,100,255)
  else:
    text = "No/Unknown voice detected"
    col = (0, 0, 255)

  draw_transluc_box(img, voice_cords, text, 0.8, col)

  if face_match and voice_match:
    draw_transluc_box(img, ('centered', 75), "Access Granted!", 2, (0, 255, 0), 3)
  else:
    draw_transluc_box(img, ('centered', 75), "Access Denied", 2, (0, 0, 255), 3)

  cv2.imshow("Face ID demo", img)
  cv2.waitKey(1)
  return img


def video_service():
  while (1):
    if not video_q.empty():
      try:
        frame = video_q.get()
        print(str(datetime.now()))
        post(frame)
      except Exception as e:
        # sleep for a bit in case that helps
        print(e)
        time.sleep(1)


def url_to_image(url):
  resp = urllib.request.urlopen(url)                          # Downloads image
  im = np.asarray(bytearray(resp.read()), dtype="uint8")      # Converts byte sequence to np array
  im2 = cv2.imdecode(im, cv2.IMREAD_COLOR)                    # Reshapes into color format
  return im2


def capture_frame():
  count = 0
  stream_url = 0
  cap = cv2.VideoCapture(stream_url)

  while True:
    # Capture frame-by-frame
    try:
      count += 1
      _, f = cap.read()
    # print(count)
      if len(f) > 0:
        if count % fps == 0:
          count = 0
          video_q.put(f)
    # Check if camera opened successfully
    except Exception:
      print("Error opening video stream or file")
      time.sleep(1)

# starting threads
# read_worker = Thread(target=capture_frame)
# service_worker = Thread(target=video_service)
# read_worker.start()
# service_worker.start()

Thread(target=capture_frame).start()
for x in range(3):
  Thread(target=video_service).start()

# read_worker.join()
# service_worker.join()

while(1):
  # print(result_q.qsize())
  if not result_q.empty():
    image, result_msg = result_q.get()
    # print(result_msg)
    draw_box(image, result_msg)
    