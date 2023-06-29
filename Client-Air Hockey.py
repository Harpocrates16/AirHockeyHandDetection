import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import socket
import threading


# Locks for synchronization
"""
client_hand_coordinates_lock = threading.Lock()
server_hand_coordinates_lock = threading.Lock()
"""
client_hand_coordinates = [500, 300, 0, 0]
server_hand_coordinates = [0, 0, 0, 0]

left = False
count_start = 0
data = ''
sync = True
def handle_server_communication(conn, client_socket):
    global client_hand_coordinates
    global server_hand_coordinates
    global left
    global data
    global sync
    while True:
        # Receive hand coordinates from the server

        if sync:
            client_coordinates = client_hand_coordinates#.get(conn)

                # Send the client hand coordinates back to the server
            #if client_coordinates:
            data = ''
            data = ','.join(map(str, client_coordinates))
            #print(data)
            client_socket.sendall(data.encode())
            #print("Data sent!")
            sync = False
        data = client_socket.recv(1024).decode()
        #print("Data recieved ")
        if not data:
            break

        left = True
        # Parse the received coordinates
        x, y, w, h = map(int, data.split(','))
        # Acquire the data lock to update the hand coordinates
        #with server_hand_coordinates_lock:
        server_hand_coordinates = (x, y, w, h)
        #print("x="+str(x)+",y="+str(y)+",w="+str(w)+",h="+str(h))
        sync = True
            # Acquire the data lock to access the client hand coordinates

        #with client_hand_coordinates_lock:
                # Get the client hand coordinates



    #conn.close()

#testing of positioning of hand coordinates
#implement dynamic sizing of img for screen resolution
def start_game(client_socket):
    global left
    global count_start
    global server_hand_coordinates
    global client_hand_coordinates
    # Set the dimensions of the vertical board
    desired_width = 1280
    desired_height = 720
    print("********************************Entered game function******************************\n")
    cap = cv2.VideoCapture(0)
    cap.set(3, desired_width)
    cap.set(4, desired_height)


    # Importing all images
    imgBackground = cv2.imread("Resources/VSboard.png")
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
    rx = 0
    ry = 0
    rw = 0
    rh = 0

    count_bounce = 2
    while True:
        #with server_hand_coordinates_lock:
            # Access and process hand coordinates for each connected client
        #for client_socket, coordinates in server_hand_coordinates.items():
                # Process hand coordinates for the client

                # Example: Access individual coordinates



        activeHands = False
        right = False
        _, img = cap.read()
        img = cv2.flip(img, 1)
        #imgRaw = img.copy()

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
                rh, rw, _ = imgBat1.shape
                tempX = x - rw // 2
                tempY = y - rh // 2

                rx = tempX
                ry = tempY
                #ry = ry + 500
                ry = ry + 300
                rx = rx + 300
                # print(y1)
                #ry = np.clip(ry, 600, 730)
                ry = np.clip(ry, 360, 694)
                rx = np.clip(rx, 220, 931)
                client_hand_coordinates = (rx, ry, rw, rh)


                if hand['type'] == "Right":
                    right = True
        print("count bounce: ")
        print(count_bounce)
        if right or activeHands is False:
            if rx != 0 and ry != 0:
                # with client_hand_coordinates_lock:
                client_hand_coordinates = (rx, ry, rw, rh)

                # print("left  x: "+str(x)+"y: "+str(y)+"w: "+str(w)+"h: "+str(h))
                img = cvzone.overlayPNG(img, imgBat1, (rx, ry))
                if count_bounce != 1:
                    if rx <= ballPos[0] <= rx + rw and ry - 50 <= ballPos[1] <= ry:
                        speedY = -speedY
                        count_bounce = 1
                        if(count_start == 0):
                            speedX = 20
                            speedY = -20
                            count_start = 1
                    elif rx < ballPos[0] <= rx + rw and ry <= ballPos[1] <= ry + rh:
                        speedY = -speedY
                        count_bounce = 1







        if left:

                lx, ly, lw, lh = server_hand_coordinates
                #print(str(lx)+','+str(ly)+','+str(lw)+','+str(lh))

                # print("left  x: "+str(x)+"y: "+str(y)+"w: "+str(w)+"h: "+str(h))
                mptW = desired_width//2
                mptH = desired_height//2

                ly = ly - 2*(ly - mptH) - lh
                if lx >= mptW:
                    lx = lx - 2*(lx - mptW) - lw
                elif lx < mptW:
                    lx = lx + 2*(mptW - lx) - lw


#start synchronization of ball
#x axis striker limits
                img = cvzone.overlayPNG(img, imgBat2, (lx, ly))
                if count_bounce != 0:
                    if lx <= ballPos[0] <= lx + lw and ly >= ballPos[1] >= ly - 50:
                        speedY = -speedY
                        count_bounce = 0

                    elif lx <= ballPos[0] <= lx + lw and ly + lh >= ballPos[1] >= ly:
                        speedY = -speedY
                        count_bounce = 0
                        if (count_start == 0):
                            speedX = -20
                            speedY = 20
                            count_start = 1






#Have to implement the scoring system logic based on the air hockey scoring area instead of just updating after every
#slider hit





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
            if ballPos[0] >= 1010 or ballPos[0] <= 230:
                speedX = -speedX
                count_bounce = 2

            if ballPos[1] >= 670 or ballPos[1] <= 10:
                speedY = -speedY
                count_bounce = 2

            ballPos[0] += speedX
            ballPos[1] += speedY
            #print("speedX: " + str(speedX) + "speedY: " + str(speedY) + "ballPose[0]: " + str(ballPos[0]) + "ballPos[1]: " + str(ballPos[1]))
            # Draw the ball
            ballPos[0] = np.clip(ballPos[0], 220, 1010)
            ballPos[1] = np.clip(ballPos[1], 0, 670)
            print('x:'+str(ballPos[0])+' ,y:'+str(ballPos[1]))
            img = cvzone.overlayPNG(img, imgBall, ballPos)

            #cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
            #cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

        #resized_imgRaw = cv2.resize(imgRaw, (213, 120))

        cv2.imshow("Image", img)
        #cv2.moveWindow("Image", 0, 0)
        key = cv2.waitKey(1)
        if key == ord('r'):
            ballPos = [615, 335]
            speedX = 20
            speedY = 20
            gameOver = False
            score = [0, 0]
            imgGameOver = cv2.imread("Resources/gameOver.png")


def client_program(conn=None):
    host = "192.168.111.67"
    port = 2000

    # Create a client socket and connect to the server
    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Create a thread for game logic
    game_thread = threading.Thread(target=start_game, args=(client_socket,))
    game_thread.start()

    # Create a thread for server communication
    server_comm_thread = threading.Thread(target=handle_server_communication, args=(conn, client_socket,))
    server_comm_thread.start()


    game_thread.join()
    server_comm_thread.join()


    client_socket.close()


if __name__ == '__main__':
    client_program()
