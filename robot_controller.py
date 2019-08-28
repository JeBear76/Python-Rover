from inputs import get_gamepad
import threading
import RPi.GPIO as GPIO
import time

class Robot_Controller(object):
    def __init__(self, camera):
        self.camera = camera
        self.threadActive = True
        self.rotateOn = False
        self.tiltOn = False


        self.cameraXdelta = 0
        self.cameraXmin = 1
        self.cameraXmax = 9
        self.cameraYdelta = 0
        self.cameraYmin = 1.5
        self.cameraYmax = 7.5

        self.currentMotorX = 0
        self.currentMotorY = 0

        self.ENA = 31
        self.ENB = 37
        self.IN1 = 33
        self.IN2 = 32
        self.IN3 = 38
        self.IN4 = 40

        self.servoH = 13
        self.servoV = 15

        GPIO.setmode(GPIO.BOARD)

        #Motor A
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
	    #Motor B
        GPIO.setup(self.ENB, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)

        #Camera Servo Rotation
        GPIO.setup(self.servoH, GPIO.OUT)
        #Camera Servo Tilt
        GPIO.setup(self.servoV, GPIO.OUT)

        self.pwmRotation = GPIO.PWM(self.servoH, 50)
        self.pwmTilt = GPIO.PWM(self.servoV, 50)

        self.resetCameraPosition(0)

        self.pwmRightMotor = GPIO.PWM(self.ENA, 100)
        self.pwmRightMotor.start(0)
        self.pwmLeftMotor = GPIO.PWM(self.ENB, 100)
        self.pwmLeftMotor.start(0)

    def __del__(self):
        self.threadActive = False

    def setMotorXDirection(self, x):
        if(x == -32768):
            x = -32767
        self.currentMotorX = x/32767

    def setMotorYDirection(self, y):
        if(y == -32768):
            y = -32767
        self.currentMotorY = y/32767

    def setRotateCameraX(self, direction):
        if(direction == -32768):
            direction = -32767
        self.cameraXdelta = -direction/327670
        self.rotateOn = True

    def setRotateCameraY(self, direction):
        if(direction == -32768):
            direction = -32767
        self.cameraYdelta = -direction/327670
        self.tiltOn = True

    def resetCameraPosition(self, i):
        self.cameraXcurrent = 5
        self.cameraYcurrent = 4.5
        self.pwmRotation.start(self.cameraXcurrent)
        self.pwmTilt.start(self.cameraYcurrent)
        
    def setDirection(self, in1,in2,in3,in4):
        GPIO.output(self.IN1, in1)
        GPIO.output(self.IN2, in2)
        GPIO.output(self.IN3, in3)
        GPIO.output(self.IN4, in4)

    def motorDirection_handler(self):
        while(self.threadActive):
            self.rightMotorSpeed = abs(self.currentMotorY)
            self.leftMotorSpeed = abs(self.currentMotorY)
            
            if (self.currentMotorY >= 0):
                self.setDirection(True,False,True,False)
                if(self.currentMotorX > 0):
                    self.leftMotorSpeed += abs(self.currentMotorX)/2
                if(self.currentMotorX < 0):
                    self.rightMotorSpeed += abs(self.currentMotorX)/2
            if (self.currentMotorY < 0):
                self.setDirection(False,True,False,True)
                if(self.currentMotorX > 0):
                    self.rightMotorSpeed += abs(self.currentMotorX)/2
                if(self.currentMotorX < 0):
                    self.leftMotorSpeed += abs(self.currentMotorX)/2

            self.pwmLeftMotor.ChangeDutyCycle(self.leftMotorSpeed * 50)
            self.pwmRightMotor.ChangeDutyCycle(self.rightMotorSpeed * 50)

    def rotateCamera_handler(self):
        while(self.threadActive):
            if self.rotateOn:
                self.cameraXcurrent += self.cameraXdelta
                if(self.cameraXcurrent <= self.cameraXmin):
                    self.cameraXcurrent = self.cameraXmin
                if(self.cameraXcurrent >= self.cameraXmax):
                    self.cameraXcurrent = self.cameraXmax

                self.pwmRotation.ChangeDutyCycle(self.cameraXcurrent)
                time.sleep(0.01)

    def tiltCamera_handler(self):
        while(self.threadActive):
            if self.tiltOn:
                self.cameraYcurrent += self.cameraYdelta
                if(self.cameraYcurrent <= self.cameraYmin):
                    self.cameraYcurrent = self.cameraYmin
                if(self.cameraYcurrent >= self.cameraYmax):
                    self.cameraYcurrent = self.cameraYmax

                self.pwmTilt.ChangeDutyCycle(self.cameraYcurrent)
                time.sleep(0.01)

    def takePicture(self, i):
        self.camera.save_image()
        return

    def sendCommand(self, command, value):
        #print (command, value)
        self.control_switcher = {
            "ABS_RX": self.setRotateCameraX,
            "ABS_RY": self.setRotateCameraY,
            "ABS_X": self.setMotorXDirection,
            "ABS_Y": self.setMotorYDirection,
            "BTN_SOUTH": self.takePicture,
            "BTN_EAST": self.resetCameraPosition
        }
        func = self.control_switcher.get(command, lambda x: x)
        func(value)

    def gamepad_handler(self):
        while self.threadActive:
            try:
                events = get_gamepad()
            except:
                print('No Controller found.')
                print('Controls shutdown.')
                self.threadActive = False
            else:
                for event in events:
                    try:
                        if(event.code == "BTN_START" and event.state == 1):
                            self.threadActive = False
                            break
                        self.sendCommand(event.code, event.state)
                    except Exception as err:
                        print(format(err))
                        self.threadActive = False
                        print('Controls shutdown.')
                        break
        print ("GamePad Controller stopped")

    def StartThisThing(self):
        self.camRotateThread = threading.Thread(target=self.rotateCamera_handler)
        self.camTiltThread = threading.Thread(target=self.tiltCamera_handler)
        self.motorThread = threading.Thread(target=self.motorDirection_handler)

        self.gamePadThread = threading.Thread(target=self.gamepad_handler)

        print ("starting GamePad Controller")
        self.camRotateThread.start()
        self.camTiltThread.start()
        self.motorThread.start()
        self.gamePadThread.start()


