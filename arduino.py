import cv2
import pyrebase
import HandModule
#############################
camw, camh = 960, 720
#############################

color = ["red", "green", "blue"]

firebaseConfig = {
    "apiKey": "AIzaSyA1501tS1oe8YF-F7CCeFosUbCCovPrq9Q",
    "authDomain": "python1-f0771.firebaseapp.com",
    "databaseURL": "https://python1-f0771-default-rtdb.firebaseio.com",
    "projectId": "python1-f0771",
    "storageBucket": "python1-f0771.appspot.com",
    "messagingSenderId": "696223136031",
    "appId": "1:696223136031:web:3fb6e65719ad2edcdfd82a",
    "measurementId": "G-BVK3PECXBR"
  }
firebase = pyrebase.initialize_app(firebaseConfig)
database = firebase.database()
vid = cv2.VideoCapture(0)
vid.set(3, camw)
vid.set(4, camh)

detector = HandModule.HandGadgets()
firebasevals = []
with open("firebase.csv", 'r') as f:
    dataline = f.readlines()
    for line in dataline:
        print(line)
        lines = line.split('=')
        print(lines[1])
        firebasevals.append(lines[1])
detectionStatus = "unkown"
i = 0
time = 0
while True :
    success, frame = vid.read()
    frame, status = detector.TiltBase(frame = frame)
    if status == "right" and time > 20:
        i += 1
        time = 0

    if status == "left" and time > 20:
        i -= 1
        time = 0
    if i > 2 :
        i = 0
    if i < 0 :
        i = 2

    cv2.putText(frame, color[i], (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 7)
    print(time)
    time += 1
    cv2.imshow("video", frame)
    cv2.waitKey(1)