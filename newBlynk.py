from pop import Window, Switch, Fan, RgbLedBar, Light, Tphg, CO2, Textlcd
from network import WLAN
import BlynkLib
import time

auto_temp = 20  # reference Temperature value
auto_light = 20  # reference Light value
BLYNK_AUTH = 'n0p7uTSl6t0pTJMyCxdGcPgPojbxZQiJ'
SSID = 'Hanbat_WLAN_Guest'
PASSWORD = ''

auto_mode = False
light_value = temp_value = co2_value = 0
color_value = [0, 0, 0]

switch_up = Switch('P8')
switch_down = Switch('P23')
fan = Fan()
window = Window()
rgbledbar = RgbLedBar()
tphg = Tphg(0x76)
light = Light(0x5C)
co2 = CO2()
textlcd = Textlcd()

# Wi-Fi 연결 설정
wlan = WLAN(mode=WLAN.STA)
wlan.connect(SSID, auth=(WLAN.WPA2, PASSWORD))
while not wlan.isconnected():
    print('x')  # 원래는 print(x)가아니라 time.sleep(1)

# Blynk 연결 설정
blynk = BlynkLib.Blynk(BLYNK_AUTH)
blynk.run()

# 센서 콜백 함수
def light_callback(param):
    global light_value
    light_value = param.read()

def tphg_callback(param):
    global temp_value
    temp_value = param.read()[0]

def co2_callback(param):
    global co2_value
    co2_value = param.read()

# Blynk 가상 핀 제어 함수
@blynk.on("V1")
def Auto_Callback(value):
    global auto_mode
    auto_mode = value[0] == '1'
    print("auto mode %s" % ('on' if auto_mode else 'off'))

@blynk.on("V2")
def Temp_Callback(value):
    global auto_temp
    auto_temp = int(value[0])

@blynk.on("V4")
def Light_Callback(value):
    global auto_light
    auto_light = int(value[0])

@blynk.on("V5")
def RgbLedBar_R_Callback(value):
    if not auto_mode:
        global color_value
        color_value[0] = int(value[0])
        rgbledbar.setColor(color_value)

@blynk.on("V6")
def RgbLedBar_G_Callback(value):
    if not auto_mode:
        global color_value
        color_value[1] = int(value[0])
        rgbledbar.setColor(color_value)

@blynk.on("V7")
def RgbLedBar_B_Callback(value):
    if not auto_mode:
        global color_value
        color_value[2] = int(value[0])
        rgbledbar.setColor(color_value)

@blynk.on("V8")
def Fan_Callback(value):
    if not auto_mode:
        if value[0] == '1':
            fan.on()
        else:
            fan.off()

@blynk.on("V10")
def Window_Callback(value):
    if not auto_mode:
        if value[0] == '1':
            window.open()
        else:
            window.close()

# 센서 콜백 설정
light.setCallback(func=light_callback, param=light)
tphg.setCallback(func=tphg_callback, param=tphg)
co2.setCallback(func=co2_callback, param=co2)

# 장치 초기화
rgbledbar.on()
textlcd.print(" Blynk Auto Control ", x=0, y=0)
textlcd.print("Press both switches to exit", x=0, y=2)
textlcd.cursorOff()

log = time.time()

# 메인 루프
while switch_up.read() or switch_down.read():
    blynk.run()

    if time.time() - log >= 1:
        log = time.time()
        blynk.virtual_write(0, "\n\nLight                :  " + str(light_value) + "lx")
        blynk.virtual_write(0, "\nTemperature         :   " + str(temp_value) + "C")
        blynk.virtual_write(0, "\nCO2                    :  " + str(co2_value) + "ppm")

    if auto_mode:
        # 자동 모드 제어
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

    time.sleep(0.001)

# 프로그램 종료 처리
window.close()
rgbledbar.off()
fan.off()
textlcd.clear()

# 콜백 해제
light.setCallback(None)
tphg.setCallback(None)
co2.setCallback(None)
