
"""
`inputs`
====================================================
"""

import my_constants as consts
import adafruit_bus_device.i2c_device as i2c_device
import time, board, digitalio
from analogio import AnalogIn
import utils
#pylint: disable=bad-whitespace
# Internal constants:

# User-facing constants/


class MyInputs:

    def __init__(self, i2c, myAnalog={}, myDigital={}):

        self.i2c = i2c

        self.currentSensors = {
            consts.VL6180X_DEFAULT_I2C_ADDR:{
                "name":"distance sensor",
                "positions":[],
                "values":[],# "valuesScaled":[0.0] # "baseline":0.0, # "gain":30.0,
                "begin": self._beginDistance,
                "read": self._readDistance
            },
            consts.SFM_DEFAULT_I2C_ADDR:{
                "name":"flow sensor",
                "positions":[],
                "values":[],
                "begin": self._beginFlow,
                "read": self._readFlow
            },
            consts.AMS_I2C_ADDR_TEN:{
                "name":"pressure sensor",
                "positions":[],
                "values":[],
                "read": self._readPressure
            },
            consts.TCA_ADDRESS:{
                "name":"multiplexer",
                "positions":[],
            }
        }
        self.activePins={}
        
        self.begin()



    def addDigital(self, name="", pin=None, isPulledUp=True):
        new_input = digitalio.DigitalInOut(pin)
        new_input.direction = digitalio.Direction.INPUT
        if isPulledUp:
            new_input.pull = digitalio.Pull.UP 
        self.activePins[name]=new_input

    def addAnalog(self,name="", pin=None):
        new_input = AnalogIn(pin)
        self.activePins[name]=new_input

    def getVal(self, addr, index=0):
        if addr in self.currentSensors and self.currentSensors[addr]["values"]!=[] and len(self.currentSensors[addr]["values"])>index:
            v = self.currentSensors[addr]["values"][index]
            return v
        return 0

    def getVals(self, *addrs):# first=True,
        out=[]
        a = {}
        for addr in addrs:
            if addr in a:
                a[addr]+=1 
            else:
                a[addr]=0
            r = self.getVal(addr, index=a[addr])# print(r)
            out.append(r)
        return tuple(out)


    def begin(self):
        for addr in self._scan():
            if addr in self.currentSensors and utils.probe_for_device(self.i2c, addr):
                print('Found device with address: {}'.format(hex(addr)))
                self.currentSensors[addr]["positions"].append(-1)
                if "values" in self.currentSensors[addr]:
                    self.currentSensors[addr]["values"].append(0.0)
        if(utils.probe_for_device(self.i2c,consts.AMS_I2C_ADDR_TEN)):
            self.currentSensors[consts.AMS_I2C_ADDR_TEN]["positions"].append(-1)
            self.currentSensors[consts.AMS_I2C_ADDR_TEN]["values"].append(0.0)

        if utils.probe_for_device(self.i2c,consts.TCA_ADDRESS): 
            for tcapos in range(8):
                b=bytearray([1 << tcapos])
                utils.call(self.i2c,b, consts.TCA_ADDRESS)
                for addr in self._scan():
                    if self._isOnBus(addr) and utils.probe_for_device(self.i2c,addr):
                            print('Found device with address: {}'.format(hex(addr)))#print(hex(addr))
                            self.currentSensors[addr]["positions"].append(tcapos)
                            self.currentSensors[addr]["values"].append(0.0)
                time.sleep(0.1)

        for addr, info in self.currentSensors.items():
            if info["positions"]!=[] and "begin" in info:
                info["begin"](info)

    def read(self, *args):
        out=[]
        if args and len(args) > 0:
            for addr in args:
                if addr in self.currentSensors:
                    info = self.currentSensors[addr]
                    if info["positions"]!=[] and "read" in info:
                        out+=info["read"](info)
        else:
            for addr, info in self.currentSensors.items():
                if info["positions"]!=[] and "read" in info:
                    v=info["read"](info)
                    if isinstance(v, list):
                        out+=v
                    
        return out
    
   

    def _beginFlow(self, info):
        buffer=bytes([0x10 & 0xFF,0x00 & 0xFF])
        print("PL")
        utils.call(self.i2c,buffer,consts.SFM_DEFAULT_I2C_ADDR,tcaPosList=info["positions"])
    
    def _beginDistance(self, info):
        result = bytearray(1)
        buffers= {
            "id":utils.createBytes(address=consts.VL6180X_REG_IDENTIFICATION_MODEL_ID),
            "reset":utils.createBytes(address=consts.VL6180X_REG_SYSTEM_FRESH_OUT_OF_RESET, data=0x00),
            "clear":utils.createBytes(address=consts.VL6180X_REG_SYSTEM_INTERRUPT_CLEAR, data=0x07),
            "range":utils.createBytes(address=consts.VL6180X_REG_SYSRANGE_START, data=0x07),
            "measurementTime":utils.createBytes(address=consts.VL6180X_SYSRANGE_INTERMEASUREMENT_PERIOD, data=0x00)
        }
        addr = consts.VL6180X_DEFAULT_I2C_ADDR#buffers[0]
        utils.call(self.i2c,buffers["id"], addr, res=result, tcaPos=info["positions"][0])
        if not(result[0] & 0xB4):
            raise RuntimeError('Could not find VL6180X, is it connected and powered?')
        self._load_settings()
        time.sleep(0.1)
        #for i in range(1,4):#utils.call(self.i2c,buffers[i], addr, tcaPosList=info["positions"])
        utils.call(self.i2c,buffers["reset"], addr, tcaPosList=info["positions"])
        utils.call(self.i2c,buffers["range"], addr, tcaPosList=info["positions"])
        #self._readDistance(info)
    

    def _readDistance(self, info):
        addr = consts.VL6180X_DEFAULT_I2C_ADDR
        buffers= {
            "status":utils.createBytes(address=consts.VL6180X_REG_RESULT_RANGE_STATUS),
            "interrupt":utils.createBytes(address=consts.VL6180X_REG_RESULT_INTERRUPT_STATUS_GPIO),
            "result":utils.createBytes(address=consts.VL6180X_REG_RESULT_RANGE_VAL),
            "clear":utils.createBytes(address=consts.VL6180X_REG_SYSTEM_INTERRUPT_CLEAR,data= 0x07),
            "start":utils.createBytes(address=consts.VL6180X_REG_SYSRANGE_START,data= 0x01)
        }
        for p in range(len(info["positions"])):
            out = []
            isReady=True
            status = utils.call(self.i2c,buffers["status"],addr, res=bytearray(1), tcaPos=info["positions"][p])# & 0x01:
            if not(status[0] & 0x01):

                isReady=False
                out= [info["values"][p]]
            interrupt= utils.call(self.i2c,buffers["interrupt"],addr, res=bytearray(1), tcaPos=info["positions"][p])
            if not (interrupt[0] & 0x04): # interrupt not ready
                isReady=False
                #print("e")
            if(isReady):
                res=utils.call(self.i2c,buffers["result"],addr, res=bytearray(1), tcaPos=info["positions"][p])
                info["values"][p]=res[0]
            utils.call(self.i2c,buffers["clear"],addr, tcaPos=info["positions"][p])
            utils.call(self.i2c,buffers["start"],addr, tcaPos=info["positions"][p])
            #v=res[0]
            # if (self.currentSensors[addr]["baseline"]!=0.0):
            #     self.currentSensors[addr]["valuesScaled"][0] = (self.currentSensors[addr]["baseline"]-v)/self.currentSensors[addr]["gain"]
        return info["values"]
    
    def _readPressure(self, info):
        _pMin = -0.15
        _pMax=0.15 
        _digOutPmin = 3277
        _digOutPmax = 29491
        _step= (_pMax - _pMin)/(_digOutPmax - _digOutPmin)
        result = bytearray(4)
        for p in range(len(info["positions"])):
            result=utils.call(self.i2c,"",consts.AMS_I2C_ADDR_TEN,res=result, tcaPos=info["positions"][p])
            r =((result[0] & 0x7F) <<8) + result[1]
            r_norm = r - _digOutPmin;# get digital result w/ 0 as start
            pres =(r_norm/((_digOutPmax - _digOutPmin)/(_pMax - _pMin)) + _pMin)
            
            pres= pres*68.9476-0.05
            if (pres <= 10.0 and pres>= -10.0):
                info["values"][p] =  pres
        return info["values"]


    def _readFlow(self, info):
        for p in range(len(info["positions"])):
            result = bytearray(3)
            result=utils.call(self.i2c,"",consts.SFM_DEFAULT_I2C_ADDR,res=result, tcaPos=info["positions"][p])
            r =((result[0]&0xFF) << 8) | (result[1]&0xff)
            flow_ = (r - 32000 ) / 140.0
            if (flow_ <200.0 and flow_ > -200.0):
                info["values"][p]=flow_ 
        return info["values"] 

    def printVals(self, otherVals=[]):
        out=otherVals
        for k,v in self.currentSensors.items():
            if("values" in v and v["values"]!=[]):
                out+=v["values"]
        print(out)
        return out
    
    def _scan(self):
        self.i2c.try_lock()
        scn = self.i2c.scan()
        self.i2c.unlock()
        return scn

    def _isOnBus(self, addr):
        return (addr in self.currentSensors and (self.currentSensors[addr]["positions"]==[] or self.currentSensors[addr]["positions"][0]!=-1))

    def _load_settings(self, tcaPos=-1):
        buffers = [[0x0207,0x01],[0x0208,0x01],[0x0096,0x00],[0x0097,0xfd],
                    [0x00e3,0x00],[0x00e4,0x04],[0x00e5,0x02],[0x00e6,0x01],
                    [0x00e7,0x03],[0x00f5,0x02],[0x00d9,0x05],[0x00db,0xce], 
                    [0x00dc,0x03],[0x00dd,0xf8],[0x009f,0x00],[0x00a3,0x3c],
                    [0x00b7,0x00],[0x00bb,0x3c],[0x00b2,0x09],[0x00ca,0x09], 
                    [0x0198,0x01],[0x01b0,0x17],[0x01ad,0x00],[0x00ff,0x05],
                    [0x0100,0x05],[0x0199,0x05],[0x01a6,0x1b], [0x01ac,0x3e],
                    [0x01a7,0x1f],[0x0030,0x00],[0x0011,0x10],[0x010a,0x30],
                    [0x003f,0x46],[0x0031,0xFF],[0x0040,0x63],[0x002e,0x01],
                    [0x001b,0x09],[0x003e,0x31], [0x0014,0x24]]
        
        for addrDataPair in buffers:
            buffer = utils.createBytes(address=addrDataPair[0],data= addrDataPair[1])
            utils.call(self.i2c,buffer, consts.VL6180X_DEFAULT_I2C_ADDR, tcaPos=tcaPos)
  
  

           
    # def getBaseline(self):
    #     if(self._distdevice==None):
    #         return 35
    #     sums = 0
    #     for i in range(5): 
    #         self.readDistance()
    #         sums+= self.distance
    #         time.sleep(0.05)
    #     baseline = (sums/5)-2
    #     return baseline

