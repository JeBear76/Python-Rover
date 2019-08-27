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
        
        self.cameraXcurrent = 5
        self.cameraXdelta = 0
        self.cameraXmin = 1
        self.cameraXmax = 9
        self.cameraYcurrent = 4.5
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
        
        self.GPIO.setmode(GPIO.BOARD)
        
        #Motor A
        self.GPIO.setup(self.ENA, GPIO.OUT)
        self.GPIO.setup(self.IN1, GPIO.OUT)
        self.GPIO.setup(self.IN2, GPIO.OUT)
        
        self.GPIO.setup(self.ENB, GPIO.OUT)
        self.GPIO.setup(self.IN3, GPIO.OUT)
        self.GPIO.setup(self.IN4, GPIO.OUT)
        
        #Camera Servo Rotation
        self.GPIO.setup(self.servoH, GPIO.OUT)
        #Camera Servo Tilt
        self.GPIO.setup(self.servoV, GPIO.OUT)
        
        self.pwmRotation = GPIO.PWM(self.servoH, 50)
        self.pwmTilt = GPIO.PWM(self.servoV, 50)
        
        self.pwmRotation.start(self.cameraXcurrent)
        self.pwmTilt.start(self.cameraYcurrent)
        
        self.pwmRightMotor = GPIO.PWM(self.ENA, 100)
        self.pwmRightMotor.start(0)
        self.pwmLeftMotor = GPIO.PWM(self.ENB, 100)
        self.pwmLeftMotor.start(0)
    
    def __del__(self):
        self.threadActive = False
    
    def dummy():
    #    print ("in dummy function")
        return
    
    def setMotorXDirection(self, x):
        if x < 25000 and x > -25000:
            self.currentMotorX = 0
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
        self.cameraYdelta = direction/327670
        self.tiltOn = True
    
    def setDirection(self, in1,in2,in3,in4):
        GPIO.output(self.IN1, in1)
        GPIO.output(self.IN2, in2)
        GPIO.output(self.IN3, in3)
        GPIO.output(self.IN4, in4)
    
    def motorDirection_handler(self):
        while(self.threadActive):
            if (self.currentMotorY >= 0):
                self.setDirection(True,False,True,False)
            if (self.currentMotorY < 0):
                self.setDirection(False,True,False,True)
    
            if(self.currentMotorX > 0):
                if (self.currentMotorY >= 0):
                    self.rightMotorSpeed = 0
                    self.leftMotorSpeed = abs(self.currentMotorX)
    
                if (self.currentMotorY < 0):
                    self.rightMotorSpeed = abs(self.currentMotorX)
                    self.leftMotorSpeed = 0
                    
            if(self.currentMotorX < 0):
                if(self.currentMotorY >= 0):
                    self.rightMotorSpeed = abs(self.currentMotorX)
                    self.leftMotorSpeed = 0
    
                if(self.currentMotorY < 0):
                    self.rightMotorSpeed = 0
                    self.leftMotorSpeed = abs(self.currentMotorX)
    
            if(self.currentMotorX == 0):
                self.rightMotorSpeed = abs(self.currentMotorY)
                self.leftMotorSpeed = abs(self.currentMotorY)
    
            self.pwmLeftMotor.ChangeDutyCycle(self.leftMotorSpeed * 30)
            self.pwmRightMotor.ChangeDutyCycle(self.rightMotorSpeed * 30)
    
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
            "BTN_SOUTH": self.takePicture
        }
        func = self.control_switcher.get(command, lambda x: dummy())
    
        func(value)
    
    def gamepad_handler(self):
        while self.threadActive:
            events = get_gamepad()
            for event in events:
                try:
    #                print("type" ,event.ev_type)
    #                print("Code", event.code)
    #                print("State", event.state)
                    if(event.code == "BTN_START" and event.state == 1):
                        self.threadActive = False
                        break
                    self.sendCommand(event.code, event.state)
                except:
                    self.threadActive = False
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

