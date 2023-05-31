import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np


# Set the dimensions of the vertical board
desired_width = 1920
desired_height = 1080

cap = cv2.VideoCapture(0)
cap.set(3, desired_width)
cap.set(4, desired_height)
#New image is not set

# Importing all images
imgBackground = cv2.imread("Resources/VSboard.png")
imgGameOver = cv2.imread("Resources/gameOver.png")
imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread("Resources/Hbat1.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Variables
ballPos = [960, 540]
speedX = 20
speedY = 20
gameOver = False
score = [0, 0]
x1 = 0
y1 = 0
w1 = 0
h1 = 0

while True:

    activeHands = False
    left = False
    _, img = cap.read()
    img = cv2.flip(img, 1)
    imgRaw = img.copy()

    hands, img = detector.findHands(img, flipType=False)  # with draw
    # Rest of the code...

    # Resize the imgBackground and img to match the desired dimensions
    imgBackground = cv2.resize(imgBackground, (desired_width, desired_height))
    img = cv2.resize(img, (desired_width, desired_height))

    img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)
    if hands:
        activeHands = True
        for hand in hands:
            x, y, w, h = hand['bbox']
            h1, w1, _ = imgBat1.shape
            tempX = x - w1 // 2
            tempY = y - h1 // 2

            x1 = tempX
            y1 = tempY
            y1 = y1 + 600

            # print(y1)
            y1 = np.clip(y1, 10, 520)
            x1 = np.clip(x1, 330, 1590)

            if hand['type'] == "Left":
                left = True

    if left or activeHands is False:
        if x1 != 0 and y1 != 0:
            # print("left  x: "+str(x)+"y: "+str(y)+"w: "+str(w)+"h: "+str(h))
            img = cvzone.overlayPNG(img, imgBat1, (x1, y1))
            if x1 < ballPos[0] < x1 + w1 and y1 - h1 < ballPos[1] < y1:
                speedY = -speedY
                ballPos[0] += 30

                score[0] += 1


    # Game Over
    if ballPos[0] < 0 or ballPos[0] > 1800:
        gameOver = True

    #if gameOver:
        #img = imgGameOver
        #cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX,
                   #2.5, (200, 0, 200), 5)


    # If game not over move the ball
    else:

        # Move the Ball
        if ballPos[0] >= 1580 or ballPos[0] <= 340:
            speedX = -speedX

        if ballPos[1] >= 1080 or ballPos[1] <= 0:
            speedY = -speedY

        ballPos[0] += speedX
        ballPos[1] += speedY
        print("speedX: " + str(speedX) + "speedY: " + str(speedY) + "ballPose[0]: " + str(
            ballPos[0]) + "ballPos[1]: " + str(ballPos[1]))
        # Draw the ball
        img = cvzone.overlayPNG(img, imgBall, ballPos)

        #cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
        #cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

    #resized_imgRaw = cv2.resize(imgRaw, (213, 120))

    cv2.imshow("Image", img)
    cv2.moveWindow("Image", 0, 0)
    key = cv2.waitKey(1)
    if key == ord('r'):
        ballPos = [150, 450]
        speedX = 20
        speedY = 20
        gameOver = False
        score = [0, 0]
        imgGameOver = cv2.imread("Resources/gameOver.png")

