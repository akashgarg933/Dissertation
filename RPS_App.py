'''
Game ran on Flask Server 
'''
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np
import ssl
import os
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

app = Flask(__name__)
socketio = SocketIO(app)

# detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
detectorP1 = HandDetector(maxHands=1)
detectorP2 = HandDetector(maxHands=1)


timer = 0
initialTime = time.time()
stateResult = False
startGame = False
scores = [0, 0]

ROCK = 1
PAPER = 2
SCISSORS = 3
SPOCK = 4
LIZARD = 5

playerMoveP1 = 0
playerMoveP2 = 0

keyPress=0

movelist = {1: "ROCK", 2: "PAPER", 3: "SCISSORS", 4: "SPOCK", 5: "LIZARD"}

@app.route('/')
def index():
    return render_template('index_with_hand_tracking.html')

@socketio.on('key_input')
def handle_key_input(data):
    key = data['key']
    # print("Key pressed:", key)
    global keyPress
    keyPress=key

@socketio.on('frame')
def generate_frames(frame_data):
    global startGame, stateResult, timer, scores, playerMoveP1, playerMoveP2,initialTime,keyPress
    img_str = frame_data['image'].split(',')[1]
    img_bytes = base64.b64decode(img_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    screenW=frame_data['width']
    screenH=frame_data['height']
    
    # print("Frame Timestamp:", frame_data['timestamp'])
    # while True:
    imgBG = cv2.imread("Resources/BG_NEW.png")
    imgScaled=img
    width, height, _ = imgScaled.shape
    imgLeft = imgScaled[:, :(height // 2)]
    imgRight = imgScaled[:, (height // 2):]

    # Draw a line down the center of the frame
    cv2.line(imgScaled, (height // 2, 0), (height // 2, height), (255, 255, 255), 2)

    # Find Hands for Player 1 (Left side)
    handsP1, imgP1 = detectorP1.findHands(imgLeft)

    # Find Hands for Player 2 (Right side)
    handsP2, imgP2 = detectorP2.findHands(imgRight)

    if startGame:
        if stateResult is False:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                timer = 0

                if handsP1 and handsP2:
                    handP1 = handsP1[0]
                    handP2 = handsP2[0]
                    lmListP1 = handP1["lmList"]
                    lmListP2 = handP2["lmList"]
                    fingersP1 = detectorP1.fingersUp(handP1)
                    fingersP2 = detectorP2.fingersUp(handP2)

                    P1lengthTI, info, imgP1 = detectorP1.findDistance(lmListP1[4][0:2], lmListP1[8][0:2], imgP1, color=(255, 0, 0),
                                                    scale=10)
                    P1lengthIM, info, imgP1 = detectorP1.findDistance(lmListP1[8][0:2], lmListP1[12][0:2], imgP1, color=(255, 0, 0),
                                                    scale=10)
                    P1lengthMR, info, imgP1 = detectorP1.findDistance(lmListP1[12][0:2], lmListP1[16][0:2], imgP1, color=(255, 0, 0),
                                                    scale=10)
                    P1lengthRP, info, imgP1 = detectorP1.findDistance(lmListP1[16][0:2], lmListP1[20][0:2], imgP1, color=(255, 0, 0),
                                                    scale=10)
                    
                    P1lengthPalm, info, imgP1 = detectorP1.findDistance(lmListP1[5][0:2], lmListP1[17][0:2], imgP1, color=(255, 0, 0),
                                                    scale=10)
                    
                    P1lengthIB, info, imgP1 = detectorP1.findDistance(lmListP1[8][0:2], lmListP1[5][0:2], imgP1, color=(255, 0, 0),
                                                    scale=10)
                    
                    P2lengthTI, info, imgP2 = detectorP2.findDistance(lmListP2[4][0:2], lmListP2[8][0:2], imgP2, color=(255, 0, 0),
                                                    scale=10)
                    P2lengthIM, info, imgP2 = detectorP2.findDistance(lmListP2[8][0:2], lmListP2[12][0:2], imgP2, color=(255, 0, 0),
                                                    scale=10)
                    P2lengthMR, info, imgP2 = detectorP2.findDistance(lmListP2[12][0:2], lmListP2[16][0:2], imgP2, color=(255, 0, 0),
                                                    scale=10)
                    P2lengthRP, info, imgP2 = detectorP2.findDistance(lmListP2[16][0:2], lmListP2[20][0:2], imgP2, color=(255, 0, 0),
                                                    scale=10)
                    
                    P2lengthPalm, info, imgP2 = detectorP2.findDistance(lmListP2[5][0:2], lmListP2[17][0:2], imgP2, color=(255, 0, 0),
                                                    scale=10)
                    
                    P2lengthIB, info, imgP2 = detectorP2.findDistance(lmListP2[8][0:2], lmListP2[5][0:2], imgP2, color=(255, 0, 0),
                                                    scale=10)
                    
                    if (P1lengthIM<P1lengthPalm//2 and P1lengthRP<P1lengthPalm*.75 and P1lengthMR>P1lengthPalm*.75 and fingersP1 == [1, 1, 1, 1, 1]):#SPOCK
                        print("SPOCK")
                        playerMoveP1 = 4
                    elif (P1lengthTI<P1lengthPalm//2 and P1lengthIM<P1lengthPalm//2 and P1lengthRP<P1lengthPalm//2 and P1lengthMR<P1lengthPalm//2 and P1lengthIB>P1lengthPalm  ):#LIZARD
                        print("LIZARD")
                        playerMoveP1 = 5
                    elif fingersP1 == [0, 0, 0, 0, 0]:#rock
                        print("ROCK")
                        playerMoveP1 = 1
                    elif fingersP1 == [1, 1, 1, 1, 1]:#paper
                        print("PAPER")
                        playerMoveP1 = 2
                    elif fingersP1 == [0, 1, 1, 0, 0]:#scissor
                        print("SCISSOR")
                        playerMoveP1 = 3 

                    if (P2lengthIM<P2lengthPalm//2 and P2lengthRP<P2lengthPalm*.75 and P2lengthMR>P2lengthPalm*.75 and fingersP2 == [1, 1, 1, 1, 1] ):#SPOCK
                        print("SPOCK")
                        playerMoveP2 = 4
                    elif (P2lengthTI<P2lengthPalm//2 and P2lengthIM<P2lengthPalm//2 and P2lengthRP<P2lengthPalm//2 and P2lengthMR<P2lengthPalm//2 and P2lengthIB>P2lengthPalm ):#LIZARD
                        print("LIZARD")
                        playerMoveP2 = 5
                    elif fingersP2 == [0, 0, 0, 0, 0]:#rock
                        print("ROCK")
                        playerMoveP2 = 1
                    elif fingersP2 == [1, 1, 1, 1, 1]:#paper
                        print("PAPER")
                        playerMoveP2 = 2
                    elif fingersP2 == [0, 1, 1, 0, 0]:#scissor
                        print("SCISSOR")
                        playerMoveP2 = 3                 

                    if (playerMoveP1 == ROCK and (playerMoveP2 == SCISSORS or playerMoveP2 == LIZARD)) or \
                            (playerMoveP1 == PAPER and (playerMoveP2 == ROCK or playerMoveP2 == SPOCK)) or \
                            (playerMoveP1 == SCISSORS and (playerMoveP2 == PAPER or playerMoveP2 == LIZARD)) or \
                            (playerMoveP1 == LIZARD and (playerMoveP2 == SPOCK or playerMoveP2 == PAPER)) or \
                            (playerMoveP1 == SPOCK and (playerMoveP2 == SCISSORS or playerMoveP2 == ROCK)):
                        scores[0] += 1  # Player 1 wins
                    elif (playerMoveP2 == ROCK and (playerMoveP1 == SCISSORS or playerMoveP1 == LIZARD)) or \
                            (playerMoveP2 == PAPER and (playerMoveP1 == ROCK or playerMoveP1 == SPOCK)) or \
                            (playerMoveP2 == SCISSORS and (playerMoveP1 == PAPER or playerMoveP1 == LIZARD)) or \
                            (playerMoveP2 == LIZARD and (playerMoveP1 == SPOCK or playerMoveP1 == PAPER)) or \
                            (playerMoveP2 == SPOCK and (playerMoveP1 == SCISSORS or playerMoveP1 == ROCK)):
                        scores[1] += 1  # Player 2 wins
                    
    imgBG[234:654, 795:1195] = cv2.flip(cv2.resize(imgP1, (400, 420), None, 2, 1),1)
    imgBG[234:654, 93:493] = cv2.flip(cv2.resize(imgP2, (400, 420), None, 2, 1),1)
    if(playerMoveP1!=0 and playerMoveP2!=0):
        cv2.putText(imgBG, movelist[playerMoveP2], (210, 290), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        cv2.putText(imgBG, movelist[playerMoveP1], (912, 290), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[0]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    # cv2.imshow("RPS", imgBG)
    
    # key = cv2.waitKey(1)
    if keyPress == 81:#key press 'q'
        pass
        # break
    if keyPress == 32:#Space key count
        # print("PRESSED SPACE")
        startGame = True
        initialTime = time.time()
        stateResult = False
        keyPress=0

    _, buffer = cv2.imencode('.jpg', imgBG)
    # _, buffer = cv2.imencode('.jpg', img)

    img_str = base64.b64encode(buffer)
    img_data = 'data:image/jpeg;base64,' + img_str.decode('utf-8')
    socketio.emit('image', {'image': img_data}
                #   , broadcast=True
                    )
    time.sleep(0.1)  # Adjust the sleep time as needed

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key.pem')

    if os.path.exists(cert_path) and os.path.exists(key_path):
        context.load_cert_chain(cert_path, key_path)
    else:
        print("SSL certificate or key file not found. Make sure to provide correct paths.")
        exit(1)

    socketio.run(app, host='0.0.0.0', port=5001, debug=True, ssl_context=context)
