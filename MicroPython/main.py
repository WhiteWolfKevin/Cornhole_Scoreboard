# Library Imports
import time
import tm1637
import machine
from machine import Pin
from machine import Timer
from utime import sleep

# Buttons
team_a_minus_button = Pin(9, Pin.IN, Pin.PULL_UP)
team_a_plus_button = Pin(10, Pin.IN, Pin.PULL_UP)
team_b_minus_button = Pin(11, Pin.IN, Pin.PULL_UP)
team_b_plus_button = Pin(12, Pin.IN, Pin.PULL_UP)
clear_button = Pin(13, Pin.IN, Pin.PULL_UP)

# Button timers
team_a_plus_button_last = time.ticks_ms()
team_a_minus_button_last = time.ticks_ms()
team_b_plus_button_last = time.ticks_ms()
team_b_minus_button_last = time.ticks_ms()
clear_button_last = time.ticks_ms()

# Button timeouts in milliseconds
BUTTON_PRESS_TIMEOUT = 200
CLEAR_BUTTON_TIMEOUT = 2000
DEBOUNCE_PERIOD = 100
BRIGHTNESS_ADJUST_TIMEOUT = 4000

# Team Class
class Team():
    def __init__(self, name, scoreboard, brightness, score):
        self.name = name
        self.scoreboard = scoreboard
        self.brightness = brightness
        self.previous_brightness = -1
        self.score = score
        self.previous_score = -1
    
    def set_brightness(self):
        self.scoreboard.brightness(self.brightness)
        
    def display_brightness(self):
        self.scoreboard.number(self.brightness)
        self.scoreboard.show("B--",str(self.brightness))
        self.previous_brightness = self.brightness
        
    def increase_brightness(self):
        if (self.brightness < 3):
            self.brightness += 1
            self.set_brightness()
            
            # Write the brightness level to a text file to save between shutdowns
            with open("team_" + self.name + "_brightness.txt", 'w') as f:
                f.write(str(self.brightness))
        
    def decrease_brightness(self):
        if (self.brightness > 0):
            self.brightness -= 1
            self.set_brightness()
            
            # Write the brightness level to a text file to save between shutdowns
            with open("team_" + self.name + "_brightness.txt", 'w') as f:
                f.write(str(self.brightness))
        
    def display_score(self):
        self.scoreboard.number(self.score)
        self.previous_score = self.score
        
    def increase_score(self):
        if (self.score < 9999):
            self.score += 1
        
    def decrease_score(self):
        if (self.score > 0):
            self.score -= 1

# Button Debounce Handler
def debounce(pin):
    timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_PERIOD, callback=lambda t: button_handler(pin))

# Button handler
def button_handler(pin):
    print(pin)
    global team_a_plus_button_last,\
           team_a_minus_button_last,\
           team_b_plus_button_last,\
           team_b_minus_button_last,\
           clear_button_last,\
           brightness_edit_mode,\
           BUTTON_PRESS_TIMEOUT,\
           CLEAR_BUTTON_TIMEOUT,\
           BRIGHTNESS_ADJUST_TIMEOUT
    
    # Determine what button is pressed
    if (pin is team_a_plus_button and not brightness_edit_mode):
        team_a.increase_score() 

    elif (pin is team_a_minus_button and not brightness_edit_mode):
        team_a.decrease_score()
            
    elif (pin is team_b_plus_button and not brightness_edit_mode):
        team_b.increase_score()

    elif (pin is team_b_minus_button and not brightness_edit_mode):
        team_b.decrease_score()
            
    elif (pin is clear_button):
        clear_button_start_time = time.ticks_ms()
        
        while (pin.value() == 0):
            if (time.ticks_diff(time.ticks_ms(), clear_button_start_time) > CLEAR_BUTTON_TIMEOUT and not brightness_edit_mode):
                team_a.score = 0
                team_b.score = 0
                team_a.display_score()
                team_b.display_score()
                clear_button_last = time.ticks_ms()
                
            if (time.ticks_diff(time.ticks_ms(), clear_button_start_time) > BRIGHTNESS_ADJUST_TIMEOUT):
                if (not brightness_edit_mode):
                    team_a.display_brightness()
                    team_b.display_brightness()
                    brightness_edit_mode = True
                # After clearing, modify the brightness with button presses
                if (team_a_plus_button.value() == 0):
                    team_a.increase_brightness()
                    time.sleep(0.2)
                    team_a.display_brightness()
                elif (team_a_minus_button.value() == 0):
                    team_a.decrease_brightness()
                    time.sleep(0.2)
                    team_a.display_brightness()
                elif (team_b_plus_button.value() == 0):
                    team_b.increase_brightness()
                    time.sleep(0.2)
                    team_b.display_brightness()
                elif (team_b_minus_button.value() == 0):
                    team_b.decrease_brightness()
                    time.sleep(0.2)
                    team_b.display_brightness()
                sleep(0.1)
                
        brightness_edit_mode = False

    print("DISPLAYING SCORE")
    team_a.display_score()
    team_b.display_score()

# Get Brightness for Displays from .txt files
f = open('team_a_brightness.txt')
team_a_brightness = int(f.read())
f.close()

f = open('team_b_brightness.txt')
team_b_brightness = int(f.read())
f.close()

# Create Team objects
team_a = Team("a", (tm1637.TM1637(clk=Pin(15), dio=Pin(14))), team_a_brightness, 0)
team_b = Team("b", (tm1637.TM1637(clk=Pin(16), dio=Pin(17))), team_b_brightness, 0)

# Set display brightness
team_a.set_brightness()
team_b.set_brightness()

# Display the name
team_a.scoreboard.show("CORN")
team_b.scoreboard.show("HOLE")
time.sleep(3)
team_a.display_score()
team_b.display_score()
brightness_edit_mode = False

timer = Timer(-1)
team_a_plus_button.irq(trigger = machine.Pin.IRQ_RISING, handler=lambda pin: debounce(team_a_plus_button))
team_a_minus_button.irq(trigger = machine.Pin.IRQ_RISING, handler=lambda pin: debounce(team_a_minus_button))
team_b_plus_button.irq(trigger = machine.Pin.IRQ_RISING, handler=lambda pin: debounce(team_b_plus_button))
team_b_minus_button.irq(trigger = machine.Pin.IRQ_RISING, handler=lambda pin: debounce(team_b_minus_button))
clear_button.irq(trigger = machine.Pin.IRQ_FALLING, handler=lambda pin: debounce(clear_button))
