'''
Game ran on Flask Server 
'''
from flask import Flask, render_template, Response,request, jsonify,session
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np
import ssl
import os
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time
import random

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

P1last3=[]
P2last3=[]

player1name = "PLAYER 1"
player2name="PLAYER 2"

gameMode ="multiplayer"

def addMoveP1(move):
    P1last3.append(move)
    if len(P1last3) > 3:
        P1last3.pop(0)

def addMoveP2(move):
    P2last3.append(move)
    if len(P2last3) > 3:
        P2last3.pop(0)

ROCK = 1
PAPER = 2
SCISSORS = 3
SPOCK = 4
LIZARD = 5

playerMoveP1 = 0
playerMoveP2 = 0

keyPress=0

movelist = {1: "ROCK", 2: "PAPER", 3: "SCISSORS", 4: "SPOCK", 5: "LIZARD"}
# movelistByNo = { "ROCK":1, "PAPER":2, "SCISSORS":3,  "SPOCK":4, "LIZARD":5}

@app.route('/')
def index():
    return render_template('index_with_hand_tracking.html')

@socketio.on('key_input')
def handle_key_input(data):
    try :
        key = data['key']
        # print("Key pressed:", key)
        global keyPress
        keyPress=key
    except Exception as e :
        print(e)

@app.route('/send_value', methods=['POST'])
def send_value():
    global startGame,initialTime,stateResult,keyPress
    data = request.get_json()
    button_value = data.get('value')
    print("Received button value:", button_value)
    if button_value == 'Start':
        startGame = True
        initialTime = time.time()
        stateResult = False
        keyPress=0

@app.route('/reset_value', methods=['POST'])
def reset_value():
    global scores,P1last3,P2last3
    data = request.get_json()
    button_value = data.get('value')
    print("Received button value:", button_value)
    if button_value == 'reset':
        scores = [0, 0]
        P1last3=[]
        P2last3=[]
    return {'status': 'success'}


def stitch_images(image_paths, target_width, target_height, spacing, x, y,imgBG):
    temp=[]
    for i in image_paths:
            temp.append(f"Resources/svgtopng/{i}.png")
    image_paths=temp
    # Load and resize all images
    images = [cv2.resize(cv2.imread(path), (target_width, target_height)) for path in image_paths]
    # print(imgBG.shape)
    for i in images:
        # cv2.imshow("i",i)
        imgBG=overlay_image(imgBG,i,x,y)
        x+=(spacing+target_width)
    return imgBG


def overlay_image(base_image, overlay_image, x, y):
    # Get dimensions of the overlay image
    overlay_height, overlay_width, _ = overlay_image.shape

    # Get dimensions of the base image
    base_height, base_width, _ = base_image.shape

    # Calculate the region of interest (ROI) where the overlay image will be placed
    roi = base_image.copy()
    x1, y1 = x, y
    x2, y2 = min(x + overlay_width, base_width), min(y + overlay_height, base_height)

    # Overlay the image onto the base image within the ROI
    roi[y1:y2, x1:x2] = overlay_image[:y2-y1, :x2-x1]

    return roi

@app.route('/process_form', methods=['POST'])
def process_form():
    global player1name,player2name,gameMode
    # Get form data from request
    data = request.json

    gameMode = data.get('gameMode')

    if(gameMode=='single'):
        player2name="AI"
        if(data.get('player1Name')!=""):
            player1name=data.get('player1Name')
    else:
        if(data.get('player1Name')!=""):
            player1name=data.get('player1Name')
        if(data.get('player2Name')!=""):
            player2name=data.get('player2Name')
    return {'status': 'success'}

@socketio.on('frame')
def generate_frames(frame_data):
    global startGame, stateResult, timer, scores, playerMoveP1, playerMoveP2,initialTime,keyPress,gameMode,player1name,player2name
    img_str = frame_data['image'].split(',')[1]
    img_bytes = base64.b64decode(img_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    screenW=frame_data['width']
    screenH=frame_data['height']
    
    # print("Frame Timestamp:", frame_data['timestamp'])
    # while True:

    if player1name == "" and player2name == "":
        imgBG = cv2.imread("Resources/BG_NEW.png")
    else:
        imgBG = cv2.imread("Resources/BG_LATEST.png")

    imgScaled=img
    width, height, _ = imgScaled.shape
    imgLeft = imgScaled[:, :(height // 2)]
    imgRight = imgScaled[:, (height // 2):]

    # Draw a line down the center of the frame
    cv2.line(imgScaled, (height // 2, 0), (height // 2, height), (255, 255, 255), 2)

    # Find Hands for Player 1 (Left side)
    handsP1, imgP1 = detectorP1.findHands(imgLeft)

    # Find Hands for Player 2 (Right side)
    if gameMode != 'single':
        handsP2, imgP2 = detectorP2.findHands(imgRight)

    if startGame:
        if stateResult is False:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                timer = 0
                print(gameMode)
                # print(handP1)
                if ((gameMode == 'multiplayer' and handsP1 and handsP2) or (gameMode == 'single' and  handsP1)):
                    handP1 = handsP1[0]
                    lmListP1 = handP1["lmList"]
                    fingersP1 = detectorP1.fingersUp(handP1)
                    if gameMode != 'single':
                        handP2 = handsP2[0]
                        lmListP2 = handP2["lmList"]
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
                    # print("game mode is "+gameMode)
                    if gameMode!='single':
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

                    if(gameMode=='single'):
                        playerMoveP2=random.randint(1, 5)

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
                    if(playerMoveP1!=0 and playerMoveP2!=0):
                        addMoveP1(movelist[playerMoveP1])
                        addMoveP2(movelist[playerMoveP2])
    #Left  player 1
    #Right player 2
                        
    # print('random ',playerMoveP2)
    if gameMode != 'single': 
        # print("game is multiplayer")                   
        imgBG[234:654, 93:493] = cv2.flip(cv2.resize(imgP2, (400, 420), None, 2, 1),1)
    elif(playerMoveP2!=0):
        imgBG=overlay_image(imgBG,cv2.imread(f"Resources/svgtopng/{str(movelist[playerMoveP2])}.png"),137,300)
        # imgBG[234:654, 93:493] = cv2.resize(cv2.imread(f"Resources/svgtopng/{str(playerMoveP2)}.png"), (400, 420))

    # imgBG[234:654, 93:493]   = cv2.flip(cv2.resize(imgP2, (400, 420), None, 2, 1),1)
    imgBG[234:654, 795:1195] = cv2.flip(cv2.resize(imgP1, (400, 420), None, 2, 1),1)



    if(playerMoveP1!=0 and playerMoveP2!=0):
        imgBG=stitch_images(P2last3,50,50,30,180,250,imgBG)
        imgBG=stitch_images(P1last3,50,50,30,882,250,imgBG)


    cv2.putText(imgBG, str(scores[1]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[0]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    
    if gameMode == 'single':
        cv2.putText(imgBG, str(player2name), (110, 205), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 5)
        cv2.putText(imgBG, str(player1name), (812, 205), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 5)
    else:
        cv2.putText(imgBG, str(player1name), (110, 205), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 5)
        cv2.putText(imgBG, str(player2name), (812, 205), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 5)       

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
