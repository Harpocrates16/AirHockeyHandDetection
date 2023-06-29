import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import socket
import threading

count_start = 0
# line 87 imgRaw needs to be fixed
# start sync
#x axis striker bounce thingy
# Locks for synchronization

client_hand_coordinates_lock = threading.Lock()
server_hand_coordinates_lock = threading.Lock()
client_hand_coordinates =[0,0,0,0]
server_hand_coordinates = [500,300,0,0]
right = False
sync =False

def handle_client_communication(conn):
    global client_hand_coordinates
    global server_hand_coordinates
    global right
    global sync
    while True:
        # Receive hand coordinates from the client
        # print("in function")
        data = conn.recv(1024).decode()
        # print("received")
        if not data:
             break

        right = True
        # Parse the received coordinates
        # print("received: "+data+"\n")
        # print("::::")
        sync =True
        x, y, w, h = map(int, data.split(','))
        # print("x: "+str(x)+"y: "+str(y)+"w: "+str(w)+"h: "+str(h))
        #print("Data received: "+data+"\n")
        #data = ""
        # Acquire the data lock to update the hand coordinates
        #with client_hand_coordinates_lock:
        client_hand_coordinates = (x, y, w, h)

            # Acquire the data lock to access the server hand coordinates
        ##with server_hand_coordinates_lock:

            # Get the server hand coordinates
        if(sync):
            server_coordinates = server_hand_coordinates
        # #
        # #     # Send the server hand coordinates back to the client
            if server_coordinates:
                server_data = ','.join(map(str, server_coordinates))
                #print("Data sent: "+server_data+"\n")
                conn.sendall(server_data.encode())
                sync = False
    # conn.close()


def start_game(client_socket):
    global server_hand_coordinates
    global client_hand_coordinates
    global right
    global count_start
    # Set the dimensions of the vertical board
    desired_width = 1280
    desired_height = 720

    cap = cv2.VideoCapture(0)
    cap.set(3, desired_width)
    cap.set(4, desired_height)

    # Importing all images
    imgBackground = cv2.imread("Resources/VSBoard.png")
    imgGameOver = cv2.imread("Resources/gameOver.png")
    imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
    imgBat1 = cv2.imread("Resources/Hbat1.png", cv2.IMREAD_UNCHANGED)
    imgBat2 = cv2.imread("Resources/Hbat1.png", cv2.IMREAD_UNCHANGED)

    # Hand Detector
    detector = HandDetector(detectionCon=0.8, maxHands=2)

    # Variables
    ballPos = [615, 335]

    speedX = 0
    speedY = 0
    gameOver = False
    score = [0, 0]
    lx = 0
    ly = 0
    lw = 0
    lh = 0
    count_bounce = 2
    while True:
        # with client_hand_coordinates_lock:
            # Access and process hand coordinates for each connected client
        #for client_socket, coordinates in client_hand_coordinates.items():
                # Process hand coordinates for the client

                # Example: Access individual coordinates
        rx, ry, rw, rh = client_hand_coordinates
        activeHands = False
        left = False
        _, img = cap.read()
        img = cv2.flip(img, 1)
        # imgRaw = img.copy()

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
                lh, lw, _ = imgBat1.shape
                tempX = x - lw // 2
                tempY = y - lh // 2

                lx = tempX
                ly = tempY
                ly = ly + 300
                #ly = ly + 500
                # print(y1)
                ly = np.clip(ly, 350, 694)
                lx = np.clip(lx, 220, 931)
                # server_hand_coordinates = (lx, ly, lw, lh)
                if hand['type'] == "Left":
                    left = True
                    server_hand_coordinates = (lx, ly, lw, lh)

        if left or activeHands is False:
            if lx != 0 and ly != 0:

                # print("left  x: "+str(x)+"y: "+str(y)+"w: "+str(w)+"h: "+str(h))
                img = cvzone.overlayPNG(img, imgBat1, (lx, ly))
                if lx <= ballPos[0] <= lx + lw and ly - 50 <= ballPos[1] <= ly and count_bounce!= 0:
                    speedY = -speedY
                    count_bounce = 0
                    if (count_start==0):
                        speedY = -20
                        speedX = 20
                        count_start = 1

                elif lx <= ballPos[0] <= lx + lw and ly  <= ballPos[1] <= ly + lh and count_bounce != 0:
                    speedY = -speedY
                    count_bounce = 0
                    # if (count_start == 0):
                    #     speedY = 20
                    #     speedX = 20
                    #     count_start = 1

                # ballPos[0] += speedX
                # ballPos[1] += speedY
                    #with server_hand_coordinates_lock:
                    # server_hand_coordinates = (lx, ly, lw, lh)
                    #print(server_hand_coordinates)

        if right:
            # print("left  x: "+str(x)+"y: "+str(y)+"w: "+str(w)+"h: "+str(h))
            mptW = desired_width // 2
            mptH = desired_height // 2
            ry = ry - 2 * (ry - mptH) - rh
            if rx >= mptW:
                rx = rx - 2 * (rx - mptW) - rw
                # print("first if")
            elif rx < mptW:
                rx = rx + 2 * (mptW - rx) - rw
                # print("Second if")

            img = cvzone.overlayPNG(img, imgBat2, (rx, ry))
            if rx <= ballPos[0] <= rx + rw and ry >= ballPos[1] >= ry - 50 and count_bounce != 1:
                speedY = -speedY
                count_bounce = 1
                if (count_start == 0):
                    speedY = 20
                    speedX = -20
                    count_start = 1

            elif rx <= ballPos[0] <= rx + rw and ry + rh >= ballPos[1] >= ry and count_bounce != 1:
                speedY = -speedY
                count_bounce = 1
                if (count_start == 0):
                    speedY = 20
                    speedX = -20
                    count_start = 1

            # ballPos[0] += speedX
            # ballPos[1] += speedY

        # Have to implement the scoring system logic based on the air hockey scoring area instead of just updating after every
        # slider hit

        # What does incrementing ballPos[0] by 30

        # Game Over
        if ballPos[0] < 0 or ballPos[0] > 1800:
            gameOver = True

        # if gameOver:
        # img = imgGameOver
        # cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX,
        # 2.5, (200, 0, 200), 5)

        # If game not over move the ball
        else:

            # Move the Ball
            if ballPos[0] >= 1010 or ballPos[0] <= 230:
                count_bounce = 2
                speedX = -speedX

            if ballPos[1] >= 670 or ballPos[1] <= 10:
                count_bounce = 2
                speedY = -speedY

            ballPos[0] += speedX
            ballPos[1] += speedY
            ballPos[0] = np.clip(ballPos[0], 220, 1010)
            ballPos[1] = np.clip(ballPos[1], 0, 670)
            #print("X ball "+str(ballPos[0])+"y: "+str(ballPos[1])+"lx: "+str(lx)+"ly: "+str(ly)+"lw: "+str(lw)+"lh: "+str(lh))
            # print("speedX: " + str(speedX) + "speedY: " + str(speedY) + "ballPose[0]: " + str(
            #     ballPos[0]) + "ballPos[1]: " + str(ballPos[1]))
            # Draw the ball
            img = cvzone.overlayPNG(img, imgBall, ballPos)

            # cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
            # cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

        # resized_imgRaw = cv2.resize(imgRaw, (213, 120))

        cv2.imshow("Image", img)
        print(str(count_bounce)+"\n")
        # cv2.moveWindow("Image", 0, 0)
        key = cv2.waitKey(1)
        if key == ord('r'):
            ballPos = [615, 335]
            speedX = 0
            speedY = 0
            count_bounce=2
            gameOver = False
            score = [0, 0]
            imgGameOver = cv2.imread("Resources/gameOver.png")


def server_program():
    host = socket.gethostname()
    port = 2000

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)

    print(host+" Server started. Waiting for connections...")

    while True:
        client_socket, addr = server_socket.accept()
        print("Connected with", addr)

        # Start the game in a separate thread
        game_thread = threading.Thread(target=start_game,args=(client_socket,))
        game_thread.start()

        # Create a new thread to handle the client connection
        client_thread = threading.Thread(target=handle_client_communication, args=(client_socket,))
        client_thread.start()

        game_thread.join()
        client_thread.join()

        client_socket.close()


if __name__ == '__main__':
    server_program()