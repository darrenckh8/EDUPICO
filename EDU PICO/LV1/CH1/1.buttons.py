import board
import digitalio
import time

button_A = digitalio.DigitalInOut(board.GP0)
button_B = digitalio.DigitalInOut(board.GP1)

button_A.direction = digitalio.Direction.INPUT
button_B.direction = digitalio.Direction.INPUT

button_A.pull = digitalio.Pull.UP
button_B.pull = digitalio.Pull.UP

button_A_count = 0
button_B_count = 0

button_A_previous = True
button_B_previous = True

print("Button Counter Program Started!")
print("Press buttons to count. Hold both buttons for 2 seconds to see totals.")

while True:
    button_A_current = button_A.value
    button_B_current = button_B.value

    if button_A_previous and not button_A_current:
        button_A_count += 1
        print(f"Button A pressed! Count: {button_A_count}")

    if button_B_previous and not button_B_current:
        button_B_count += 1
        print(f"Button B pressed! Count: {button_B_count}")

    if not button_A_current and not button_B_current:
        print("Both buttons held - showing totals in 2 seconds...")
        time.sleep(2)
        if not button_A.value and not button_B.value:
            print(f"=== TOTALS ===")
            print(f"Button A total presses: {button_A_count}")
            print(f"Button B total presses: {button_B_count}")
            print(f"Combined total: {button_A_count + button_B_count}")
            print("==============")
            time.sleep(1)

    button_A_previous = button_A_current
    button_B_previous = button_B_current

    time.sleep(0.05)
