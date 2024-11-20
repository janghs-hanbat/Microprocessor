import time
from pop import Switch, Fan, Textlcd, Light, Tphg, RgbLedBar, WaterPump, Window, SoilMoisture, WaterLevel, CO2

internal_light = Light(0x5C)
external_light = Light(0x23)
internal_temp_humi = Tphg(0x76)
external_temp_humi = Tphg(0x77)
soil_moisture = SoilMoisture()
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
soil_moisture_val = soil_moisture.calcSoilMoisture(soil_moisture.read())
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
rgb_led.setColor([0, 0, 0])
water_pump.off()
fan.off()
text_lcd.clear()

for i in range(4):
    text_lcd.print(MAIN_SCENE_TEXT[curr_scene][i], x=0, y=i)
    text_lcd.setCursor(0, 0)

while switch_up.read() or switch_down.read():
    if not switch_up.read():
        scene = curr_scene
        line = curr_line
        if scene == 0:
            if line == 0:
                auto_mode = not auto_mode
        elif scene == 4:
            if line == 0:
                auto_mode_temp = auto_mode_temp + 10
                if auto_mode_temp > 100:
                    auto_mode_temp = 0
            elif line == 1:
                auto_mode_humi = auto_mode_humi + 10
                if auto_mode_humi > 100:
                    auto_mode_humi = 0
            elif line == 2:
                auto_mode_soil_moisture = auto_mode_soil_moisture + 10
                if auto_mode_soil_moisture > 100:
                    auto_mode_soil_moisture = 0
            elif line == 3:
                auto_mode_light = auto_mode_light + 500
                if auto_mode_light > 10000:
                    auto_mode_light = 0
        elif not auto_mode:
            if scene == 3:
                if line == 0:
                    if fan_status:
                        fan.off()
                        fan_status = False
                    else:
                        fan.on()
                        fan_status = True
                elif line == 1:
                    if window_opening:
                        window.close()
                        window_opening = False
                    else:
                        window.open()
                        window_opening = True
                elif line == 2:
                    if not rgb_status:
                        rgb_led.setColor([255, 255, 255])
                        rgb_status = True
                    else:
                        rgb_led.setColor([0, 0, 0])
                        rgb_status = False
                elif line == 3:
                    if not water_pump_status:
                        water_pump_status = True
                    else:
                        water_pump.off()
                        water_pump_status = False
        time.sleep_ms(200)

    if not switch_down.read():
        curr_line = curr_line + 1
        if curr_line > 3:
            curr_scene = curr_scene + 1
            if curr_scene > 4:
                curr_scene = 0
            curr_line = 0
            text_lcd.clear()
            for i in range(4):
                text_lcd.print(MAIN_SCENE_TEXT[curr_scene][i], line=i)
        text_lcd.setCursor(0, curr_line)
        time.sleep_ms(200)
    
    if auto_mode is True:
        if internal_temp_val > auto_mode_temp:
            fan.on()
            window.open()
            fan_status = True
            window_opening = True
        else:
            fan.off()
            window.close()
            fan_status = False
            window_opening = False
        
        if internal_light_val < auto_mode_light:
            rgb_led.setColor([255, 255, 255])
            rgb_status = True
        else:
            rgb_led.setColor([0, 0, 0])
            rgb_status = False

        if soil_moisture_val < auto_mode_soil_moisture or internal_humi_val < auto_mode_humi:
            water_pump_status = True
        else:
            water_pump_off()
            water_pump_status = False
    if curr_scene == 0:
        text_lcd.print("{0:>8}".format("AUTO" if auto_mode else "MANUAL"), x=12 y=0)
        text_lcd.print("{0:>8}".format("%0.1f'C" %internal_temp_val), x=12, y=1)
        text_lcd.print("{0:>8}".format("%0.2f%%" %internal_humi_val), x=12, y=2)
        text_lcd.print("{0:>8}".format("%0.1f'C" %external_temp_val), x=12, y=3)
        text_lcd.setCursor(0, curr_line)
    elif curr_scene == 1:
        text_lcd.print("{0:>8}".format("%0.2f%%" %external_humi_val), x=12, y=0)
        text_lcd.print("{0:>8}".format("%0.2f%%" %soil_moisture_val), x=12, y=1)
        text_lcd.print("{0:>8}".format("%dL" %internal_light_val), x=12, y=2)
        text_lcd.print("{0:>8}".format("%dL" %external_light_val), x=12, y=3)
        text_lcd.setCursor(0, curr_line)
    elif curr_scene == 2:
        text_lcd.print("{0:>8}".format("%dppm" %co2_val), x=12, y=0)
        text_lcd.print("{0:>8}".format("FULL" if water_level_val else "WARNING"), x=12, y=1)
        text_lcd.print("{0:>8}".format(""), x=12, y=2)
        text_lcd.print("{0:>8}".format(""), x=12, y=3)
        text_lcd.setCursor(0, curr_line)
    elif curr_scene == 3:
        text_lcd.print("{0:>8}".format("ON" if fan_status else "OFF"), x=12, y=0)
        text_lcd.print("{0:>8}".format("OPEN" if window_opening else "CLOSE"), x=12, y=1)
        text_lcd.print("{0:>8}".format("ON" if rgb_status else "OFF"), x=12, y=2)
        text_lcd.print("{0:>8}".format("ON" if water_pump_status else "OFF"), x=12, y=3)
        text_lcd.setCursor(0, curr_line)
    elif curr_scene == 4:
        text_lcd.print("{0:>8}".format("%0.1f" % auto_mode_temp), x=12, y=0)
        text_lcd.print("{0:>8}".format("%0.2f%%" % auto_mode_humi), x=12, y=1)
        text_lcd.print("{0:>8}".format("%0.2f%%" % auto_mode_soil_moisture), x=12, y=2)
        text_lcd.print("{0:>8}".format("%dL" % auto_mode_light), x=12, y=3)
        text_lcd.setCursor(0, curr_line)
        
    if water_pump_status == True:
        if water_level_val:
            water_pump.on()
        else:
            water_pump.off()
        
    time.sleep_ms(1)
        
text_lcd.clear()
text_lcd.displayOff()
water_pump.off()
fan.off()
window.close()
rgb_led.off()
internal_light.setCallback(None)
external_light.setCallback(None)
internal_temp_humi.setCallback(None)
external_temp_humi.setCallback(None)
soil_moisture.setCallback(None)
co2.setCallback(None)
water_level.setCallback(None)