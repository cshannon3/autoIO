
import pulseio, terminalio, displayio, time, board, math
import adafruit_bus_device.i2c_device as i2c_device
from micropython import const

from adafruit_register.i2c_struct import UnaryStruct
from adafruit_register.i2c_struct_array import StructArray
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import my_constants as consts
import utils
  
class MyOutputs:

    def __init__(self, i2c):
        self.outputpwm = pulseio.PWMOut(board.D12, frequency=20000, duty_cycle=int(65535/4))
        self.controllerMap = consts.controllerData
        self.controllerMap["output"] = 0.0
        self.updatePWM()
        self.clockMap = consts.therapyClockData
        self.distanceInitiated=True
        self.outputs = {}
        self.tick=0
        self.pidC=0.0

        displayio.release_displays()
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
        self.display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
        self.splash = displayio.Group(max_size=10)


    def updateDisplay(self,newText):
        text_area = label.Label(terminalio.FONT, text=newText, color=0xFFFF00, x=10, y=15)
        self.splash[-1]=text_area
        time.sleep(.5)

    def initDisplay(self,initiated):
        self.display.show(self.splash)
        color_bitmap = displayio.Bitmap(128, 32, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF # White

        bg_sprite = displayio.TileGrid(color_bitmap,
                                    pixel_shader=color_palette,
                                    x=0, y=0)
        self.splash.append(bg_sprite)
        inner_bitmap = displayio.Bitmap(118, 24, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0x000000 # Black
        inner_sprite = displayio.TileGrid(inner_bitmap,
                                        pixel_shader=inner_palette,
                                        x=5, y=4)
        self.splash.append(inner_sprite)
        if initiated:
            text = "Press Y to Start"
        else:
            text = "Sensor Issue"
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=10, y=15)
        self.splash.append(text_area)  


    def compute(self, dist): #, isNewWay=False flow
        #baseline, alpha, gain, blmax = utils.toTuple(self.controllerMap, "baseline", "alpha", "gain", "bl_max")
        baseline, alpha, gain= utils.toTuple(self.controllerMap, "baseline", "alpha", "gain")
        output, current, last =utils.toTuple(self.controllerMap, "output", "current", "last")
        
        beta = 1.0-alpha
        current= (baseline-dist)*alpha + last*beta #baseline-(+ last*beta)
        
        g=(current/gain)
        blmax=0.2
        blmin=0.05
        if(output==0.0):
            #self.pidC=0.0
            if(self.tick>1):
                self.tick-=1
        elif(self.tick<300):
            self.tick+=1
        if( current>last  and self.tick<70):
            if(current<0.0):
                o=current*0.8
                current= o
                #*alpha + last*beta
               # current=o
               # last=o
            # elif(g<blmin):
            #     inverse = 4*(g/blmin) 
            #     o= current*inverse
            #     #print("inverse:{},initial:{},scaled:{}".format(inverse, current, o))
            #     current=o
            elif(g<blmax):
                multiplier = (1+1.5*(blmax-g)/blmax)
                o = current*multiplier
               # print("mult:{},initial:{},scaled:{}".format(multiplier, current, o))
                current= o
                #alpha + last*beta
                #current=o
                #last=o
        
        last=current
               # print(multiplier)
            #     o=current*0.5
            #     current=o
            # else:
               
        # elif((current/gain)>blmax and self.pidC==0.0):
        #     self.pidC= current*0.8
        
        #last = current
        
        output = current/gain
        utils.capOutput(self.controllerMap, newVal=output,valStr="output", maxStr="outmax")
        self.controllerMap["last"]=last
        self.controllerMap["current"]=current
    

        self.updatePWM()
       # print(self.tick)

    #     if(self.controllerMap["new_way"]):
    #         floatingBaseline += (unscaledOutput-floatingBaseline)
    #         #self.controllerMap=
    #         utils.capOutput(self.controllerMap, newVal=floatingBaseline, valStr="floatingBaseline", maxStr="bl_max")
    #         output = unscaledOutput+floatingBaseline
    #         #self.controllerMap=
    #         utils.capOutput(self.controllerMap, newVal=unscaledOutput, valStr="unscaledOutput")
    #     else:
    #         output = unscaledOutput

    #     #self.controllerMap=
    #    # print
        #self.controllerMap["output"]=output
        
    def updatePWM(self):
        output, pwmRange, minPWM = utils.toTuple(self.controllerMap, "output", "pwmRange", "minPWM")
        self.outputpwm.duty_cycle=int(output*pwmRange + minPWM)
    
    def startTherapy(self, startTime):
        self.clockMap["therapy_start_time"]=startTime
        self.clockMap["breath_gap_start_time"] = startTime
        self.clockMap["breath_start_time"]=startTime

    def deltaTime(self, currenttime):
        return currenttime-self.clockMap["t"]
    
    def inTherapy(self, currenttime):
        return (currenttime-self.clockMap["therapy_start_time"])<self.clockMap["therapy_length"]

    def inBreathGap(self):
        return self.clockMap["breath_gap_start_time"]>=self.clockMap["breath_start_time"]

    def breathCheck(self, currenttime, breathdetected):
        # breath detected passed in from main -> determines what to do if check
        self.clockMap["t"]=currenttime
        t, check_length, last_check_time = utils.toTuple(self.controllerMap, "t", "check_length", "last_check_time")
        #  if last check time is longer than check lenaght ago, check again
        if (t- last_check_time)>check_length:
            self.clockMap["last_check_time"]=t
            return self.inBreath(breathdetected)
        return False

    def inBreath(self, breathdetected):
        return False





       
        # if not self.distanceInitiated:
        #     if baseline!=0.0:
        #         self.distanceInitiated=True
        #     else:
        #         return

        # not currently in breath and breath is detected, updates for new breath
        # if breathdetected and self.inBreathGap():
        #     #print("Breath Detected")
        #     # respiratory rate is the time in sec from when last breath started to now
        #     # if the last breath was longer than 7 seconds ago
        #     if self.t-self.breath_gap_start_time > 7:  #self.inInactivePeriod():   #(newRespRate>(self.respiratorytime+self.respiratory_buffer)):
        #         self.inactive_therapy_time+=((self.t-self.breath_gap_start_time)-7)# print(self.inactive_therapy_time)#print(self.t-self.therapy_start_time)
        #     else:
        #         newRespRate = self.t-self.breath_start_time
        #         self.numBreaths+=1
        #         self.respiratorytimes.reverse()
        #         self.respiratorytimes[0]=newRespRate
        #         self.currentRespTime= (self.respiratorytimes[0]+self.respiratorytimes[1])/2
        #     self.breath_start_time=self.t
           
        #     return True
        # elif not breathdetected and not self.inBreathGap() : #self.breath_gap_start_time<self.breath_start_time):
        #     self.breath_gap_start_time= self.t
        #     return False

