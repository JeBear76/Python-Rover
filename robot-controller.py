from inputs import devices, get_gamepad
import threading
import RPi.GPIO as GPIO
import time
import datetime
import cv2

threadActive = True
rotateOn = False
tiltOn = False

for device in devices:
    print(device)

cameraXcurrent = 5
cameraXdelta = 0
cameraXmin = 1
cameraXmax = 9
cameraYcurrent = 4.5
cameraYdelta = 0
cameraYmin = 1.5
cameraYmax = 7.5

currentMotorX = 0
currentMotorY = 0

ENA = 31
ENB = 37
IN1 = 33
IN2 = 32
IN3 = 38
IN4 = 40

GPIO.setmode(GPIO.BOARD)

#Motor A
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

#Camera Servo Rotation
GPIO.setup(13, GPIO.OUT)
#Camera Servo Tilt
GPIO.setup(15, GPIO.OUT)

pwmRotation = GPIO.PWM(13, 50)
pwmTilt = GPIO.PWM(15, 50)

pwmRotation.start(cameraXcurrent)
pwmTilt.start(cameraYcurrent)

pwmRightMotor = GPIO.PWM(ENA, 100)
pwmRightMotor.start(0)
pwmLeftMotor = GPIO.PWM(ENB, 100)
pwmLeftMotor.start(0)

def dummy():
#    print ("in dummy function")
    return

def setMotorXDirection(x):
    global currentMotorX
    if x < 25000 and x > -25000:
        currentMotorX = 0
    if(x == -32768):
        x = -32767
    currentMotorX = x/32767


def setMotorYDirection(y):
    global currentMotorY
    if(y == -32768):
        y = -32767
    currentMotorY = y/32767

def setRotateCameraX(direction):
    global cameraXdelta
    global rotateOn
    if(direction == -32768):
        direction = -32767
    cameraXdelta = -direction/327670
    rotateOn = True

def setRotateCameraY(direction):
    global cameraYdelta
    global tiltOn
    if(direction == -32768):
        direction = -32767
    cameraYdelta = direction/327670
    tiltOn = True

def setDirection(in1,in2,in3,in4):
    GPIO.output(IN1, in1)
    GPIO.output(IN2, in2)
    GPIO.output(IN3, in3)
    GPIO.output(IN4, in4)

def motorDirection_handler():
    while(threadActive):
        if (currentMotorY >= 0):
            setDirection(True,False,True,False)
        if (currentMotorY < 0):
            setDirection(False,True,False,True)

        if(currentMotorX > 0):
            if (currentMotorY >= 0):
                rightMotorSpeed = 0
                leftMotorSpeed = abs(currentMotorX)

            if (currentMotorY < 0):
                rightMotorSpeed = abs(currentMotorX)
                leftMotorSpeed = 0
                
        if(currentMotorX < 0):
            if(currentMotorY >= 0):
                rightMotorSpeed = abs(currentMotorX)
                leftMotorSpeed = 0

            if(currentMotorY < 0):
                rightMotorSpeed = 0
                leftMotorSpeed = abs(currentMotorX)

        if(currentMotorX == 0):
            rightMotorSpeed = abs(currentMotorY)
            leftMotorSpeed = abs(currentMotorY)

        pwmLeftMotor.ChangeDutyCycle(leftMotorSpeed * 30)
        pwmRightMotor.ChangeDutyCycle(rightMotorSpeed * 30)

def rotateCamera_handler():
    global threadActive
    global rotateOn
    global cameraXcurrent
    while(threadActive):
        if rotateOn:
            cameraXcurrent += cameraXdelta
            if(cameraXcurrent <= cameraXmin):
                cameraXcurrent = cameraXmin
            if(cameraXcurrent >= cameraXmax):
                cameraXcurrent = cameraXmax

            pwmRotation.ChangeDutyCycle(cameraXcurrent)
            time.sleep(0.01)


def tiltCamera_handler():
    global threadActive
    global tiltOn
    global cameraYcurrent
    while(threadActive):
        if tiltOn:
            cameraYcurrent += cameraYdelta
            if(cameraYcurrent <= cameraYmin):
                cameraYcurrent = cameraYmin
            if(cameraYcurrent >= cameraYmax):
                cameraYcurrent = cameraYmax

            pwmTilt.ChangeDutyCycle(cameraYcurrent)
            time.sleep(0.01)

def takePicture():
    cap = cv2.VideoCapture(0)
    success, image = cap.read()
    if success:
        text = "Greetings from..."
        font = cv2.FONT_HERSHEY_SIMPLEX
        image = cv2.putText(image, text, (10, 50), font, 0.75, (255, 0, 255), 2, cv2.LINE_AA)
        cv2.imwrite('static/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png', image)
    cap.release()
    return

def sendCommand(command, value):
    print (command, value)
    control_switcher = {
        "ABS_RX": setRotateCameraX,
        "ABS_RY": setRotateCameraY,
        "ABS_X": setMotorXDirection,
        "ABS_Y": setMotorYDirection,
        "BTN_SOUTH": takePicture
    }
    func = control_switcher.get(command, lambda x: dummy())

    func(value)

def gamepad_handler():
    global threadActive
    while threadActive:
        events = get_gamepad()
        for event in events:
            try:
#                print("type" ,event.ev_type)
#                print("Code", event.code)
#                print("State", event.state)
                if(event.code == "BTN_START" and event.state == 1):
                    threadActive = False
                    break
                sendCommand(event.code, event.state)
            except:
                threadActive = False
                break
    print ("GamePad Controller stopped")

camRotateThread = threading.Thread(target=rotateCamera_handler)
camTiltThread = threading.Thread(target=tiltCamera_handler)
motorThread = threading.Thread(target=motorDirection_handler)

t = threading.Thread(target=gamepad_handler)

print ("starting GamePad Controller")
camRotateThread.start()
camTiltThread.start()
motorThread.start()
t.start()

