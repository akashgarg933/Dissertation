# from flask import Flask, render_template, Response
# import cv2
# from cvzone.HandTrackingModule import HandDetector

# app = Flask(__name__)
# cap = cv2.VideoCapture(0)
# detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

# @app.route('/')
# def index():
#     return render_template('index_hand_tracking.html')

# def generate_frames():
#     while True:
#         success, img = cap.read()

#         hands, img = detector.findHands(img, draw=True, flipType=True)

#         if hands:
#             hand = hands[0]
#             lmList1 = hand["lmList"]
#             lengthTI, info, img = detector.findDistance(lmList1[4][0:2], lmList1[8][0:2], img, color=(255, 0, 0),
#                                                           scale=10)
#             lengthIM, info, img = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img, color=(255, 0, 0),
#                                                           scale=10)
#             lengthMR, info, img = detector.findDistance(lmList1[12][0:2], lmList1[16][0:2], img, color=(255, 0, 0),
#                                                           scale=10)
#             lengthRP, info, img = detector.findDistance(lmList1[16][0:2], lmList1[20][0:2], img, color=(255, 0, 0),
#                                                           scale=10)

#             #tip to base length
#             lengthIB, info, img = detector.findDistance(lmList1[8][0:2], lmList1[5][0:2], img, color=(255, 0, 0),
#                                                           scale=10)
#             lengthMB, info, img = detector.findDistance(lmList1[12][0:2], lmList1[9][0:2], img, color=(255, 0, 0),
#                                                           scale=10)
#             lengthRB, info, img = detector.findDistance(lmList1[16][0:2], lmList1[13][0:2], img, color=(255, 0, 0),
#                                                           scale=10)
#             lengthPB, info, img = detector.findDistance(lmList1[20][0:2], lmList1[17][0:2], img, color=(255, 0, 0),
#                                                           scale=10)

#             lengthPalm, info, img = detector.findDistance(lmList1[5][0:2], lmList1[17][0:2], img, color=(255, 0, 0),
#                                                           scale=10)

#             fingers = detector.fingersUp(hand)

#             if (lengthIM < lengthPalm//2 and lengthRP < lengthPalm*.75 and lengthMR > lengthPalm*.75 and fingers == [1, 1, 1, 1, 1]):
#                 cv2.putText(img, "SPOCK", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
#                 print("SPOCK")
#             elif (lengthTI < lengthPalm//2 and lengthIM < lengthPalm//2 and lengthRP < lengthPalm//2 and lengthMR < lengthPalm//2 and lengthIB > lengthPalm):
#                 print("LIZARD")
#                 cv2.putText(img, "LIZARD", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
#             elif fingers == [0, 0, 0, 0, 0]:
#                 print("ROCK")
#                 cv2.putText(img, "ROCK", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
#             elif fingers == [1, 1, 1, 1, 1]:
#                 print("PAPER")
#                 cv2.putText(img, "PAPER", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
#             elif fingers == [0, 1, 1, 0, 0]:
#                 print("SCISSOR")
#                 cv2.putText(img, "SCISSOR", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

#         _, buffer = cv2.imencode('.jpg', img)
#         frame = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     # app.run(debug=True)
#     app.run(host='0.0.0.0', port=5001, debug=True)

##########

from flask import Flask, render_template
import ssl
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key.pem')

    if os.path.exists(cert_path) and os.path.exists(key_path):
        context.load_cert_chain(cert_path, key_path)
    else:
        print("SSL certificate or key file not found. Make sure to provide correct paths.")
        exit(1)

    app.run(host='0.0.0.0', port=5001, debug=True, ssl_context=context)
