import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import socket
import threading


# Locks for synchronization

client_hand_coordinates_lock = threading.Lock()
server_hand_coordinates_lock = threading.Lock()
client_hand_coordinates = {}
server_hand_coordinates = {}
left = False
def handle_server_communication(conn,client_socket):
    global left
    while True:
        # Receive hand coordinates from the server
        data = client_socket.recv(1024).decode()
        if not data:
            break

        left = True
        # Parse the received coordinates
        x, y, w, h = map(int, data.split(','))
        # Acquire the data lock to update the hand coordinates
        with server_hand_coordinates_lock:
            server_hand_coordinates[conn] = (x, y, w, h)

            # Acquire the data lock to access the client hand coordinates
        with client_hand_coordinates_lock:
                # Get the client hand coordinates
            client_coordinates = client_hand_coordinates.get(conn)

            # Send the client hand coordinates back to the server
        if client_coordinates:
            data = ','.join(map(str, client_coordinates))
            client_socket.sendall(data.encode())

    conn.close()

def send_coordinates(client_socket, coordinates):
    # Send hand coordinates to the server
    data = ','.join(map(str, coordinates))
    client_socket.sendall(data.encode())

def receive_coordinates(client_socket):
    # Receive server hand coordinates from the server
    data = client_socket.recv(1024).decode()
    if data:
        coordinates = tuple(map(int, data.split(',')))
        return coordinates
    return None


def start_game():
    global left
    # Set the dimensions of the vertical board
    desired_width = 350
    desired_height = 800

    cap = cv2.VideoCapture(0)
    cap.set(3, desired_width)
    cap.set(4, desired_height)


    # Importing all images
    imgBackground = cv2.imread("Resources/vertical_board.png")
    imgGameOver = cv2.imread("Resources/gameOver.png")
    imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
    imgBat1 = cv2.imread("Resources/Hbat1.png", cv2.IMREAD_UNCHANGED)
    imgBat2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)

    # Hand Detector
    detector = HandDetector(detectionCon=0.8, maxHands=2)

    # Variables
    ballPos = [150, 400]
    speedX = 20
    speedY = 20
    gameOver = False
    score = [0, 0]
    rx = 0
    ry = 0
    rw = 0
    rh = 0

    while True:
        with server_hand_coordinates_lock:
            # Access and process hand coordinates for each connected client
            for client_socket, coordinates in server_hand_coordinates.items():
                # Process hand coordinates for the client

                # Example: Access individual coordinates
                lx, ly, lw, lh = coordinates

        activeHands = False
        right = False
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
                rh, rw, _ = imgBat1.shape
                tempX = x - rw // 2
                tempY = y - rh // 2

                rx = tempX
                ry = tempY
                ry = ry + 700

                # print(y1)
                y1 = np.clip(ry, 600, 730)
                x1 = np.clip(rx, 20, 330)

                if hand['type'] == "Right":
                    right = True

        if right or activeHands is False:
            if rx != 0 and ry != 0:
                # print("left  x: "+str(x)+"y: "+str(y)+"w: "+str(w)+"h: "+str(h))
                img = cvzone.overlayPNG(img, imgBat1, (rx, ry))
                if rx < ballPos[0] < rx + rw and ry - rh < ballPos[1] < ry:
                    speedY = -speedY
                    ballPos[0] += 30
                    with client_hand_coordinates_lock:
                        client_hand_coordinates[client_socket] = (rx, ry, rw, rh)

        if left:
                # print("left  x: "+str(x)+"y: "+str(y)+"w: "+str(w)+"h: "+str(h))
                mptW = desired_width//2
                mptH = desired_width//2
                ly = ry - 2(mptH - ly)
                if lx >= mptW:
                    lx = lx - 2(lx - mptW) - lw

                elif rx < mptW:
                    lx = lx + 2(mptW - lx) - lw

                img = cvzone.overlayPNG(img, imgBat2, (lx, ly))
                if lx < ballPos[0] < lx + lw and ly - lh < ballPos[1] < ly:
                    speedY = -speedY
                    ballPos[0] -= 30



#Have to implement the scoring system logic based on the air hockey scoring area instead of just updating after every
#slider hit

#What does incrementing ballPos[0] by 30



        # Game Over
        if ballPos[0] < 0 or ballPos[0] > 800:
            gameOver = True

        #if gameOver:
            #img = imgGameOver
            #cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX,
                       #2.5, (200, 0, 200), 5)


        # If game not over move the ball
        else:

            # Move the Ball
            if ballPos[0] >= 280 or ballPos[0] <= 10:
                speedX = -speedX

            if ballPos[1] >= 730 or ballPos[1] <= 10:
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
        #cv2.moveWindow("Image", 0, 0)
        key = cv2.waitKey(1)
        if key == ord('r'):
            ballPos = [150, 450]
            speedX = 20
            speedY = 20
            gameOver = False
            score = [0, 0]
            imgGameOver = cv2.imread("Resources/gameOver.png")


def client_program():
    host = socket.gethostname()
    port = 2000

    # Create a client socket and connect to the server
    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Create a thread for server communication
    server_comm_thread = threading.Thread(target=handle_server_communication, args=(client_socket,))
    server_comm_thread.start()

    # Create a thread for game logic
    game_thread = threading.Thread(target=start_game)
    game_thread.start()

    server_comm_thread.join()
    game_thread.join()

    client_socket.close()


if __name__ == '__main__':
    client_program()
