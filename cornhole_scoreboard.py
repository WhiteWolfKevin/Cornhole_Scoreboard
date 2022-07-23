# Library Imports
import time
import utime
import tm1637
from machine import Pin

# TM1637 Displays
team_a_scoreboard = tm1637.TM1637(clk=Pin(15), dio=Pin(14))
team_b_scoreboard = tm1637.TM1637(clk=Pin(16), dio=Pin(17))

# Displays Brightness
team_a_scoreboard_brightness = 7
team_b_scoreboard_brightness = 7

# Buttons
team_a_plus_button = Pin(1, Pin.IN, Pin.PULL_DOWN)
team_a_minus_button = Pin(0, Pin.IN, Pin.PULL_DOWN)
team_b_plus_button = Pin(3, Pin.IN, Pin.PULL_DOWN)
team_b_minus_button = Pin(2, Pin.IN, Pin.PULL_DOWN)
clear_button = Pin(4, Pin.IN, Pin.PULL_DOWN)

# Button timers
team_a_plus_button_last = time.ticks_ms()
team_a_minus_button_last = time.ticks_ms()
team_b_plus_button_last = time.ticks_ms()
team_b_minus_button_last = time.ticks_ms()
clear_button_last = time.ticks_ms()

# Team Scores
team_a_score = 0
team_b_score = 0

# Set display brightness
team_a_scoreboard.brightness(team_a_scoreboard_brightness)
team_b_scoreboard.brightness(team_b_scoreboard_brightness)

# Button handler
def button_handler(pin):
    global team_a_plus_button,\
           team_a_minus_button,\
           team_a_plus_button_last,\
           team_a_minus_button_last,\
           team_a_score,\
           team_b_plus_button,\
           team_b_minus_button,\
           team_b_plus_button_last,\
           team_b_minus_button_last,\
           team_b_score,\
           clear_button
    
    # Determine what button is pressed
    if pin is team_a_plus_button:
        if (time.ticks_diff(time.ticks_ms(), team_a_plus_button_last) > 150):
            if (team_a_score < 9999):
                team_a_score += 1
            team_a_plus_button_last = time.ticks_ms()

    elif pin is team_a_minus_button:
        if (time.ticks_diff(time.ticks_ms(), team_a_minus_button_last) > 150):
            if (team_a_score > 0):
                team_a_score -= 1
            team_a_minus_button_last = time.ticks_ms()
            
    elif pin is team_b_plus_button:
        if (time.ticks_diff(time.ticks_ms(), team_b_plus_button_last) > 150):
            if (team_b_score < 9999):
                team_b_score += 1
            team_b_plus_button_last = time.ticks_ms()

    elif pin is team_b_minus_button:
        if (time.ticks_diff(time.ticks_ms(), team_b_minus_button_last) > 150):
            if (team_b_score > 0):
                team_b_score -= 1
            team_b_minus_button_last = time.ticks_ms()
            
    elif pin is clear_button:
        clear_button_start_time = time.ticks_ms()
          
        while (clear_button.value()):
            if (time.ticks_diff(time.ticks_ms(), clear_button_start_time) > 2000):
                team_a_score = 0
                team_b_score = 0
                
            team_a_scoreboard.number(team_a_score)
            team_b_scoreboard.number(team_b_score)


# Display the name
team_a_scoreboard.show("CORN")
team_b_scoreboard.show("HOLE")
time.sleep(3)

# Program main loop
while True:
    team_a_scoreboard.number(team_a_score)
    team_b_scoreboard.number(team_b_score)
    
    team_a_plus_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)
    team_a_minus_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)
    team_b_plus_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)
    team_b_minus_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)
    clear_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)