import board
import busio
import time
import adafruit_ssd1306

i2c = busio.I2C(board.GP5, board.GP4)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

while True:
    oled.fill(0)
    oled.invert(True)
    oled.text("Hello,world", 40, 20, 1)
    oled.text("How are you?", 40, 35, 1)
    oled.show()
    time.sleep(2)

    oled.fill(0)
    oled.rect(10, 10, 50, 30, 1)
    oled.fill_rect(70, 10, 40, 20, 1)
    oled.hline(0, 50, 128, 1)
    oled.vline(64, 0, 64, 1)
    oled.pixel(120, 60, 1)
    oled.show()
    time.sleep(2)

    oled.fill(0)
    message = "Scrolling Text Demo"
    for x in range(128, -len(message)*8, -2):
        oled.fill(0)
        oled.text(message, x, 30, 1)
        oled.show()
        time.sleep(0.03)

    oled.fill(0)
    for x in range(0, 128, 4):
        oled.fill(0)
        oled.pixel(x, 32, 1)
        oled.show()
        time.sleep(0.05)

    oled.fill(0)
    oled.text("Turning off...", 10, 30, 1)
    oled.show()
    time.sleep(1)
    oled.poweroff()
    time.sleep(1)
    oled.poweron()
    oled.fill(0)
    oled.text("Display On!", 20, 30, 1)
    oled.show()
    time.sleep(2)

    oled.fill(0)
    oled.rect(0, 0, 128, 64, 1)
    oled.text("All features!", 20, 10, 1)
    oled.hline(10, 30, 108, 1)
    oled.fill_rect(54, 40, 20, 10, 1)
    oled.text(":-)", 58, 42, 0)
    oled.show()
    time.sleep(2)

    oled.fill(0)
    oled.invert(False)
    oled.text("Normal mode", 20, 50, 1)
    oled.show()
    time.sleep(1)
    oled.invert(True)
    oled.fill(0)
    oled.text("Inverted mode", 20, 50, 1)
    oled.show()
    time.sleep(1)
    oled.invert(False)

    oled.fill(0)
    oled.text("Partial clear below", 10, 10, 1)
    oled.fill_rect(20, 20, 40, 20, 1)
    oled.show()
    time.sleep(1)
    oled.fill_rect(20, 20, 40, 20, 0)
    oled.show()
    time.sleep(1)

    oled.fill(0)
    oled.text("Bar graph:", 0, 0, 1)
    for i in range(0, 100, 10):
        oled.fill_rect(10 + i, 60 - i//2, 8, i//2, 1)
    oled.show()
    time.sleep(2)
