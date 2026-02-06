import time
import board
from analogio import AnalogIn

potentio = AnalogIn(board.GP28)

reading_count = 0

while True:
    raw_value = potentio.value
    voltage = (raw_value * 3.3) / 65535
    percentage = (raw_value / 65535) * 100

    reading_count += 1

    bar_length = 20
    filled_length = min(bar_length, round((raw_value / 65535) * bar_length))
    bar = "=" * filled_length + "-" * (bar_length - filled_length)

    if reading_count % 1 == 0:
        print(f"\nPOTENTIOMETER STATISTICS (Reading #{reading_count})")
        print(f"Current Voltage: {voltage:.3f}V ({percentage:.1f}%)")
        print(f"Visual Bar: [{bar}] {voltage:.2f}V")
        print(f"Raw ADC Value:   {raw_value}/65535")
        print("-" * 50)

    time.sleep(0.1)
