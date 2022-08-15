# Library Imports
import time
import utime
import tm1637
from machine import Pin

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

# Button timeouts in milliseconds
button_press_timeout = 200
button_hold_timeout = 1500
clear_screen_timeout = 2000

# Team Class
class Team():
    def __init__(self, name, scoreboard, brightness, score):
        self.name = name
        self.scoreboard = scoreboard
        self.brightness = brightness
        self.score = score
        self.previous_score = -1
    
    def set_brightness(self):
        self.scoreboard.brightness(self.brightness)
        
    def increase_brightness(self):
        if (self.brightness < 3):
            self.brightness += 1
            self.set_brightness()
            
            # Write the brightness level to a text file to save between shutdowns
            f = open("team_" + self.name + "_brightness.txt", 'w')
            f.write(str(self.brightness))
            f.close()
        
    def decrease_brightness(self):
        if (self.brightness > 0):
            self.brightness -= 1
            self.set_brightness()
            
            # Write the brightness level to a text file to save between shutdowns
            f = open("team_" + self.name + "_brightness.txt", 'w')
            f.write(str(self.brightness))
            f.close()
        
    def display_score(self):
        
        if (self.score != self.previous_score):
            self.scoreboard.number(self.score)
            self.previous_score = self.score
        
    def increase_score(self):
        if (self.score < 9999):
            self.score += 1
        
    def decrease_score(self):
        if (self.score > 0):
            self.score -= 1


# Button handler
def button_handler(pin):
    global team_a_plus_button,\
           team_a_minus_button,\
           team_a_plus_button_last,\
           team_a_minus_button_last,\
           team_b_plus_button,\
           team_b_minus_button,\
           team_b_plus_button_last,\
           team_b_minus_button_last,\
           clear_button
    
    # Determine what button is pressed
    if pin is team_a_plus_button:
        team_a_plus_button_start_time = time.ticks_ms()
        
        if (time.ticks_diff(time.ticks_ms(), team_a_plus_button_last) > button_press_timeout):
            team_a.increase_score()
                
            while (team_a_plus_button.value()):
                print("team_a_plus_button is being held " + str(time.ticks_ms()))
                if (time.ticks_diff(time.ticks_ms(), team_a_plus_button_start_time) > button_hold_timeout):
                    team_a.increase_score()

                team_a.display_score()
                time.sleep(0.1)
                
            team_a_plus_button_last = time.ticks_ms()

    elif pin is team_a_minus_button:    
        team_a_minus_button_start_time = time.ticks_ms()
        
        if (time.ticks_diff(time.ticks_ms(), team_a_minus_button_last) > button_press_timeout):
            team_a.decrease_score()
                
            while (team_a_minus_button.value()):
                print("team_a_minus_button is being held " + str(time.ticks_ms()))
                if (time.ticks_diff(time.ticks_ms(), team_a_minus_button_start_time) > button_hold_timeout):
                    team_a.decrease_score()

                team_a.display_score()
                time.sleep(0.1)
                
            team_a_minus_button_last = time.ticks_ms()
            
    elif pin is team_b_plus_button:
        team_b_plus_button_start_time = time.ticks_ms()
        
        if (time.ticks_diff(time.ticks_ms(), team_b_plus_button_last) > button_press_timeout):
            team_b.increase_score()
                
            while (team_b_plus_button.value()):
                if (time.ticks_diff(time.ticks_ms(), team_b_plus_button_start_time) > button_hold_timeout):
                    team_b.increase_score()

                team_b.display_score()
                time.sleep(0.1)
                
            team_b_plus_button_last = time.ticks_ms()

    elif pin is team_b_minus_button:
        team_b_minus_button_start_time = time.ticks_ms()
        
        if (time.ticks_diff(time.ticks_ms(), team_b_minus_button_last) > button_press_timeout):
            team_b.decrease_score()
                
            while (team_b_minus_button.value()):
                if (time.ticks_diff(time.ticks_ms(), team_b_minus_button_start_time) > button_hold_timeout):
                    team_b.decrease_score()

                team_b.display_score()
                time.sleep(0.1)
                
            team_b_minus_button_last = time.ticks_ms()
            
    elif pin is clear_button:
        clear_button_start_time = time.ticks_ms()
          
        while (clear_button.value()):
            if (time.ticks_diff(time.ticks_ms(), clear_button_start_time) > clear_screen_timeout):
                team_a.score = 0
                team_b.score = 0
                
                # After clearing, modify the brightness with button presses
                if (team_a_plus_button.value()):
                    team_a.increase_brightness()
                    time.sleep(0.2)
                    
                elif (team_a_minus_button.value()):
                    team_a.decrease_brightness()
                    time.sleep(0.2)
                    
                if (team_b_plus_button.value()):
                    team_b.increase_brightness()
                    time.sleep(0.2)
                    
                elif (team_b_minus_button.value()):
                    team_b.decrease_brightness()
                    time.sleep(0.2)

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

# Program main loop
while True:
    
    team_a.display_score()
    team_b.display_score()
    
    team_a_plus_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)
    team_a_minus_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)
    team_b_plus_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)
    team_b_minus_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)
    clear_button.irq(trigger = machine.Pin.IRQ_RISING, handler = button_handler)