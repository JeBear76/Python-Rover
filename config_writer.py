import shelve
import constants as c

def recursiveConfig(configSection, depth=0):
    for item in configSection.keys():
        value = configSection[item]
        if type(value) == int or type(value) == float:
            val = input('{} {} ({}):'.format('=' * depth ,item , value))
            try:
                val = type(value)(val)
                configSection[item] = val
            except:
                pass
        else:
            if depth > 0:
                print('=' * depth, end=' ')
            print(item)
            recursiveConfig(value, depth + 1)

with shelve.open(c.config) as config:
    memoryconfig = dict(config)

if memoryconfig:
    reset = input('Recreate default config file (y/N):')
    if reset.casefold() == 'y':
        memoryconfig = {}

if not memoryconfig:
    memoryconfig = {}
    memoryconfig[c.motorPins] = {
                c.ENA:6,
                c.ENB:26,
                c.IN1:12,
                c.IN2:13,
                c.IN3:20,
                c.IN4:21
                }
    memoryconfig[c.cameraPins] = {
                c.servoH:27,
                c.servoV:22
                }
    memoryconfig[c.PWMFrequencies] = {
                c.motorFrequency:100,
                c.servoFrequency:50,
            }
    memoryconfig[c.IRPins] = {
                c.leftIR:19,
                c.rightIR:16
                }
    memoryconfig[c.constValues] = {
                c.pigpio:
                    {
                            c.dutyCycleMultiplier:255,
                            c.cameraDeltaDivider: 3276.7,
                            c.cameraXReset:1100,
                            c.cameraXmin:500,
                            c.cameraXmax:1700,
                            c.cameraYReset:950,
                            c.cameraYmin:500,
                            c.cameraYmax:1300
                    },
                c.GPIO:
                    {
                            c.dutyCycleMultiplier:50,
                            c.cameraDeltaDivider: 327670,
                            c.cameraXReset:5,
                            c.cameraXmin:1,
                            c.cameraXmax:9,
                            c.cameraYReset:4.5,
                            c.cameraYmin:1.5,
                            c.cameraYmax:7.5
                    }, 
                }

recursiveConfig(memoryconfig)

with shelve.open(c.config, writeback=True) as config:
    config.update(memoryconfig)

print('Configuration saved!')