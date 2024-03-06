'''
Single hand Detection 
'''
from cvzone.HandTrackingModule import HandDetector
import cv2


cap = cv2.VideoCapture(0)

detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

while True:

    success, img = cap.read()


    hands, img = detector.findHands(img, draw=True, flipType=True)

    #T,I,M,R,P
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
        print(fingers)
        # if (lengthIM<100 and lengthRP<150 and lengthMR>150 and fingers == [1, 1, 1, 1, 1] ):#SPOCK
        if (lengthIM<lengthPalm//2 and lengthRP<lengthPalm*.75 and lengthMR>lengthPalm*.75 and (fingers == [1, 1, 1, 1, 1] or fingers ==[0, 1, 1, 1, 1] )):#SPOCK
            cv2.putText(img, "SPOCK", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
            print("SPOCK")
        elif (lengthTI<lengthPalm//2 and lengthIM<lengthPalm//2 and lengthRP<lengthPalm//2 and lengthMR<lengthPalm//2 and lengthIB>lengthPalm ):#LIZARD
            print("LIZARD")
            cv2.putText(img, "LIZARD", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        elif fingers == [0, 0, 0, 0, 0] or fingers == [1, 0, 0, 0, 0] :#rock
            print("ROCK")
            cv2.putText(img, "ROCK", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        elif fingers == [1, 1, 1, 1, 1] or fingers == [0, 1, 1, 1, 1] :#paper
            print("PAPER")
            cv2.putText(img, "PAPER", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
        elif fingers == [0, 1, 1, 0, 0] or fingers == [1, 1, 1, 0, 0]:#scissor
            print("SCISSOR")
            cv2.putText(img, "SCISSOR", (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

    cv2.imshow("Image", img)

    cv2.waitKey(1)