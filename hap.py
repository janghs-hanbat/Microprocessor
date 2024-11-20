import time
from pop import Window, Switch, Fan, RgbLedBar, Light, Tphg, CO2, Textlcd
from network import WLAN
import BlynkLib

# 초기 설정
auto_temp = 20  # reference Temperature value
auto_light = 20  # reference Light value
BLYNK_AUTH = 'n0p7uTSl6t0pTJMyCxdGcPgPojbxZQiJ'
SSID = 'Hanbat_WLAN_Guest'
PASSWORD = ''

auto_mode = False
light_value = temp_value = co2_value = 0
color_value = [0, 0, 0]

# 장치 초기화
switch_up = Switch('P8')
switch_down = Switch('P23')
fan = Fan()
window = Window()
rgbledbar = RgbLedBar()
internal_light = Light(0x5C)
external_light = Light(0x23)
internal_temp_humi = Tphg(0x76)
external_temp_humi = Tphg(0x77)
co2 = CO2()
textlcd = Textlcd()

# Wi-Fi 연결 설정
wlan = WLAN(mode=WLAN.STA)
wlan.connect(SSID, auth=(WLAN.WPA2, PASSWORD))
while not wlan.isconnected():
    print('x')  # Wi-Fi 연결 대기

# Blynk 연결 설정
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# 센서 값 초기화
internal_light_val = internal_light.read()
external_light_val = external_light.read()
internal_temp_val, _, internal_humi_val, _ = internal_temp_humi.read()
external_temp_val, _, external_humi_val, _ = external_temp_humi.read()
co2_val = co2.read()

window_opening = False
rgb_status = False
fan_status = False

# Blynk 콜백 함수 정의
@blynk.on("V1")
def Auto_Callback(value):
    global auto_mode
    auto_mode = value[0] == '1'
    print("Auto mode: %s" % ('on' if auto_mode else 'off'))

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

# 센서 콜백 함수 정의
def light_callback(param):
    global light_value
    light_value = param.read()

def tphg_callback(param):
    global temp_value
    temp_value = param.read()[0]

def co2_callback(param):
    global co2_value
    co2_value = param.read()

# 콜백 설정
internal_light.setCallback(func=light_callback, param=internal_light)
tphg = internal_temp_humi  # 내부 온도/습도만 사용
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
    blynk.run()  # Blynk 동작

    # 물리적 버튼 기반 제어
    if not switch_up.read():
        if auto_mode:  # Auto mode 전환
            auto_mode = False
        else:
            auto_mode = True

    # Blynk와 물리 버튼 동시 상태 처리
    if auto_mode:
        if temp_value > auto_temp:
            fan.on()
            window.open()
            fan_status = True
            window_opening = True
        else:
            fan.off()
            window.close()
            fan_status = False
            window_opening = False

        if light_value < auto_light:
            rgbledbar.setColor([255, 255, 255])
        else:
            rgbledbar.setColor([0, 0, 0])

    if time.time() - log >= 1:
        log = time.time()
        blynk.virtual_write(0, f"\nLight: {light_value}lx\nTemp: {temp_value}C\nCO2: {co2_value}ppm")
        textlcd.clear()
        textlcd.print(f"Light: {light_value}lx", x=0, y=0)
        textlcd.print(f"Temp: {temp_value}C", x=0, y=1)
        textlcd.print(f"CO2: {co2_value}ppm", x=0, y=2)

    time.sleep(0.001)

# 프로그램 종료 처리
window.close()
rgbledbar.off()
fan.off()
textlcd.clear()
internal_light.setCallback(None)
tphg.setCallback(None)
co2.setCallback(None)
