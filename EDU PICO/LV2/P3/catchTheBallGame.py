import board
import busio
import digitalio
import time
import random
import adafruit_ssd1306
import simpleio
from analogio import AnalogIn

# Initialize OLED Display (I2C)
i2c = busio.I2C(board.GP5, board.GP4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
# Initialize Potentiometer
potentio = AnalogIn(board.GP28)

# Initialize Buttons
button_A = digitalio.DigitalInOut(board.GP0)
button_B = digitalio.DigitalInOut(board.GP1)
button_A.direction = digitalio.Direction.INPUT
button_B.direction = digitalio.Direction.INPUT
button_A.pull = digitalio.Pull.UP
button_B.pull = digitalio.Pull.UP

# Buzzer pin
buzzer_pin = board.GP21

# Game constants
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 3
BALL_SIZE = 3
BALL_SPEED = 2
PADDLE_Y = SCREEN_HEIGHT - 8

# Game variables
score = 0
game_state = "start"  # "start", "playing", "paused", "game_over"
ball_x = 0
ball_y = 0
paddle_x = 50
ball_speed = BALL_SPEED

# Button debouncing
button_A_previous = True
button_B_previous = True

def play_catch_sound():
    """Play sound when ball is caught"""
    simpleio.tone(buzzer_pin, 880, 0.1)  # High pitch
    simpleio.tone(buzzer_pin, 1047, 0.1)

def play_miss_sound():
    """Play sound when ball is missed"""
    simpleio.tone(buzzer_pin, 200, 0.3)  # Low pitch

def play_start_sound():
    """Play sound when game starts"""
    simpleio.tone(buzzer_pin, 523, 0.2)
    simpleio.tone(buzzer_pin, 659, 0.2)
    simpleio.tone(buzzer_pin, 784, 0.2)

def reset_ball():
    """Reset ball to random position at top"""
    global ball_x, ball_y, ball_speed
    ball_x = random.randint(5, SCREEN_WIDTH - 5)
    ball_y = 0
    ball_speed = BALL_SPEED + (score // 5)  # Speed increases every 5 points

def draw_start_screen():
    """Draw the start screen"""
    oled.fill(0)
    oled.text("CATCH THE BALL", 10, 10, 1)
    oled.text("Press A to", 25, 30, 1)
    oled.text("START", 45, 40, 1)
    oled.show()

def draw_game_screen():
    """Draw the game playing screen"""
    oled.fill(0)
    
    # Draw score
    oled.text(f"Score:{score}", 0, 0, 1)
    
    # Draw paddle
    oled.fill_rect(int(paddle_x), PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 1)
    
    # Draw ball
    oled.fill_rect(int(ball_x), int(ball_y), BALL_SIZE, BALL_SIZE, 1)
    
    # Draw ground line
    oled.hline(0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)
    
    oled.show()

def draw_pause_screen():
    """Draw the pause screen"""
    oled.fill(0)
    oled.text(f"PAUSED", 40, 20, 1)
    oled.text(f"Score: {score}", 35, 35, 1)
    oled.text("Press B", 35, 50, 1)
    oled.show()

def draw_game_over_screen():
    """Draw the game over screen"""
    oled.fill(0)
    oled.text("GAME OVER!", 25, 15, 1)
    oled.text(f"Score: {score}", 35, 30, 1)
    oled.text("Press A to", 25, 45, 1)
    oled.text("restart", 40, 55, 1)
    oled.show()

def update_paddle():
    """Update paddle position based on potentiometer"""
    global paddle_x
    pot_value = potentio.value
    # Map potentiometer value (0-65535) to paddle position (0 to SCREEN_WIDTH - PADDLE_WIDTH)
    paddle_x = (pot_value / 65535) * (SCREEN_WIDTH - PADDLE_WIDTH)

def update_ball():
    """Update ball position and check for collisions"""
    global ball_y, score, game_state
    
    # Move ball down
    ball_y += ball_speed
    
    # Check if ball reached paddle level
    if ball_y + BALL_SIZE >= PADDLE_Y:
        # Check if ball hit the paddle
        if (ball_x + BALL_SIZE >= paddle_x and 
            ball_x <= paddle_x + PADDLE_WIDTH):
            # Ball caught!
            score += 1
            play_catch_sound()
            reset_ball()
        elif ball_y >= SCREEN_HEIGHT - 5:
            # Ball missed - game over
            play_miss_sound()
            game_state = "game_over"

def check_buttons():
    """Check button presses with debouncing"""
    global game_state, score, button_A_previous, button_B_previous
    
    button_A_current = button_A.value
    button_B_current = button_B.value
    
    # Button A - Start/Restart
    if button_A_previous and not button_A_current:
        if game_state == "start" or game_state == "game_over":
            score = 0
            reset_ball()
            play_start_sound()
            game_state = "playing"
    
    # Button B - Pause/Unpause
    if button_B_previous and not button_B_current:
        if game_state == "playing":
            game_state = "paused"
        elif game_state == "paused":
            game_state = "playing"
    
    button_A_previous = button_A_current
    button_B_previous = button_B_current

# Initialize game
print("Catch the Ball Game Starting!")
print("Controls:")
print("  Potentiometer: Move paddle")
print("  Button A: Start/Restart")
print("  Button B: Pause/Unpause")
reset_ball()

# Main game loop
while True:
    check_buttons()
    
    if game_state == "start":
        draw_start_screen()
    
    elif game_state == "playing":
        update_paddle()
        update_ball()
        draw_game_screen()
    
    elif game_state == "paused":
        draw_pause_screen()
    
    elif game_state == "game_over":
        draw_game_over_screen()
    
    time.sleep(0.05)  # Small delay for smoother gameplay
