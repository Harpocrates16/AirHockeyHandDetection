import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time
import sqlite3
import os

# recieve Player names from GUI
value1 = os.environ["P1"]
value2 = os.environ["P2"]
print("Received from GUI: ", value1, value2)

# database connection
connection = sqlite3.connect('airhockey.db')
c = connection.cursor()
# c.execute("create table scoreset(name text, leftscore int, rightscore int, timecol time)");
# c.execute("create table temp_scoreset(name text, leftscore int, rightscore int, timecol time)")
query1 = "insert into scoreset values(?, ?, ?)"
execcnt = 0

def close_window(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.destroyAllWindows()

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Importing all images
imgBackground = cv2.imread("Resources/Background.png")
imgGameOver = cv2.imread("Resources/gameOver.png")
imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread("Resources/bat1.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Variables
ballPos = [100, 100]
speedX = 15
speedY = 15
gameOver = False
score = [0, 0]

# Stopwatch variables
start_time = time.time()

cv2.namedWindow('Image')
cv2.setMouseCallback('Image', close_window)

while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)
    imgRaw = img.copy()

    # Find the hand and its landmarks
    hands, img = detector.findHands(img, flipType=False)  # with draw

    # Overlaying the background image
    img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

    # Check for hands
    if hands:
        for hand in hands:
            x, y, w, h = hand['bbox']
            h1, w1, _ = imgBat1.shape
            y1 = y - h1 // 2
            x1 = x - w1 // 2
            y1 = np.clip(y1, 20, 415)

            if hand['type'] == "Left":
                img = cvzone.overlayPNG(img, imgBat1, (x1, y1))
                if x1 < ballPos[0] < x1 + w1 and y1 < ballPos[1] < y1 + h1:
                    speedX = -speedX
                    ballPos[0] += 30
                    score[0] += 1

            if hand['type'] == "Right":
                img = cvzone.overlayPNG(img, imgBat2, (x1, y1))
                if x1 - 50 < ballPos[0] < x1 and y1 < ballPos[1] < y1 + h1:
                    speedX = -speedX
                    ballPos[0] -= 30
                    score[1] += 1

    # Game Over
    if ballPos[0] < 40 or ballPos[0] > 1200:
        gameOver = True

    if gameOver:
        img = imgGameOver
        cv2.putText(img, str(score[0]).zfill(2), (370, 360), cv2.FONT_HERSHEY_COMPLEX, 2.5, (200, 0, 200), 5)
        cv2.putText(img, str(score[1]).zfill(2), (800, 360), cv2.FONT_HERSHEY_COMPLEX, 2.5, (200, 0, 200), 5)

        if start_time is not None:
            elapsed_time = time.time() - start_time
            formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            print("Elapsed Time: ", formatted_time)
            start_time = None  # Reset start_time to None

        # update database
        if execcnt == 0:
            if score[0] > score[1]:
                c.execute(query1, (value1, score[0], formatted_time,))
                c.execute("insert into temp_scoreset select * from scoreset order by timecol ASC")
                c.execute("delete from scoreset")
                c.execute("insert into scoreset select * from temp_scoreset")
                c.execute("delete from temp_scoreset")
                connection.commit()
            else:
                c.execute(query1, (value2, score[1], formatted_time,))
                c.execute("insert into temp_scoreset select * from scoreset order by timecol ASC")
                c.execute("delete from scoreset")
                c.execute("insert into scoreset select * from temp_scoreset")
                c.execute("delete from temp_scoreset")
                connection.commit()
        execcnt = execcnt+1

    else:
        # If game not over move the ball
        # Move the Ball
        if ballPos[1] >= 500 or ballPos[1] <= 10:
            speedY = -speedY

        ballPos[0] += speedX
        ballPos[1] += speedY

        # Draw the ball
        img = cvzone.overlayPNG(img, imgBall, ballPos)

        cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
        cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

    img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

    # Stopwatch display
    if start_time is not None:
        elapsed_time = time.time() - start_time
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        cv2.putText(img, formatted_time, (550, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Image", img)

    # Check for keyboard input
    key = cv2.waitKey(1)
    if key == ord('r'):
        ballPos = [100, 100]
        speedX = 15
        speedY = 15
        gameOver = False
        score = [0, 0]
        imgGameOver = cv2.imread("Resources/gameOver.png")
        start_time = time.time()  # Reset stopwatch
        print("Game Restarted")
        execcnt = 0

    if cv2.getWindowProperty('Image', cv2.WND_PROP_VISIBLE) < 1:
        break

# Release the VideoCapture object and close the windows
cap.release()
cv2.destroyAllWindows()
