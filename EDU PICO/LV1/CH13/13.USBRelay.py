import board  # Helps us refer to the correct pins on the board.                    #type: ignore
import digitalio  # Helps us control the digital pins on the board.                 #type: ignore

# Create a digital pin object called relay.
relay = digitalio.DigitalInOut(board.GP22)
# Set the direction of the pin to OUTPUT.
relay.direction = digitalio.Direction.OUTPUT

while True:  # Create an infinite loop.
    # Ask the user to input a value.
    user_input = input("1:ON,0:OFF \nYour choice:")
    state = int(user_input)  # Convert the input to an integer.
    
    if state == 0:  # Check if the input is 0.
        print("Relay OFF")  # Print the message "OFF".
        relay.value = False  # Turn the relay OFF.
    
    elif state == 1:  # Check if the input is 1.
        print("Relay ON")  # Print the message "ON".
        relay.value = True  # Turn the relay ON.
    
    else:  # If the input is neither 0 nor 1.
        # Print an error message.
        print("Invalid input, Please enter 0 for OFF or 1 for ON.")
