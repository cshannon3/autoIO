
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


    def deltaTime(self, currenttime):
        return currenttime-self.clockMap["t"]

