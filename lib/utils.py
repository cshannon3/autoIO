
import my_constants as consts
import time

def toTuple(ctrMap, *args):
    values = []
    for key in args:
        if key in ctrMap:
            values.append(ctrMap[key])
        else:
            values.append(None)
    return tuple(values)

def capOutput(ctrMap, **kwargs):  
    minVal=0.0
    maxVal=1.0
    if "valStr" in kwargs and kwargs["valStr"] in ctrMap:
        valstr = kwargs["valStr"]
        #update value
        if "newVal" in kwargs:
           ctrMap[valstr]=kwargs["newVal"]
        val=ctrMap[valstr]
    else:
        return ctrMap

    if "minVal" in kwargs:
        minVal=kwargs["minVal"]
    elif "minStr" in kwargs and kwargs["minStr"] in ctrMap:
        minVal=ctrMap[kwargs["minStr"]]

    if "maxVal" in kwargs:
        maxVal=kwargs["maxVal"]
    elif "maxStr" in kwargs and kwargs["maxStr"] in ctrMap:
        maxVal=ctrMap[kwargs["maxStr"]]
    
    if val<minVal:
        ctrMap[valstr]=minVal
    elif val>maxVal:
        ctrMap[valstr]=maxVal
    return ctrMap

def call(i2c, buffer, addr,res=None,tcaPos=-1, isRoot=True, tcaPosList=[]):
    if tcaPosList!=[]:
        r=[]
        for pos in tcaPosList:
            r.append(call(i2c, buffer, addr, res=res, tcaPos=pos))
        return r
    if(isRoot): 
        while not i2c.try_lock():
            i2c.unlock() 
            pass
    if(tcaPos!=-1):
        b=bytearray([1 << tcaPos])
        try: 
            i2c.writeto(consts.TCA_ADDRESS,b)
            res = call(i2c, buffer, addr, res=res, isRoot=False)
            i2c.writeto(consts.TCA_ADDRESS, b'\x00')
        except:
            print("tca not connected") #self.begin()
            time.sleep(1)
        return res
    else:
        if(buffer!=""):
            try:
                i2c.writeto(addr, buffer) 
            except:
                print("write error from {} of {}".format(hex(addr), buffer))
        if(res!=None):
            try:
                i2c.readfrom_into(addr,res)
            except:
                print("read error from {}".format(hex(addr)))
        if(isRoot):
            i2c.unlock()
    return res


def createBytes(address=None, addressBytes=2, data=None, dataBytes=1):
    out = []
    if(address!=None):
        if(addressBytes>1):
            out.append((address >> 8) & 0xFF)
        if(addressBytes>0):
            out.append(address & 0xFF)
    if(data!=None):
        if(dataBytes>1):
            out.append((data >> 8) & 0xFF)
        if(dataBytes>0):
            out.append(data & 0xFF)
    return bytes(out)

def probe_for_device(i2c, address):
        """
        Try to read a byte from an address,
        if you get an OSError it means the device is not there
        or that the device does not support these means of probing
        """
        isGood= False
        while not i2c.try_lock():
            pass
        try:
            i2c.writeto(address, b'')
            isGood=True
        except:
            try:
                result = bytearray(1)
                i2c.readfrom_into(address, result)
                isGood=True
            except:
                print("No I2C device at address: %x" % address)
        finally:
            i2c.unlock()
            return isGood

