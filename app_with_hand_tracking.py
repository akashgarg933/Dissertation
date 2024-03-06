'''
Single live hand detection on web
Issue 
- frameRate mismatch
'''

from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np
import ssl
import os
from cvzone.HandTrackingModule import HandDetector

app = Flask(__name__)
socketio = SocketIO(app)


detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

@socketio.on('frame')
def handle_frame(frame_data):
    img_str = frame_data['image'].split(',')[1]
    img_bytes = base64.b64decode(img_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # print("Frame Timestamp:", frame_data['timestamp'])

    hands, img = detector.findHands(img, draw=True, flipType=True)

    if hands:
        hand = hands[0]
        lmList1 = hand["lmList"]
        lengthTI, info, img = detector.findDistance(lmList1[4][0:2], lmList1[8][0:2], img, color=(255, 0, 0),
                                                      scale=10)
        lengthIM, info, img = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img, color=(255, 0, 0),
                                                      scale=10)
        lengthMR, info, img = detector.findDistance(lmList1[12][0:2], lmList1[16][0:2], img, color=(255, 0, 0),
                                                      scale=10)
        lengthRP, info, img = detector.findDistance(lmList1[16][0:2], lmList1[20][0:2], img, color=(255, 0, 0),
                                                      scale=10)
        #tip to base length
        lengthIB, info, img = detector.findDistance(lmList1[8][0:2], lmList1[5][0:2], img, color=(255, 0, 0),
                                                      scale=10)
        lengthMB, info, img = detector.findDistance(lmList1[12][0:2], lmList1[9][0:2], img, color=(255, 0, 0),
                                                      scale=10)
        lengthRB, info, img = detector.findDistance(lmList1[16][0:2], lmList1[13][0:2], img, color=(255, 0, 0),
                                                      scale=10)
        lengthPB, info, img = detector.findDistance(lmList1[20][0:2], lmList1[17][0:2], img, color=(255, 0, 0),
                                                      scale=10)
        
        lengthPalm, info, img = detector.findDistance(lmList1[5][0:2], lmList1[17][0:2], img, color=(255, 0, 0),
                                                      scale=10)

        # print(lengthIB,"<>",lengthMB,"<>",lengthRB,"<>",lengthPB)
        
        # print(lengthPalm)
        # print(lengthIM, lengthRP, lengthMR)

        fingers = detector.fingersUp(hand)
        # print(fingers)
        # if (lengthIM<100 and lengthRP<150 and lengthMR>150 and fingers == [1, 1, 1, 1, 1] ):#SPOCK
        if (lengthIM<lengthPalm//2 and lengthRP<lengthPalm*.75 and lengthMR>lengthPalm*.75 and fingers == [1, 1, 1, 1, 1] ):#SPOCK
            cv2.putText(img, "SPOCK", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
            print("SPOCK")
        elif (lengthTI<lengthPalm//2 and lengthIM<lengthPalm//2 and lengthRP<lengthPalm//2 and lengthMR<lengthPalm//2 and lengthIB>lengthPalm ):#LIZARD
            print("LIZARD")
            cv2.putText(img, "LIZARD", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        elif fingers == [0, 0, 0, 0, 0]:#rock
            print("ROCK")
            cv2.putText(img, "ROCK", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        elif fingers == [1, 1, 1, 1, 1]:#paper
            print("PAPER")
            cv2.putText(img, "PAPER", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        elif fingers == [0, 1, 1, 0, 0]:#scissor
            print("SCISSOR")
            cv2.putText(img, "SCISSOR", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        # Include your hand tracking logic here
    
    # cv2.imshow("Image", img)

    _, buffer = cv2.imencode('.jpg', img)
    img_str = base64.b64encode(buffer)
    img_data = 'data:image/jpeg;base64,' + img_str.decode('utf-8')
    # print("Processed Image:", img_data)
    emit('image', {'image': img_data}
        #  , broadcast=True
         )

@app.route('/')
def index():
    return render_template('index_with_hand_tracking.html')


if __name__ == '__main__':
    # print("password<<")
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key.pem')

    if os.path.exists(cert_path) and os.path.exists(key_path):
        context.load_cert_chain(cert_path, key_path)
    else:
        print("SSL certificate or key file not found. Make sure to provide correct paths.")
        exit(1)

    socketio.run(app,host='0.0.0.0', port=5001, debug=True, ssl_context=context)
    