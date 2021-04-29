import cv2
import time
import numpy as np
import HandModule as HTM
import math
import pyrebase
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
def findnumber(hand1):
    i = 0
    points = [8, 12, 16, 20]
    tippoints = []
    threshpoints = []
    status = []
    graph = []
    tippoints.append(hand1[4])
    threshpoints.append(hand1[3])
    i, tx, ty = tippoints[0]
    i, tx1, ty1 = threshpoints[0]
    if tx > tx1:
        graph.append(1)
    else:
        graph.append(0)
    i = 0
    while i < 4:
        tippoints.append(hand1[points[i]])
        threshpoints.append(hand1[points[i] - 3])
        id, cx, cy = tippoints[i+1][0], tippoints[i+1][1], tippoints[i+1][2]
        id, cx1, cy1 = threshpoints[i+1][0], threshpoints[i+1][1], threshpoints[i+1][2]
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        cv2.circle(frame, (cx1, cy1), 5, (0, 0, 255), cv2.FILLED)
        # print(cy, cy1)
        if cy < cy1:
            graph.append(1)
        else :
            graph.append(0)
        i = i + 1
    return graph


#############################
camw, camh = 1280, 540
#############################
vid = cv2.VideoCapture(0)
vid.set(3, camw)
vid.set(4, camh)

pTime = 0
vol = 0
barvol = 0
barpercentage = 0
detector = HTM.handDetector(detectionCon=0.5, maxHands=1)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
print(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
print(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
while True:
    success, frame = vid.read()
    frame = detector.findHands(frame)
    lmlist = detector.findPosition(frame, draw= False)
    if len(lmlist)!= 0 :
        graph = findnumber(lmlist)
        if graph == [1, 1, 0, 0, 0] :
            x1, y1 = lmlist[4][1], lmlist[4][2]
            x2, y2 = lmlist[8][1], lmlist[8][2]
            x, y = (x1+x2)//2, (y1+ y2)//2
            cv2.circle(frame,(x1, y1), 10,(255, 0, 255), cv2.FILLED )
            cv2.circle(frame,(x2, y2), 10,(255, 0, 255), cv2.FILLED )
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(frame,(x, y), 10,(255, 0, 255), cv2.FILLED )
            distance = math.hypot(x2-x1, y2-y1)

            #print(distance)

            #hand volume range 15 - 300
            #volume range -65-0

            vol = np.interp(distance, [50, 300], [minVol, maxVol])
            barvol = np.interp(distance, [50, 300], [500, 100])
            barpercentage = np.interp(distance, [50, 300], [0, 100])

            volume.SetMasterVolumeLevel(vol, None)

            if distance<175  :
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                cv2.circle(frame, (x, y), 10, (255, 0, 0), cv2.FILLED)
            if distance>175  :
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)
            if distance>300  :
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.circle(frame, (x, y), 10, (0, 0, 255), cv2.FILLED)


        cv2.rectangle(frame,(75, 100),(128, 500),(0, 255, 0),3)
        cv2.rectangle(frame, (75, int(barvol)), (128, 500), (0, 255, 0), cv2.FILLED )
        cv2.putText(frame, f'{int(barpercentage)}%', (65, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        if barpercentage < 50:
            cv2.rectangle(frame, (75, int(barvol)), (128, 500), (255, 0, 0), cv2.FILLED)
        if barpercentage > 50:
            cv2.rectangle(frame, (75, int(barvol)), (128, 500), (0, 255, 0), cv2.FILLED)
        if barpercentage >= 75 :
            cv2.rectangle(frame, (75, int(barvol)), (128, 500), (0, 0, 255), cv2.FILLED)
        cTime = time.time()
        if pTime != cTime:
            fps = 1/(cTime-pTime)
        pTime = cTime


    #cv2.putText(frame, f'FPS : {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255,), 3)
    cv2.imshow("video", frame)
    cv2.waitKey(1)