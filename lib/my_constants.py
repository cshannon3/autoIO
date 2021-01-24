from micropython import const


VL6180X_DEFAULT_I2C_ADDR                  = const(0x29)
VL6180X_REG_IDENTIFICATION_MODEL_ID       = const(0x000)
VL6180X_REG_SYSTEM_INTERRUPT_CONFIG       = const(0x014)
VL6180X_REG_SYSTEM_INTERRUPT_CLEAR        = const(0x015)
VL6180X_REG_SYSTEM_FRESH_OUT_OF_RESET     = const(0x016)
VL6180X_REG_SYSRANGE_START                = const(0x018)
VL6180X_REG_SYSALS_START                  = const(0x038)
VL6180X_REG_SYSALS_ANALOGUE_GAIN          = const(0x03F)
VL6180X_REG_SYSALS_INTEGRATION_PERIOD_HI  = const(0x040)
VL6180X_REG_SYSALS_INTEGRATION_PERIOD_LO  = const(0x041)
VL6180X_SYSRANGE_INTERMEASUREMENT_PERIOD  = const(0x01B)
VL6180X_SYSRANGE_MAX_CONVERGENCE_TIME     = const(0x01C)
VL6180X_REG_RESULT_ALS_VAL                = const(0x050)
VL6180X_REG_RESULT_RANGE_VAL              = const(0x062)
VL6180X_REG_RESULT_RANGE_STATUS           = const(0x04d)
VL6180X_REG_RESULT_INTERRUPT_STATUS_GPIO  = const(0x04f)
SFM_DEFAULT_I2C_ADDR                      = const(0x40)
AMS_I2C_ADDR_FIVE                         = const(0x28)
AMS_I2C_ADDR_TEN                          = const(0x78)
TCA_ADDRESS                               = const(0x70)
DISPLAY_ADDR                              = const(0x3c)

## CONTROLLER ##
controllerData = {
    "minPWM":65535*0.45,"pwmRange":65535*0.55,
    "gain":30.0,"alpha":0.2,# "beta":0.8,
    
    "output":0.0,"current":0.0,
    "last":0.0,"baseline":0.0,

    "new_way":False, "bl_max":0.2,"outmax":0.53,
    "floatingBaseline":0.0,"unscaledOutput":0.0
}
therapyClockData={
    "t":0,
    "therapy_start_time":0.0,
    "therapy_length":(10*60), # 10 minutes for test
    "inactive_therapy_time":0.0,
    
    "last_check_time":0.0,
    "check_length":0.2,
    "breath_gap_start_time":0.0,
    "breath_start_time":0.0,
    
    "currentRespTime":6.0,
    "respiratorytimes":[6.0, 6.0],
    "respiratory_buffer":2.0,
    "numBreaths":0
}
# def toTuple(ctrMap, *args):
#     values = []
#     for key in args:
#         if key in ctrMap:
#             values.append(ctrMap[key])
#         else:
#             values.append(None)
#     return tuple(values)

# def capOutput(ctrMap, **kwargs):
#     minVal=0.0
#     maxVal=1.0
#     if "valStr" in kwargs and kwargs["valStr"] in ctrMap:
#         valstr = kwargs["valStr"]
#         #update value
#         if "newVal" in kwargs:
#             ctrMap[valstr]=kwargs["newVal"]
#         val=ctrMap[valstr]
#     else:
#         return ctrMap

#     if "minVal" in kwargs:
#         minVal=kwargs["minVal"]
#     elif "minStr" in kwargs and kwargs["minStr"] in ctrMap:
#         minVal=ctrMap[kwargs["minStr"]]

#     if "maxVal" in kwargs:
#         maxVal=kwargs["maxVal"]
#     elif "maxStr" in kwargs and kwargs["maxStr"] in ctrMap:
#         maxVal==ctrMap[kwargs["maxStr"]]
    
#     if val<minVal:
#         ctrMap[valstr]=minVal
#     elif val>maxVal:
#         ctrMap[valstr]=maxVal
#     return ctrMap
        
    
