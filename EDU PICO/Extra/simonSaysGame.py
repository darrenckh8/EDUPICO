import board
import busio
import time
import random
import digitalio
import neopixel
import adafruit_ssd1306
import simpleio
from analogio import AnalogIn

# Hardware setup
i2c = busio.I2C(board.GP5, board.GP4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

pixels = neopixel.NeoPixel(board.GP14, 5, brightness=0.5, auto_write=False)

button_A = digitalio.DigitalInOut(board.GP0)
button_A.direction = digitalio.Direction.INPUT
button_A.pull = digitalio.Pull.UP

button_B = digitalio.DigitalInOut(board.GP1)
button_B.direction = digitalio.Direction.INPUT
button_B.pull = digitalio.Pull.UP

pot = AnalogIn(board.GP28)

buzzer_pin = board.GP21

# Game settings
LED_COLORS = [
    (255, 0, 0),      # LED 0: Red
    (0, 255, 0),      # LED 1: Green
    (0, 0, 255),      # LED 2: Blue
    (255, 255, 0),    # LED 3: Yellow
    (255, 0, 255),    # LED 4: Magenta
]

TONES = [262, 330, 392, 523, 659]  # C, E, G, C5, E5

# Game state
game_state = "menu"  # "menu", "playing", "watching", "game_over"
sequence = []
player_input = []
current_level = 0
score = 0
high_score = 0
lives = 3

last_button_A = True
last_button_B = True

def read_difficulty():
    """Read difficulty from potentiometer (1=Easy, 2=Medium, 3=Hard)"""
    pot_value = pot.value / 65535
    if pot_value < 0.33:
        return 1, "Easy"
    elif pot_value < 0.66:
        return 2, "Medium"
    else:
        return 3, "Hard"

def get_playback_speed(difficulty):
    """Get playback speed based on difficulty"""
    speeds = {1: 0.6, 2: 0.4, 3: 0.25}  # seconds per LED
    return speeds[difficulty]

def update_display():
    """Update OLED display"""
    oled.fill(0)
    
    if game_state == "menu":
        oled.text("SIMON SAYS", 25, 0, 1)
        oled.text(f"High Score: {high_score}", 15, 15, 1)
        
        diff_level, diff_name = read_difficulty()
        oled.text(f"Difficulty:", 20, 30, 1)
        oled.text(diff_name, 35, 40, 1)
        
        oled.text("Press A to Start", 5, 55, 1)
    
    elif game_state == "watching":
        oled.text("WATCH!", 40, 20, 1)
        oled.text(f"Level: {current_level}", 30, 35, 1)
    
    elif game_state == "playing":
        oled.text("YOUR TURN!", 30, 10, 1)
        oled.text(f"Level: {current_level}", 30, 25, 1)
        oled.text(f"Score: {score}", 35, 35, 1)
        oled.text(f"Lives: {lives}", 35, 45, 1)
        oled.text(f"{len(player_input)}/{len(sequence)}", 40, 55, 1)
    
    elif game_state == "game_over":
        oled.text("GAME OVER!", 25, 15, 1)
        oled.text(f"Score: {score}", 35, 30, 1)
        oled.text(f"Level: {current_level}", 30, 40, 1)
        oled.text("Press A: Retry", 15, 55, 1)
    
    oled.show()

def flash_led(led_index, duration=0.3):
    """Flash specific LED and play its tone"""
    pixels.fill((0, 0, 0))
    pixels[led_index] = LED_COLORS[led_index]
    pixels.show()
    simpleio.tone(buzzer_pin, TONES[led_index], duration)
    
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(0.1)

def play_sequence(difficulty):
    """Play the sequence for player to watch"""
    global game_state, selected_led
    game_state = "watching"
    update_display()
    
    time.sleep(1)  # Pause before starting
    
    speed = get_playback_speed(difficulty)
    
    for led_index in sequence:
        flash_led(led_index, speed * 0.7)
        time.sleep(speed * 0.3)
    
    game_state = "playing"
    selected_led = 0  # Reset to first LED
    # Show first LED as selected
    pixels.fill((0, 0, 0))
    pixels[selected_led] = (50, 50, 50)  # Dim white
    pixels.show()
    update_display()

def add_to_sequence():
    """Add random LED to sequence"""
    sequence.append(random.randint(0, 4))

def check_input(led_index):
    """Check if player input is correct"""
    global score, lives, current_level, game_state, player_input
    
    player_input.append(led_index)
    
    # Check if input matches sequence so far
    if player_input[-1] != sequence[len(player_input) - 1]:
        # Wrong input!
        lives -= 1
        play_error_sound()
        
        if lives <= 0:
            # Game over
            game_over()
        else:
            # Lose life but continue
            print(f"Wrong! Lives remaining: {lives}")
            player_input.clear()
            time.sleep(1)
            difficulty, _ = read_difficulty()
            play_sequence(difficulty)
    
    else:
        # Correct input
        flash_led(led_index, 0.2)
        
        # Check if sequence complete
        if len(player_input) == len(sequence):
            # Level complete!
            score += current_level * 10
            current_level += 1
            player_input.clear()
            
            play_success_sound()
            time.sleep(0.5)
            
            # Add new LED to sequence
            add_to_sequence()
            
            # Play next sequence
            difficulty, _ = read_difficulty()
            play_sequence(difficulty)
        else:
            # Still more inputs needed, show current selected LED
            pixels.fill((0, 0, 0))
            pixels[selected_led] = (50, 50, 50)  # Dim white
            pixels.show()
    
    update_display()

def play_success_sound():
    """Play level complete sound"""
    simpleio.tone(buzzer_pin, 523, 0.1)
    time.sleep(0.05)
    simpleio.tone(buzzer_pin, 659, 0.1)
    time.sleep(0.05)
    simpleio.tone(buzzer_pin, 784, 0.15)

def play_error_sound():
    """Play error sound"""
    simpleio.tone(buzzer_pin, 200, 0.3)

def play_game_over_sound():
    """Play game over sound"""
    for _ in range(3):
        simpleio.tone(buzzer_pin, 300, 0.1)
        time.sleep(0.1)
        simpleio.tone(buzzer_pin, 200, 0.1)
        time.sleep(0.1)

def start_game():
    """Start new game"""
    global game_state, sequence, player_input, current_level, score, lives
    
    game_state = "playing"
    sequence = []
    player_input = []
    current_level = 1
    score = 0
    lives = 3
    
    # Start with one random LED
    add_to_sequence()
    
    # Play first sequence
    difficulty, _ = read_difficulty()
    play_sequence(difficulty)

def game_over():
    """Handle game over"""
    global game_state, high_score
    
    game_state = "game_over"
    
    # Update high score
    if score > high_score:
        high_score = score
        print(f"New high score: {high_score}!")
    
    play_game_over_sound()
    update_display()
    
    # Flash all LEDs red
    for _ in range(3):
        pixels.fill((255, 0, 0))
        pixels.show()
        time.sleep(0.2)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.2)

def select_led_from_buttons():
    """Determine which LED player is selecting (simplified: A=LED 0-2, B=LED 3-4)"""
    # In a full version, you'd use gestures or more buttons
    # Here we simplify: A cycles through 0-2, B cycles through 3-4
    pass

print("Simon Says Memory Game")
print("Button A: Select/Start")
print("Button B: Select")
print("Potentiometer: Difficulty")

update_display()

# LED selection system (simplified)
selected_led = 0
selection_timer = 0

while True:
    current_time = time.monotonic()
    
    # Menu state
    if game_state == "menu":
        # Button A: Start game
        if not button_A.value and last_button_A:
            start_game()
            time.sleep(0.2)
        last_button_A = button_A.value
        
        # Update display when pot moves
        update_display()
    
    # Game over state
    elif game_state == "game_over":
        # Button A: Restart
        if not button_A.value and last_button_A:
            game_state = "menu"
            update_display()
            time.sleep(0.2)
        last_button_A = button_A.value
    
    # Playing state - player input
    elif game_state == "playing":
        # Button A: Cycle through LEDs 0-4
        if not button_A.value and last_button_A:
            selected_led = (selected_led + 1) % 5
            # Show selection
            pixels.fill((0, 0, 0))
            pixels[selected_led] = (50, 50, 50)  # Dim white
            pixels.show()
            time.sleep(0.1)
        last_button_A = button_A.value
        
        # Button B: Confirm selection
        if not button_B.value and last_button_B:
            check_input(selected_led)
            time.sleep(0.2)
        last_button_B = button_B.value
    
    time.sleep(0.05)
