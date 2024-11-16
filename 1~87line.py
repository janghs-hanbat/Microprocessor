import time
from pop import Switch, Fan, Textlcd, Light, Tphg, RgbLedBar, WaterPump, Window, SoilMoisture, WaterLevel, CO2

internal_light = Light(0x5C)
external_light = Light(0x23)
internal_temp_humi = Tphg(0x76)
external_temp_humi = Tphg(0x77)
soil_mositure = SoilMoisture()
co2 = CO2()
window = Window()
rgb_led = RgbLedBar()
water_pump = WaterPump()
water_level = WaterLevel()
fan = Fan()
switch_up = Switch('P8')
switch_down = Switch('P23')
text_lcd = Textlcd()

internal_light_val = internal_light.read()
external_light_val = external_light.read()
internal_temp_val,_,internal_humi_val,_ = internal_temp_humi.read()
external_temp_val,_,external_humi_val,_ = external_temp_humi.read()
soil_moisture_val = soil_moisture.calcSoilMoisture(soil_mositure.read())
co2_val = co2.read()
water_level_val = water_level.read()

window_opening = False
rgb_status = False
water_pump_status = False
fan_status = False

auto_mode = False
auto_mode_light = 0.0
auto_mode_temp = 0.0
auto_mode_humi = 0.0
auto_mode_soil_moisture = 0.0

prev_scene = 0
prev_line = 0
curr_scene = 0
curr_line = 0

MAIN_SCENE_TEXT = [
                    ["Mode       :", "Intern Temp:", "Intern Humi:", "Extern Temp:"],
                    ["Extern Humi:", "Soil moist :", "InternLight:", "ExternLight:"],
                    ["CO2        :", "Water Level:", "            ", "            "],
                    ["Fan        :", "Window     :", "RGB LED Bar:", "Water Pump :"],
                    ["Auto Temp  :", "Auto Humi  :", "Auto Moist :", "Auto Light :"]
                   ]

def light_in_callback(param):
    global internal_light_val
    internal_light_val = param.read()
    
def light_ex_callback(param):
    global external_light_val
    external_light_val = param.read()

def temphumi_in_callback(param):
    global internal_temp_val
    global internal_humi_val
    internal_temp_val,_,internal_humi_val,_ = param.read()

def temphumi_ex_callback(param):
    global external_temp_val
    global external_humi_val
    external_temp_val,_,external_humi_val,_ = param.read()

def soil_moisture_callback(value, param):
    global soil_moisture_val
    soil_moisture_val = param.calcSoilMoisture(value)

def co2_callback(param):
    global co2_val
    co2_val = param.read()

def waterlevel_callback(param):
    global water_level_val
    water_level_val = param.read()

internal_light.setCallback(func = light_in_callback, param = internal_light)
external_light.setCallback(func = light_ex_callback, param = external_light)
internal_temp_humi.setCallback(func = temphumi_in_callback, param = internal_temp_humi)
external_temp_humi.setCallback(func = temphumi_ex_callback, param = external_temp_humi)
soil_moisture.setCallback(func = soil_moisture_callback, type = soil_moisture.TYPE_NORMAL, param = soil_moisture)
co2.setCallback(func = co2_callback, param = co2)
water_level.setCallback(func = waterlevel_callback, param = water_level)

window.close()
rgb_led.on()
rgb_led.setColor([0,0,0])
water_pump.off()
fan.off()
text_lcd.clear()

for i in range(4):
    text_lcd.print(MAIN_SCENE_TEXT[curr_scene][i],x = 0,y = i)
    text_lcd.setCursor(0,0)
    
while switch_up.read() or switch_down.read():
    if not switch_up.read():
        scene = curr_scene
        lin = curr_line
        if scene == 0:
            if line == 0:
                auto_mode = not auto_mode
        elif scene == 4:
            if line == 0:
                pass
            elif line == 1:
                pass
            elif line == 2:
                pass
            elif line == 3:
                auto_mode_light += 500
                if auto_mode_light > 10000:
                    auto_mode_light = 0
        elif not auto_mode:
            if scene == 3:
                if line == 0:
                    pass
                elif line == 1:
                    pass
                elif line == 2:
                    if not rgb_status:
                        rgb_led.setColor([255,255,255])
                        rgb_status = False
                elif line == 3:
                    pass
        time.sleep_ms(200)