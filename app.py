import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from flask import Flask,render_template,request

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/result",methods = ["POST","GET"])
def result():
    output = request.form.to_dict()
    name = output["File_Path"]
    
    width, height = 1280, 720
    folderPath = name
    imgNumber = 0
    hs, ws = int(120*1), int(213*1)
    gestureThreshold = 300
    buttonPressed = False
    buttonCounter = 0
    buttonDelay = 20
    annotations = [[]]
    annotationNumber = -1
    annotationStart = False
    
    # Camera Setup
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)
    
    # Get The List Of Presentation Images
    pathImages = sorted(os.listdir(folderPath), key=len)
    # print(pathImages)
    
    # Hand Detector
    detector = HandDetector(detectionCon= 0.8, maxHands=1)
    
    while True:
        # Import Images
        success, img = cap.read()
        img = cv2.flip(img,1)
        pathFullImage = os.path.join(folderPath,pathImages[imgNumber])
        imgCurrent = cv2.imread(pathFullImage)
    
        hands, img = detector.findHands(img)
        cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0,255,0), 10)
        if hands and buttonPressed is False:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            cx, cy = hand['center']
            lmList = hand['lmList']
    
            # Constraint values for easier drawing
            xVal = int(np.interp(lmList[8][0],[width//2,w], [0,width]))
            yVal = int(np.interp(lmList[8][1], [150, height-150], [0, height]))
            indexFinger = xVal, yVal
            # print(fingers)
            if cy <= gestureThreshold:
                # Gesture - 1: left
                if fingers == [0, 0, 0, 0, 0]:
                
                    if imgNumber > 0:
                        buttonPressed = True
                        annotations = [[]]
                        annotationNumber = -1
                        annotationStart = False
                        imgNumber -= 1
    
                # Gesture - 2: right
                if fingers == [1, 1, 1, 1, 1]:
                
                    if imgNumber < len(pathImages)-1:
                        buttonPressed = True
                        annotations = [[]]
                        annotationNumber = -1
                        annotationStart = False
                        imgNumber += 1
    
            # Gesture - 3: show pointer
            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(imgCurrent, indexFinger, 12, (0,0,255), cv2.FILLED)
    
            # Gesture - 4: draw
            if fingers == [0, 1, 0, 0, 0]:
                if annotationStart is False:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([])
                cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                annotations[annotationNumber].append(indexFinger)
            else:
                annotationStart = False
    
            # Gesture - 5: erase
            if fingers == [0, 1, 1, 1, 0]:
                if annotations:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = False
        # buttonPressed iterations
        if buttonPressed:
            buttonCounter += 1
            if buttonCounter > buttonDelay:
                buttonCounter = 0
                buttonPressed = False
    
        for i in range (len(annotations)):
            for j in range (len(annotations[i])):
                if j != 0:
                    cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)
    
        # Adding webcam image on slide
        imgSmall = cv2.resize(img, (ws, hs))
        h, w, _ = imgCurrent.shape
        imgCurrent[0:hs,w-ws:w] = imgSmall
    
        # cv2.imshow("Image", img)
        cv2.imshow("Slides", imgCurrent)
    
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    return render_template("index.html",name = folderPath)


if __name__ == '__main__':
    app.run(debug=True,port=5002)