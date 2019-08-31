from inputs import get_gamepad
import threading
import RPi.GPIO as GPIO
import pigpio
import time

class Robot_Controller(object):
    def __init__(self, camera):        
        
        self.usePigPio = False
        self.camera = camera
        self.threadActive = True
        self.gameControllerActive = True
        self.rotateOn = False
        self.tiltOn = False

        self.currentMotorX = 0
        self.currentMotorY = 0

        self.ENA = 6
        self.ENB = 26
        self.IN1 = 12
        self.IN2 = 13
        self.IN3 = 20
        self.IN4 = 21

        self.servoH = 27
        self.servoV = 22

        self.leftIR = 19
        self.rightIR = 16
        
        try:
            self.pi = pigpio.pi()
        except:
            self.initRPi()
        else:
            self.usePigPio = True
            self.initPigPio()
            
        self.cameraXdelta = 0
        if self.usePigPio:     
            self.cameraXReset = 1100
            self.cameraXmin = 500
            self.cameraXmax = 1700
        else:
            self.cameraXReset = 5
            self.cameraXmin = 1
            self.cameraXmax = 9
        
        self.cameraYdelta = 0
        if self.usePigPio:
            self.cameraYReset = 950
            self.cameraYmin = 500
            self.cameraYmax = 1300
        else:
            self.cameraYReset = 4.5
            self.cameraYmin = 1.5
            self.cameraYmax = 7.5

        self.resetCameraPosition(0)
            
    def initRpi(self):
        GPIO.setmode(GPIO.BCM)

        #Motor A
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
	    #Motor B
        GPIO.setup(self.ENB, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        
        self.pwmRightMotor = GPIO.PWM(self.ENA, 100)
        self.pwmRightMotor.start(0)
        self.pwmLeftMotor = GPIO.PWM(self.ENB, 100)
        self.pwmLeftMotor.start(0)
        
        #Camera Servo Rotation
        GPIO.setup(self.servoH, GPIO.OUT)
        #Camera Servo Tilt
        GPIO.setup(self.servoV, GPIO.OUT)

        self.pwmRotation = GPIO.PWM(self.servoH, 50)
        self.pwmTilt = GPIO.PWM(self.servoV, 50)
        
    def initPigPio(self):
        #Motor A
        self.pi.set_mode(self.ENA, pigpio.OUTPUT)
        self.pi.set_mode(self.IN1, pigpio.OUTPUT)
        self.pi.set_mode(self.IN2, pigpio.OUTPUT)
	    #Motor B
        self.pi.set_mode(self.ENB, pigpio.OUTPUT)
        self.pi.set_mode(self.IN3, pigpio.OUTPUT)
        self.pi.set_mode(self.IN4, pigpio.OUTPUT)
        
        #Camera Servo Rotation
        self.pi.set_mode(self.servoH, pigpio.OUTPUT)
        #Camera Servo Tilt
        self.pi.set_mode(self.servoV, pigpio.OUTPUT)
        

    def __del__(self):
        self.gameControllerActive = False
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
        self.rotateOn = True
        if self.usePigPio:
            self.cameraXdelta = -direction / 3276.7
        else:
            self.cameraXdelta = -direction / 327670
        

    def setRotateCameraY(self, direction):
        if(direction == -32768):
            direction = -32767
        if self.usePigPio:
            self.cameraYdelta = -direction / 3276.7
        else:
            self.cameraYdelta = -direction/327670
        self.tiltOn = True

    def resetCameraPosition(self, i):
        self.cameraXcurrent = self.cameraXReset
        self.cameraYcurrent = self.cameraYReset
        if self.usePigPio:
            self.pi.set_servo_pulsewidth(self.servoH, self.cameraXcurrent)
            self.pi.set_servo_pulsewidth(self.servoV, self.cameraYcurrent)
        else:
            self.pwmRotation.ChangeDutyCycle(self.cameraXcurrent)
            self.pwmTilt.ChangeDutyCycle(self.cameraYcurrent)
        
        
    def setDirection(self, in2,in1,in3,in4):
        if self.usePigPio:
            self.pi.write(self.IN1, in1)
            self.pi.write(self.IN2, in2)
            self.pi.write(self.IN3, in3)
            self.pi.write(self.IN4, in4)
        else:
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
                    
            if self.usePigPio:
                self.pi.set_PWM_dutycycle(self.ENB, self.leftMotorSpeed * 255)
                self.pi.set_PWM_dutycycle(self.ENA, self.rightMotorSpeed * 255)
            else:
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
                    
                if self.usePigPio:
                    self.pi.set_servo_pulsewidth(self.servoH, self.cameraXcurrent)
                else:
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
                if self.usePigPio:
                    self.pi.set_servo_pulsewidth(self.servoV, self.cameraYcurrent)
                else:
                    self.pwmTilt.ChangeDutyCycle(self.cameraYcurrent)
                time.sleep(0.01)

    def iR_handler(self):
        while(self.threadActive):
            l = bool(self.pi.read(self.leftIR))
            r = bool(self.pi.read(self.rightIR))
            self.camera.set_warning_overlay(l, r)
            time.sleep(0.5)
            
        
    def takePicture(self, i):
        self.camera.save_image()
        return

    def sendCommand(self, command, value, fromController):
        #print (command, value)
        self.control_switcher = {
            "ABS_RX": self.setRotateCameraX,
            "ABS_RY": self.setRotateCameraY,
            "ABS_X": self.setMotorXDirection,
            "ABS_Y": self.setMotorYDirection,
            "BTN_SOUTH": self.takePicture,
            "BTN_EAST": self.resetCameraPosition
        }
        if(not fromController):
            if (command == "ABS_Y"):
                value = -value
            
        func = self.control_switcher.get(command, lambda x: x)
        func(value)

    def gamepad_handler(self):
        while self.gameControllerActive:
            try:
                events = get_gamepad()
            except:
                print('No Controller found.')
                self.gameControllerActive = False
            else:
                for event in events:
                    try:
                        if(event.code == "BTN_START" and event.state == 1):
                            self.gameControllerActive = False
                            break
                        self.sendCommand(event.code, event.state, True)
                    except Exception as err:
                        print(format(err))
                        self.StopControls()
                        break
                    

    def StartThisThing(self):
        self.camRotateThread = threading.Thread(target=self.rotateCamera_handler)
        self.camTiltThread = threading.Thread(target=self.tiltCamera_handler)
        self.motorThread = threading.Thread(target=self.motorDirection_handler)
        self.irThread = threading.Thread(target=self.iR_handler)
        self.gamePadThread = threading.Thread(target=self.gamepad_handler)

        print ("Controls starting")
        self.camRotateThread.start()
        self.camTiltThread.start()
        self.motorThread.start()
        self.irThread.start()
        self.gamePadThread.start()
        
    def StopControls(self):
        self.gameControllerActive = False
        self.threadActive = False
        if not self.usePigPio:
            GPIO.cleanup()
        print('Controls shutdown.')
        


