from inputs import get_gamepad
import threading
import RPi.GPIO as GPIO
import pigpio
import time
import shelve
import constants as c

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
        self.motorPins = {}
        self.cameraPins = {}
        self.PWMFrequencies = {}
        self.IRPins = {}
        self.constValues = {}
        self.config = {}
        with shelve.open(c.config) as config:
            self.config = dict(config)
            
        self.motorPins = self.config[c.motorPins]
        self.cameraPins = self.config[c.cameraPins]
        self.PWMFrequencies = self.config[c.PWMFrequencies]
        self.IRPins = self.config[c.IRPins]
        self.constValues = self.config[c.constValues]
            
        try:
            self.pi = pigpio.pi()
        except:
            self.initRPi()
        else:
            self.usePigPio = True
            self.initPigPio()
            
        self.cameraXdelta = 0
        self.cameraYdelta = 0
        self.cameraXcurrent = self.constValues[c.cameraXReset]
        self.cameraYcurrent = self.constValues[c.cameraYReset]


        self.resetCameraPosition(0)
            
    def initRpi(self):
        """
        Init method for GPIO functionality. 
        This is the fallback as pigpio is a lot better
        """
        self.constValues = self.constValues[c.GPIO]
        GPIO.setmode(GPIO.BCM)
        
        for motorPin in self.motorPins.values():
            GPIO.setup(motorPin, GPIO.OUT)
        
        
        self.pwmRightMotor = GPIO.PWM(self.motorPins[c.ENA], self.PWMFrequencies[c.motorFrequency])
        self.pwmRightMotor.start(0)
        self.pwmLeftMotor = GPIO.PWM(self.motorPins[c.ENB], self.PWMFrequencies[c.motorFrequency])
        self.pwmLeftMotor.start(0)
        
        for cameraPin in self.cameraPins.values():
            GPIO.setup(cameraPin, GPIO.OUT)
            
        self.pwmRotation = GPIO.PWM(self.cameraPins[c.servoH], self.PWMFrequencies[c.servoFrequency])
        self.pwmTilt = GPIO.PWM(self.cameraPins[c.servoV], self.PWMFrequencies[c.servoFrequency])
        
    def initPigPio(self):
        """
        pigpio init method
        """
        self.constValues = self.constValues[c.pigpio]
        for motorPin in self.motorPins.values():
            self.pi.set_mode(motorPin, pigpio.OUTPUT)
        
        for cameraPin in self.cameraPins.values():
            self.pi.set_mode(cameraPin, pigpio.OUTPUT)
        

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
        self.cameraXdelta = -direction / self.constValues[c.cameraDeltaDivider]
        

    def setRotateCameraY(self, direction):
        if(direction == -32768):
            direction = -32767
        self.tiltOn = True
        self.cameraYdelta = -direction / self.constValues[c.cameraDeltaDivider]

    def resetCameraPosition(self, i):
        self.cameraXcurrent = self.cameraXReset
        self.cameraYcurrent = self.cameraYReset
        if self.usePigPio:
            self.pi.set_servo_pulsewidth(self.servoH, self.cameraXcurrent)
            self.pi.set_servo_pulsewidth(self.servoV, self.cameraYcurrent)
        else:
            self.pwmRotation.ChangeDutyCycle(self.cameraXcurrent)
            self.pwmTilt.ChangeDutyCycle(self.cameraYcurrent)
        
        
    def setDirection(self, in1,in2,in3,in4):
        if self.usePigPio:
            self.pi.write(self.motorPins[c.IN2], in2)
            self.pi.write(self.motorPins[c.IN3], in3)
            self.pi.write(self.motorPins[c.IN1], in1)
            self.pi.write(self.motorPins[c.IN4], in4)
        else:
            GPIO.output(self.motorPins[c.IN1], in1)
            GPIO.output(self.motorPins[c.IN2], in2)
            GPIO.output(self.motorPins[c.IN3], in3)
            GPIO.output(self.motorPins[c.IN4], in4)

    def motorDirection_handler(self):
        while(self.threadActive):
            self.rightMotorSpeed = abs(self.currentMotorY)
            self.leftMotorSpeed = abs(self.currentMotorY)
            
            if (self.currentMotorY >= 0):
                self.setDirection(False,True,True,False)
                if(self.currentMotorX > 0):
                    self.leftMotorSpeed += abs(self.currentMotorX)/2
                if(self.currentMotorX < 0):
                    self.rightMotorSpeed += abs(self.currentMotorX)/2
            if (self.currentMotorY < 0):
                self.setDirection(True,False,False,True)
                if(self.currentMotorX > 0):
                    self.rightMotorSpeed += abs(self.currentMotorX)/2
                if(self.currentMotorX < 0):
                    self.leftMotorSpeed += abs(self.currentMotorX)/2
                    
            if self.usePigPio:
                self.pi.set_PWM_dutycycle(self.ENB, self.leftMotorSpeed * self.constValues[c.dutyCycleMultiplier])
                self.pi.set_PWM_dutycycle(self.ENA, self.rightMotorSpeed * self.constValues[c.dutyCycleMultiplier])
            else:
                self.pwmLeftMotor.ChangeDutyCycle(self.leftMotorSpeed * self.constValues[c.dutyCycleMultiplier])
                self.pwmRightMotor.ChangeDutyCycle(self.rightMotorSpeed * self.constValues[c.dutyCycleMultiplier])

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
            l = bool(self.pi.read(self.IRPins[c.leftIR]))
            r = bool(self.pi.read(self.IRPins[c.rightIR]))
            self.camera.set_warning_overlay(l, r)
            time.sleep(0.1)
            
        
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
        


