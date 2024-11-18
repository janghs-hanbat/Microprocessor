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
        if internal_tempval > auto_mode_temp:
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
        elif curr_scene = 1:
            text_lcd.print("{0:>8}".format("%0.2f%%" %external_humi_val), x=12, y=0)
            text_lcd.print("{0:>8}".format("%0.2f%%" %soil_moisture_val), x=12, y=1)
            text_lcd.print("{0:>8}".format("%dL" %internal_light_val), x=12, y=2)
            text_lcd.print("{0:>8}".format("%dL" %external_light_val), x=12, y=2)
            text_lcd.setCursor(0, curr_line)
        elif curr_scene = 2:
            text_lcd.print("{0:>8}".format("%dppm" %co2_val), x=12, y=0)
            text_lcd.print("{0:>8}".format("FULL" if water_level_val else "WARNING"), x=12, y=1)
            text_lcd.print("{0:>8}".format(""), x=12, y=2)
            text_lcd.print("{0:>8}".format(""), x=12, y=3)
            text_lcd.setCursor(0, curr_line)
        elif curr_scene == 3:
            text_lcd.print("{0:>8}".format("ON" if fan_status else "OFF"), x=12, y=0)
            text_lcd.print("{0:>8}".format("OPEN" if window_opening else "CLOSE"), x=12, y=1)
            text_lcd.print("{0:>8}".format("ON" if rgb_status else "OFF"), x=12, y=2)
            text_lcd.print("{0:>8}".format("ON" if water_pump else "OFF"), x=12, y=3)
            text_lcd.setCursor(0, curr_line)
        elif curr_scene == 4:
            text_lcd.print("{0:>8}".format("%0.1f" % auto_mode_temp), x=12, y=0)
            text_lcd.print("{0:>8}".format("%0.2f%%" % auto_mode_humi), x=12, y=1)
            text_lcd.print("{0:>8}".format("%0.2f%%" % auto_mode_soil_moisture), x=12, y=2)
            text_lcd.print("{0:>8}".format("%dL" % auto_mode_light), x=12, y=3)
            text_lcd.setCursor(0, curr_line)
        
        if water_pump_status = True:
            if water_level_val:
                water_pump.on()
            else:
                water_pump.off()
        
        time.sleep_ms(1)