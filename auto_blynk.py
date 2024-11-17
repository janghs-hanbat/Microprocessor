from pop import Window, Switch, Fan, RgbLedBar, WaterPump, WaterLevel, Light, Tphg, SoilMoisture, CO2, Textlcd
from network import WLAN
import blynklib
import time

auto_temp = 20 # reference Temperature value
auto_light = 20 # reference Light value
auto_soil_moisture = 30 # reference Soil Moisture value
BLYNK_AUTH = 'n0p7uTSl6t0pTJMyCxdGcPgPojbxZQiJ'
SSID = 'hanbat_WLAN_guest'
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

blynk = blynklib.Blynk(BLYNK_AUTH)
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
