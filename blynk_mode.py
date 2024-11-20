from pop import Window, Switch, Fan, RgbLedBar, WaterPump, WaterLevel, Light, Tphg, SoilMoisture, CO2, Textlcd
from network import WLAN
import BlynkLib
import time

auto_temp = 20 # reference Temperature value
auto_light = 20 # reference Light value
auto_soil_moisture = 30 # reference Soil Moisture value
BLYNK_AUTH = 'n0p7uTSl6t0pTJMyCxdGcPgPojbxZQiJ'
SSID = 'Hanbat_WLAN_Guest'
PASSWORD = ''

flag_pump = False
auto_mode = False
light_value = temp_value = soil_value = co2_value = 0
color_value = [0,0,0]

switch_up = Switch('P8')
switch_down = Switch('P23')
fan = Fan()
window = Window()
pump = WaterPump()
rgbledbar = RgbLedBar()
waterlevel = WaterLevel()
tphg = Tphg(0x76)
light = Light(0x5C)
co2 = CO2()
textlcd = Textlcd()
soil = SoilMoisture()

wlan = WLAN(mode = WLAN.STA)
wlan.connect(SSID, auth=(WLAN.WPA2, PASSWORD))
while not wlan.isconnected():
    print('x') #원래는 print(x)가아니라 time.sleep(1)

blynk = BlynkLib.Blynk(BLYNK_AUTH)
blynk.run()

def light_callback(param):
    global light_value
    light_value = param.read()

def tphg_callback(param):
    global temp_value
    temp_value = param.read()[0]

def soil_moisture_callback(value, param):
    global soil_value
    soil_value = param.calcSoilMoisture(value)

def co2_callback(param):
    global co2_value
    co2_value = param.read()

@blynk.on("V1")
def Auto_Callback(value):
    global auto_mode
    if value[0] == '1':
        auto_mode = True
    else:
        auto_mode = False

    print("auto mode %s"%('on' if auto_mode else 'off'))

@blynk.on("V2")
def Temp_Callback(value):
    global auto_temp
    auto_temp = int(value[0])

@blynk.on("V3")
def Soil_Moisture_Callback(value):
    global auto_soil_moisture
    auto_soil_moisture = int(value[0])

@blynk.on("V4")
def Light_Callback(value):
    global auto_light
    auto_light = int(value[0])

@blynk.on("V5")
def RgbLedBar_R_Callback(value):
    if auto_mode is False:
        global color_value
        color_value[0] = int(value[0])
        rgbledbar.setColor(color_value)

@blynk.on("V6")
def RgbLedBar_G_Callback(value):
    if auto_mode is False:
        global color_value
        color_value[1] = int(value[0])
        rgbledbar.setColor(color_value)

@blynk.on("V7")
def RgbLedBar_B_Callback(value):
    if auto_mode is False:
        global color_value
        color_value[2] = int(value[0])
        rgbledbar.setColor(color_value)

@blynk.on("V8")
def Fan_Callback(value):
    if auto_mode is False:
        if value[0] == '1':
            fan.on()
        else:
            fan.off()

@blynk.on("V9")
def Pump_Callback(value):
    global flag_pump
    if auto_mode is False:
        if value[0] == '1':
            flag_pump = True
        else:
            flag_pump = False
        pump.off()

@blynk.on("V10")
def Window_Callback(value):
    if auto_mode is False:
        if value[0] == '1':
            window.open()
        else:
            window.close()

light.setCallback(func = light_callback, param = light)
tphg.setCallback(func = tphg_callback, param = tphg)
soil.setCallback(func           =           soil_moisture_callback, type=soil.TYPE_NORMAL, param = soil)
co2.setCallback(func = co2_callback, param = co2)

rgbledbar.on()
textlcd.print(" Blynk Auto Control ",x=0,y=0)
textlcd.print("Press both switches to exit",x=0,y=2)
textlcd.cursorOff()

log = time.time()

while switch_up.read() or switch_down.read():
    blynk.run()

    if time.time()-log >= 1:
        log = time.time()
        blynk.virtual_write(0,   "\n\nLight                :  "  +str(light_value)+"lx")
        blynk.virtual_write(0,    "\nTemperature         :   "   +str(temp_value)+"C")
        blynk.virtual_write(0,     "\nSoil     Moisture:    "    +str(soil_value)+"%")
        blynk.virtual_write(0,   "\nCO2                    :  "  +str(co2_value)+"ppm")

    if auto_mode is True:
        if temp_value > auto_temp:
            fan.on()
            window.open()
        else:
            fan.off()
            window.close()

        if light_value < auto_light:
            rgbledbar.setColor([255, 255, 255])
        else:
            rgbledbar.setColor([0, 0, 0])

        if soil_value < auto_soil_moisture:
            flag_pump = True
        else:
            flag_pump = False
            pump.off()

    if flag_pump == True:
        if waterlevel.read():
            pump.on()
        else:
            pump.off()

    time.sleep(0.001)

window.close()
rgbledbar.off()
fan.off()
pump.off()
textlcd.clear()
soil.setCallback(None)
light.setCallback(None)
tphg.setCallback(None)
co2.setCallback(None)