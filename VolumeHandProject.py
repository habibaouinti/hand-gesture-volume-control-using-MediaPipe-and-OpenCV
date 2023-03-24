import cv2
import mediapipe as mp
import time
import handTrackingModule as htm
import math as m
import numpy as np
###################
#the volume control library imports
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#####################
#to change volume based on the length we will use the library pycaw
#initialisations of volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
##############
print(volume.GetVolumeRange())
#we get that the range is (-65.25, 0.0, 0.03125)
#so 0.0 is maximum and -65.25 is minimum
volrange = volume.GetVolumeRange()
minvol = volrange[0]
maxvol = volrange[1]
#volume.GetMute()
#volume.GetMasterVolumeLevel()
#volume.GetVolumeRange()
#volume.SetMasterVolumeLevel(0, None)
################################
pTime = 0
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
detector = htm.handDetector(detectionCon=0.8)
vol = 100
volperc = 100
volrect = 400
while True:
    success, video = cap.read()
    hands = detector.findHands(video)
    landmarkslist = detector.findPosition(hands, draw=False)
    if len(landmarkslist)!=0 :
        #print(landmarkslist[4],landmarkslist[8])
        # to know the coordinates of the two fingers
        x4, y4 = landmarkslist[4][1], landmarkslist[4][2]
        x8, y8 = landmarkslist[8][1], landmarkslist[8][2]
        # to draw the circles and line on the fingers
        cv2.circle(hands, (x4, y4), 7, (255,0,0), cv2.FILLED)
        cv2.circle(hands, (x8, y8), 7, (255, 0, 0), cv2.FILLED)
        cv2.line(hands, (x4, y4), (x8, y8), (255, 0, 0), 2)
        # to know the median of the line
        cx, cy = (x4+x8)//2, (y4+y8)//2
        cv2.circle(hands, (cx, cy), 7, (255, 0, 0), cv2.FILLED)
        # length of the line
        length = m.hypot(x4-x8, y4-y8)
        #print("length is :", length)
        # converting distance range to volume range
        vol = np.interp(length, [25, 190], [minvol, maxvol])
        volrect = np.interp(length, [25, 190], [400, 150])
        volperc = np.interp(length, [25, 190], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)
        #by testing we can guess that the max is around 225 and the min is around 15
        if length < 25 :
            #changing color to green while on minimum volume
            cv2.circle(hands, (cx, cy), 7, (0, 255, 0), cv2.FILLED)
        if length > 190:
            # changing color to green while on minimum volume
            cv2.circle(hands, (x4, y4), 7, (0, 255, 0), cv2.FILLED)
            cv2.circle(hands, (x8, y8), 7, (0, 255, 0), cv2.FILLED)


        #drawing the rectangle volume range
    cv2.rectangle(video, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(video, (50, int(volrect)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(video, f'{int(volperc)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(video, f'FPS: {int(fps)}', (10, 26), cv2.FONT_HERSHEY_PLAIN, 2,
                (255, 0, 0), 2)
    cv2.imshow("camera video", video)
    cv2.waitKey(1)
