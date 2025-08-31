import time
from machine import Pin, I2C
import ssd1306
from lib.large_digits import LARGE_DIGITS

# =====================
# I2C & OLED setup
# =====================
# I2C0: GP14=SDA, GP15=SCL
i2c_bus_0 = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
# I2C1: GP18=SDA, GP19=SCL
i2c_bus_1 = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

oled_a = ssd1306.SSD1306_I2C(128, 64, i2c_bus_0, addr=0x3C)
oled_b = ssd1306.SSD1306_I2C(128, 64, i2c_bus_1, addr=0x3C)

# =====================
# Button setup
# =====================
team_a_minus_button = Pin(9, Pin.IN, Pin.PULL_UP)
team_a_plus_button  = Pin(10, Pin.IN, Pin.PULL_UP)
team_b_minus_button = Pin(11, Pin.IN, Pin.PULL_UP)
team_b_plus_button  = Pin(12, Pin.IN, Pin.PULL_UP)
clear_button        = Pin(13, Pin.IN, Pin.PULL_UP)

# Timeouts (ms)
DEBOUNCE_MS           = 150
CLEAR_HOLD_MS         = 3000
BRIGHTNESS_HOLD_MS    = 4000
INITIAL_HOLD_DELAY_MS = 700
REPEAT_RATE_MS        = 200

# =====================
# Large number drawing
# =====================
def draw_digit(oled, digit, x, y, scale=4):
    bitmap = LARGE_DIGITS[digit]
    for row_idx, row in enumerate(bitmap):
        for col_idx, c in enumerate(row):
            if c == "1":
                for sx in range(scale):
                    for sy in range(scale):
                        oled.pixel(x + col_idx*scale + sx, y + row_idx*scale + sy, 1)

def draw_number(oled, number):
    s = str(number)
    oled.fill(0)
    scale = (64 // 7) - 1  # 8
    total_width = len(s) * 8 * scale
    x_offset = max((128 - total_width)//2, 0)  # center horizontally
    total_height = 7 * scale
    y_offset = max((64 - total_height)//2, 0)   # center vertically
    for i, ch in enumerate(s):
        draw_digit(oled, ch, x_offset + i*8*scale, y_offset, scale)
    oled.show()

# =====================
# Load/save brightness
# =====================
def load_brightness(fname, default=2):
    try:
        with open(fname) as f:
            return int(f.read())
    except:
        return default

def save_brightness(fname, val):
    with open(fname, "w") as f:
        f.write(str(val))

# =====================
# Team class
# =====================
class Team:
    def __init__(self, name, oled, brightness, score_file, score=0):
        self.name = name
        self.oled = oled
        self.brightness = brightness
        self.score_file = score_file
        self.score = score
        self.set_brightness()
        self.display_score()

    def set_brightness(self):
        contrast = int((self.brightness / 7) * 255)
        self.oled.contrast(contrast)

    def display_score(self):
        draw_number(self.oled, self.score)

    def save_score(self):
        with open(self.score_file, "w") as f:
            f.write(str(self.score))

    def load_score(self):
        try:
            with open(self.score_file) as f:
                self.score = int(f.read())
        except:
            self.score = 0

    def increase_score(self):
        if self.score >= 99:
            self.score = 0
        else:
            self.score += 1
        self.save_score()

    def decrease_score(self):
        if self.score > 0:
            self.score -= 1
            self.save_score()

    def increase_brightness(self):
        if self.brightness < 7:
            self.brightness += 1
            self.set_brightness()

    def decrease_brightness(self):
        if self.brightness > 0:
            self.brightness -= 1
            self.set_brightness()

    def display_brightness(self):
        self.oled.fill(0)
        self.oled.text("Brightness", 0, 20)
        self.oled.text(str(self.brightness), 0, 40)
        self.oled.show()

# =====================
# Initialize teams
# =====================
team_a = Team(
    "a",
    oled_a,
    load_brightness("team_a_brightness.txt"),
    "team_a_score.txt"
)
team_a.load_score()
team_a.display_score()

team_b = Team(
    "b",
    oled_b,
    load_brightness("team_b_brightness.txt"),
    "team_b_score.txt"
)
team_b.load_score()
team_b.display_score()

# =====================
# State tracking
# =====================
last_press = {
    "a_minus": 0,
    "a_plus": 0,
    "b_minus": 0,
    "b_plus": 0,
    "clear": 0
}
hold_start = {
    "a_minus": None,
    "a_plus": None,
    "b_minus": None,
    "b_plus": None
}

clear_pressed_at = None
in_brightness_mode = False
reset_armed = False

# =====================
# Main loop
# =====================
while True:
    now = time.ticks_ms()

    # --- handle clear button hold ---
    if clear_button.value() == 0:
        if clear_pressed_at is None:
            clear_pressed_at = now
            reset_armed = True
        held = time.ticks_diff(now, clear_pressed_at)
        if not in_brightness_mode and held >= BRIGHTNESS_HOLD_MS:
            in_brightness_mode = True
            team_a.display_brightness()
            team_b.display_brightness()
        elif reset_armed and not in_brightness_mode and held >= CLEAR_HOLD_MS:
            team_a.score = 0
            team_b.score = 0
            team_a.display_score()
            team_b.display_score()
            team_a.save_score()
            team_b.save_score()
            reset_armed = False
    else:
        if in_brightness_mode:
            team_a.display_score()
            team_b.display_score()
        clear_pressed_at = None
        in_brightness_mode = False
        reset_armed = False

    # --- helper to check buttons with hold/auto-repeat ---
    def check_button(pin, key, action):
        if pin.value() == 0:
            if hold_start[key] is None:
                hold_start[key] = now
                action()
                last_press[key] = now
            else:
                held = time.ticks_diff(now, hold_start[key])
                if held >= INITIAL_HOLD_DELAY_MS:
                    if time.ticks_diff(now, last_press[key]) >= REPEAT_RATE_MS:
                        action()
                        last_press[key] = now
        else:
            hold_start[key] = None

    # --- button handling ---
    if in_brightness_mode:
        check_button(team_a_plus_button, "a_plus", lambda: (team_a.increase_brightness(),
                                                           save_brightness("team_a_brightness.txt", team_a.brightness),
                                                           team_a.display_brightness()))
        check_button(team_a_minus_button, "a_minus", lambda: (team_a.decrease_brightness(),
                                                             save_brightness("team_a_brightness.txt", team_a.brightness),
                                                             team_a.display_brightness()))
        check_button(team_b_plus_button, "b_plus", lambda: (team_b.increase_brightness(),
                                                           save_brightness("team_b_brightness.txt", team_b.brightness),
                                                           team_b.display_brightness()))
        check_button(team_b_minus_button, "b_minus", lambda: (team_b.decrease_brightness(),
                                                             save_brightness("team_b_brightness.txt", team_b.brightness),
                                                             team_b.display_brightness()))
    else:
        check_button(team_a_plus_button, "a_plus", lambda: (team_a.increase_score(), team_a.display_score()))
        check_button(team_a_minus_button, "a_minus", lambda: (team_a.decrease_score(), team_a.display_score()))
        check_button(team_b_plus_button, "b_plus", lambda: (team_b.increase_score(), team_b.display_score()))
        check_button(team_b_minus_button, "b_minus", lambda: (team_b.decrease_score(), team_b.display_score()))

    time.sleep_ms(20)
