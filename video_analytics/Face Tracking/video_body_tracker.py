import cv2
import numpy as np
import urllib.request
import json, base64, time
from datetime import datetime
import os, sys
from queue import Queue
from threading import Thread

fps = 8
font = cv2.FONT_HERSHEY_SIMPLEX
video_q = Queue(maxsize=3)
result_q = Queue(maxsize=3)
color_map = {'person': (0, 255, 0), 'face': (0, 0, 255)}
obj_thresh = 0.9        # Confidence threshold for the object
face_thresh = 0.45      # Confidence threshold for the face
dist_thresh = 450**2    # Acceptable squared distance between bboxes for tracking. Similar to epsilon

sample = 'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
current_state = {'isperson': False, 'personId': ""}
clear_screen = lambda: os.system('clear')

# Centroid of rectangle
def centroid(x,y,w,h):
  return [x + w/2, y + h/2]

# Squared Distance
def dist_sq(p1, p2):
  return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2


# matches a previous frame's faces (col) to current frame's faces (row) from a distance matrix.
# Returns tuples (curr, prev) of match. This always pairs one-to-one
def match(dists, threshold):
  # Finds the minimum along each row
  if len(dists) == 0:
    return np.array([])
  pairs = np.array(list(zip(range(len(dists)), np.argmin(dists, axis=1)))) # Minimum pairs
  pairs = pairs[[dists[tuple(p)] < threshold for p in pairs]] # Filter out those who are above threshold
  cols = [x[1] for x in pairs]
  bool = [cols[x] not in np.delete(cols, x) for x in range(len(cols))]  # True if 2nd value (column) is unique
  newPairs = []

  # If we have duplicate column numbers, take the least distant pair
  if sum(bool) != len(bool):
      cols_to_check = list(set([x[1] for x in pairs[np.logical_not(bool)]]))
      for x in cols_to_check:
          newPairs.append([np.argmin(dists[:,x]),x])
      return np.concatenate((pairs[bool], newPairs))
  else:
      return pairs[bool]


def post(image):
  success, img_jpg = cv2.imencode('.jpg', image)
  image_string = base64.b64encode(img_jpg.tobytes()).decode()
  body = {'image': image_string}
  #myurl = "http://192.168.2.195:8765/request"  # 69.58.93.10
  myurl = "http://69.58.93.10:8765/request"
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
  print("time elapsed:    ", time.time() - t0)
  print()

def draw_box(img, result, result_prev, ids):
  objs = json.loads(result)
  objs_prev = json.loads(result_prev)

  # Find all Previous person bboxes and centroids
  prev_person = []
  new_ids = [ids[0],{}]
  for obj_pv in objs_prev['objects']:
    if obj_pv['class'] == 'person':
      if obj_pv['confidence'] > obj_thresh:
        prev_person.append([centroid(*obj_pv['box']), obj_pv])

  # Pairwise Centroid Distances to current bboxes. Creates distance matrix and matches pairs
  dists = []
  for obj in objs['objects']:
    if obj['class'] == "person" and obj['confidence'] > obj_thresh and len(prev_person) > 0:
      cent = centroid(*obj['box'])
      dists.append([dist_sq(cent, p[0]) for p in prev_person])
  pairs = match(np.array(dists), dist_thresh)

  print("Current Frame:    " + result) # Current Frame
  print("Faces_Loaded:     " + str(prev_person)) # Previous frame
  print("IDs loaded:       " + str(ids))
  print("# prev people:    " + str(len(prev_person)))

  pers_ind = 0
  for obj in objs['objects']:
    box = obj['box']
    obj_class = obj['class']
    obj_confidence = obj['confidence']
    annotation = "%s: %.3f" % (obj_class, obj_confidence)
    if obj_confidence < obj_thresh:
      continue
    color = color_map.get(obj_class)
    if 'face' in obj:
      # print('we found a face')
      face = obj['face']
      face_box = face['box']
      face_confidence = face['confidence']
      fbox = [box[0] + face_box[0], box[1] + face_box[1], box[0] + face_box[2], box[1] + face_box[3]]
      face_id = face['id']
      fcolor = color_map.get('face')
      cv2.rectangle(img, (fbox[0], fbox[1]), (fbox[2], fbox[3]), fcolor, 2)
    else:
      face = {}

    if obj_class == "person":
      tracked = False
      if len(pairs) != 0:
        pair_id = pairs[np.where(pairs[:,0] == pers_ind)]
        if len(pair_id) != 0:
          # print("matching pair: " + str(pair_id))
          tracked = True
          curr_id = list(ids[1].keys())[pair_id[0][1]]
          print("Tracking Person!")
          new_ids[1][curr_id] = ids[1][curr_id]
      if not tracked:
        print("New Person!")
        curr_id = new_ids[0]
        new_ids[1][new_ids[0]] = ["Unknown_Person", face_thresh]
        new_ids[0] += 1  # Increase Counter
      if len(face) != 0 and face_confidence > new_ids[1][curr_id][1]:
        new_ids[1][curr_id] = [face_id, face_confidence]

      # Person detected, no face detected, but previous facial data found
      if new_ids[1][curr_id][1] > face_thresh and len(face) == 0:
        annotation = "%s-%s (%.3f) %.3f" % (curr_id, new_ids[1][curr_id][0], new_ids[1][curr_id][1], obj_confidence)
      elif len(face) == 0:  # Person detected, no previous facial data
        annotation = "%s-%s %.3f" % (curr_id, new_ids[1][curr_id][0], obj_confidence)
      else:                 # Face detected
        annotation = "%s-Person %.3f" % (curr_id, obj_confidence)
        # Face Textbox
        fannotation = "%s %.3f" % tuple(new_ids[1][curr_id])
        ft_size = cv2.getTextSize(fannotation, font, 0.6, 2)
        cv2.rectangle(img, (fbox[0], fbox[1]), (fbox[0] + ft_size[0][0], fbox[1] - ft_size[0][1] - 12), fcolor, cv2.FILLED)
        cv2.putText(img, fannotation, (fbox[0] + 1, fbox[1] - 10), font, 0.6, (255, 255, 255), 2)

      pers_ind += 1
    # Prints object bbox
    cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), color, 2)
    t_size = cv2.getTextSize(annotation, font, 0.6, 2)
    cv2.rectangle(img, (box[0], box[1]), (box[0] + t_size[0][0], box[1] - t_size[0][1] - 12), color, cv2.FILLED)
    cv2.putText(img, annotation, (box[0] + 1, box[1] - 10), font, 0.6, (255, 255, 255), 2)


  cv2.imshow("Face ID demo", img)
  cv2.waitKey(1)
  print("Returning:        " + str(objs).replace("\'", "\""))
  return img, str(objs).replace("\'", "\""), new_ids


def video_service():
  while (1):
    if not video_q.empty():
      try:
        frame = video_q.get()
        # print(str(datetime.now()))
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
  # stream_url = 0      # User Webcam
  stream_url = 'http://192.168.98.124/image/jpeg.cgi'
  # cap = cv2.VideoCapture(stream_url)
  # stream_url = 'http://192.168.2.89/image/jpeg.cgi'

  while True:
    # Capture frame-by-frame
    try:
      count += 1
      # _, f = cap.read()
      f = url_to_image(stream_url)
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

msg_prev = str({"objects": ""}).replace("\'", "\"")
ids = [1, {}]
while(1):
  if not result_q.empty():
    image, result_msg, = result_q.get()
    _, msg_prev, ids = draw_box(image, result_msg, msg_prev, ids)
