import cv2
import HandModule as hm
import time


def findnumber(hand1):
    i = 0
    points = [8, 12, 16, 20]
    tippoints = []
    threshpoints = []
    status = []
    number = 0
    while i < 4:
        tippoints.append(hand1[points[i]])
        threshpoints.append(hand1[points[i] - 3])
        id, cx, cy = tippoints[i][0], tippoints[i][1], tippoints[i][2]
        id, cx1, cy1 = threshpoints[i][0], threshpoints[i][1], threshpoints[i][2]
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        cv2.circle(frame, (cx1, cy1), 5, (0, 0, 255), cv2.FILLED)
        # print(cy, cy1)
        if cy < cy1:
            status.insert(i, 1)
            number = number + 1
        else:
            status.insert(i, 0)
        i = i + 1
    tippoints.append(hand1[4])
    threshpoints.append(hand1[3])
    i, tx, ty = tippoints[4]
    i, tx1, ty1 = threshpoints[4]
    if tx > tx1:
        number += 1
    return number




camw, camh = 960, 720
vid = cv2.VideoCapture(0)
vid.set(3, camw)
vid.set(4, camh)
detector = hm.handDetector(detectionCon=0.8, maxHands= 2)
mainpoints = []
while True :
    number = 0
    hand1 = []
    success, frame = vid.read()
    frame = detector.findHands(frame)
    framelm = detector.findPosition(frame)[0]
    numberofhands = detector.findPosition(frame)[1]
#    numberofhands = detector.findPosition(frame)[1]
#    print(numberofhands)
    if len(framelm) != 0 :
        hand1 = framelm
    if len(hand1) != 0 :
        number = findnumber(hand1)
    cv2.putText(frame, str(number), (0, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 7)
    cv2.waitKey(1)
    cv2.imshow('video', frame)