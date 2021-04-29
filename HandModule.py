import cv2
import mediapipe as mp
import math
import numpy as np
import pyrebase
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from google.protobuf.json_format import MessageToDict


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.7, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.barvol = 0
        self.barpercentange = 0
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img,
                    handLms,
                    self.mpHands.HAND_CONNECTIONS,
                    self.mpDraw.DrawingSpec(color = (0, 0, 255), circle_radius= 3, thickness= cv2.FILLED),
                    self.mpDraw.DrawingSpec(color = (0, 255, 0), thickness=3)
                    )
        return img
    def findPosition(self, img, handNo=0, draw = False ):
        hand = []
        lmlist = []
        length = 0
        l = 0
        if self.results.multi_hand_landmarks:
                handlm = self.results.multi_hand_landmarks[handNo]
                for id, lm in enumerate(handlm.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                   # print(id, cy, cx)
                    lmlist.append([id, cx, cy])
                    if draw :
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        if self.results.multi_hand_landmarks:
            length = len(self.results.multi_handedness)
            x = self.results.multi_handedness

        return lmlist, length
class HandGadgets :
    def __init__(self, detection = True, SendToFirebase = False, maxhands = 1, detectionCon = 0.5, trackconf = 0.5):
        self.detector = handDetector(detectionCon=detectionCon, maxHands=maxhands) #hand module used to detect and identify the points on the hand
        self.firebasevalue = SendToFirebase # firebase confermation
        self.barvol = 0
        self.barpercentage = 0
        self.devices = AudioUtilities.GetSpeakers()
        interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def TiltBase(self, frame):
        firebaseConfig = { # firebase configaration to the firebase database
             "apiKey": "AIzaSyA1501tS1oe8YF-F7CCeFosUbCCovPrq9Q",
             "authDomain": "python1-f0771.firebaseapp.com",
             "databaseURL": "https://python1-f0771-default-rtdb.firebaseio.com",
             "projectId": "python1-f0771",
             "storageBucket": "python1-f0771.appspot.com",
             "messagingSenderId": "696223136031",
             "appId": "1:696223136031:web:8aa3053818556f79dfd82a",
             "measurementId": "G-VYSJV75J0R"
        }
        self.firebase = pyrebase.initialize_app(firebaseConfig)
        self.database = self.firebase.database()
        frame = self.detector.findHands(frame)
        location = self.detector.findPosition(frame)
        if len(location) != 0:
            # getting the locations
            i, x, y = location[0]
            i, x1, y1 = location[9]
            i, indexX, indexY = location[12]
            x2, y2 = ((x + x1) // 2), ((y + y1) // 2)
            bx1, bx2 = x2 + 40, x2 - 40
            status = 0
            # checking
            # print(indexY)
            # 110, 850
            # checking cv2.line(frame, (0, indexY), (960, indexY), (255, 0, 0), 4)  # horizontal center line
            # h, w, c = frame.shape
            # print(h)
            cv2.line(frame, (0, 110), (960, 110), (255, 0, 0), 4)  # horizontal center line
            cv2.line(frame, (0, 430), (960, 430), (255, 0, 0), 4)  # horizontal center line
            cv2.line(frame, (x2, 0), (x2, 720), (255, 0, 0), 4)  # vertical center line
            cv2.line(frame, (x, y), (x1, y1), (0, 255, 0), 2)  # center line
            cv2.line(frame, (0, y2), (960, y2), (255, 0, 0), 4)  # horizontal center line
            detectionStatus = "hand detected"
            if self.firebasevalue == True:
                self.database.child("data").child("detection").update({"detectionStatus": detectionStatus})
            if indexX > bx1:
               # cv2.putText(frame, "status : right ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 255, 0), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 255, 0), 2, )  # threshold 2
                status = "right"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            elif indexX < bx2:
               # cv2.putText(frame, "status : left ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 255, 0), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 255, 0), 2, )  # threshold 2
                status = "left"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            elif indexY < 110:
                cv2.putText(frame, "status : up ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 255, 0), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 255, 0), 2, )  # threshold 2
                status = "up"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            elif y > 430:
                cv2.putText(frame, "status : down ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 255, 0), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 255, 0), 2, )  # threshold 2
                status = "down"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            else:
                cv2.putText(frame, "status : normal ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 0, 255), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 0, 255), 2, )  # threshold 2
                status = "stationary"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            cv2.circle(frame, (x2, y2), 8, (0, 255, 0), cv2.FILLED)  # center point
        else:
            detectionStatus = "hand not detected"
            status = "not detected"
            if self.firebasevalue == True:
                self.database.child("data").child("detection").update({"detectionStatus": detectionStatus})
                self.database.child("data").child("direction").update({"directionStatus": "null"})
            cv2.putText(frame, "status : not detected", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
        return frame, status

    def VolumeControl(self, frame, volrange, ):
        frame = self.detector.findHands(frame)
        lmlist = self.detector.findPosition(frame, draw=False)
        volRange = volrange
        minVol = volRange[0]
        maxVol = volRange[1]
        distance = 0
        if len(lmlist) != 0:
            # print(lmlist[4], lmlist[8])
            x1, y1 = lmlist[4][1], lmlist[4][2]
            x2, y2 = lmlist[8][1], lmlist[8][2]
            x, y = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(frame, (x, y), 10, (255, 0, 255), cv2.FILLED)
            distance = math.hypot(x2 - x1, y2 - y1)
            vol = np.interp(distance, [50, 300], [minVol, maxVol])
            self.barvol = np.interp(distance, [50, 300], [500, 100])
            self.barpercentage = np.interp(distance, [50, 300], [0, 100])
            self.volume.SetMasterVolumeLevel(vol, None)
            self.volume.SetMasterVolumeLevel(vol, None)

            if distance < 175:
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
            if distance > 175:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            if distance > 300:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

        cv2.rectangle(frame, (75, 100), (128, 500), (0, 255, 0), 3)
        cv2.rectangle(frame, (75, int(self.barvol)), (128, 500), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, f'{int(self.barpercentage)}%', (65, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        if self.barpercentage < 50:
            cv2.rectangle(frame, (75, int(self.barvol)), (128, 500), (255, 0, 0), cv2.FILLED)
        if self.barpercentage > 50:
            cv2.rectangle(frame, (75, int(self.barvol)), (128, 500), (0, 255, 0), cv2.FILLED)
        if self.barpercentage >= 100:
            cv2.rectangle(frame, (75, int(self.barvol)), (128, 500), (0, 0, 255), cv2.FILLED)
        percentage = str(self.barpercentage)+"%"

        return frame, percentage, distance
def main() :

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    pTime = 0
    cTime = 0
    detector = handDetector()
    #############################
    camw, camh = 960, 720
    #############################

    vid = cv2.VideoCapture(0)
    vid.set(3, camw)
    vid.set(4, camh)
    while True:
        success, img = vid.read()
        frame = detector.findHands(img)
        pos = detector.findPosition(frame)
        cv2.imshow('video', frame)
        print(frame)
        cv2.waitKey(1)

if __name__ == "__main__" :
    main()