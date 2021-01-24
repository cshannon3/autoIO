
import board, digitalio, time, pulseio, busio
import my_outputs, my_inputs
import my_constants as consts
from micropython import const
from analogio import AnalogIn

_distance                  = const(0x29)
_pressure                  = const(0x78)
_flow                      = const(0x40)

time.sleep(1)
i2c = board.I2C()
i = my_inputs.MyInputs(i2c)
i.addDigital(name="button c",pin=board.D5)
i.addDigital(name="button b",pin=board.D6)
i.addAnalog(name="mic", pin=board.A1)

o = my_outputs.MyOutputs(i2c)
#o.initDisplay(True)

def getBaseline():
    sums=0
    p=0
    try:
        for h in range(0,10):
            i.read(_distance)
            time.sleep(0.05)
        while p < 5:
            v=i.read(_distance)[0]
            if(v!=0):
                p+=1
                sums+= v
            time.sleep(0.05)
        baseline = (sums/p)-2
        return baseline
    except:
        return 40

def getDisplayOptions(vol, displInt):
    ops = ["Vol(l): {:5.2f}".format(vol),\
                "Inactive(%): {:2.2f}".format(clock.inactivePct()),\
                "Resp(BPM): {:2.0f}".format(60/clock.currentRespTime),
                "# Breaths: {:2.0f}".format(clock.numBreaths),]
    if displInt == -1:
        return ops
    return ops[displInt%len(ops)]

def checkBreath(flow):
    return flow>3.0

def setController(baseline=0.0, gain=40, alpha=0.2, bl_max=0.2, out_max=0.6, newway=False):
    o.controllerMap["baseline"] = baseline
    o.controllerMap["gain"] = gain
    o.controllerMap["alpha"] = alpha
    o.controllerMap["bl_max"] = bl_max
    o.controllerMap["outmax"] = out_max
    o.controllerMap["new_way"] = newway
    out="baseline:{},gain:{},alpha:{},bl_max:{},out_max:{},version:".format(baseline, gain, alpha, bl_max, out_max)
    if(newway):
        out+="new way"
    else:
        out +="old way"
    return out

def runSystem():
    baseline= getBaseline()
    i.currentSensors[_distance]["baseline"] = baseline
    print(baseline)
    #o.updateDisplay("Press C to Start")
    while i.activePins["button c"].value:
        time.sleep(.01)

    #o.updateDisplay("In Therapy")
    t = time.monotonic()
    o.startTherapy(t)
    tstart = t
    volume = 0.0
    buttonPressed = False
    tick = 0
    while o.inTherapy(t) and i.activePins["button b"].value:
        if (time.monotonic()-t >= 0.01):
            tick+=1
            t=time.monotonic()
            i.read()
            distance,flowOut, flowIn, pressure = i.getVals(_distance, _flow, _flow, _pressure)#
            o.compute(distance)
            otpt = [(t-tstart),flowOut, pressure] #mic
            print(tuple(otpt))
        else:
            time.sleep(.0001)

while True:
    runSystem()