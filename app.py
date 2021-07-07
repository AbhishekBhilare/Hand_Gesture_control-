from flask import Flask, jsonify, render_template, Response, request
import warnings
import requests

warnings.simplefilter(action='ignore', category=FutureWarning)

app = Flask(__name__)
parameters = {}
URL = "https://script.google.com/macros/s/AKfycbzt8-itmp9y1fgnsd1MNiaG1UQeDQWQM5ga_In9qnuWlMWyq8mzyQ-HcqwtYAHS_37F/exec"
LED = ''
FAN = ''
#response = requests.get(URL, params=parameters)

import cv2
import mediapipe as mp
# from handDetector import HandDetector

results = None
# import pyautogui
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
##################################
tipIds = [4, 8, 12, 16, 20]
state = None
Gesture = None
wCam, hCam = 720, 640
detected = ''

count = 0
############################
def fingerPosition(image, handNo=0):
    lmList = []
    global results
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            # print(id,lm)
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])
    return lmList

def mp_recog():
    global results
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    ##################################
    global tipIds
    global count
    global detected
    #state = None
    #Gesture = None
    global wCam
    global hCam
    global parameters
    global URL
    global response
    global LED
    global FAN
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    with mp_hands.Hands(
            min_detection_confidence=0.8,
            min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            count = count+1
            success, image = cap.read()
            #handLandmarks = HandDetector.findHandLandMarks(image=image, draw=True)
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue
            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lmList = fingerPosition(image)
            # print(lmList)
            if len(lmList) != 0:
                fingers = []
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        # state = "Play"
                        fingers.append(1)
                    if (lmList[tipIds[id]][2] > lmList[tipIds[id] - 2][2]):
                        # state = "Pause"
                        # pyautogui.press('space')
                        # print("Space")
                        fingers.append(0)
                totalFingers = fingers.count(1)
                # print(totalFingers)
                # print(lmList[9][2])
                #if handLandmarks[8][2]>handLandmarks[6][2] and handLandmarks[12][2]>handLandmarks[10][2] and handLandmarks[16][2]<handLandmarks[13][2]:
                 #   print("V")
                if totalFingers == 1:
                    detected = "Fan ON"
                    FAN = 'ON'
                    print("Fan ON")
                if totalFingers == 2:
                    detected = "Fan OFF"
                    FAN = 'OFF'
                    print("Fan OFF")
                if totalFingers == 3:
                    detected = "LED ON"
                    LED = 'ON'
                    print("LED ON")
                if totalFingers == 4:
                    detected = "LED OFF"
                    LED = 'OFF'
                    print("LED OFF")

            parameters = {"id":"Sheet1","LED":LED,"FAN":FAN}
            #requests.get(URL, params=parameters)
                        # pyautogui.press('Down')
            cv2.putText(image, detected, (10,40), cv2.FONT_HERSHEY_SIMPLEX,
                          1, (255, 0, 0), 2)
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        if username == "team1" and password == "abcd":
            msg = 'Logged in successfully !'
            return render_template('About.html', msg = msg)
        elif username == "team2" and password == "1234":
            msg = 'Logged in successfully !'
            return render_template('About.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('LOGIN PAGE.html', msg = msg)

@app.route('/home')
def home():
    return render_template('About.html')

@app.route('/status')
def status():
    return render_template('Status_page.html')

@app.route('/video_feed')
def video_feed():
    return Response(mp_recog(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/about')
def about():
    return render_template('HOME_PAGE.html')

if __name__ == "__main__":
    app.run(debug=True)
