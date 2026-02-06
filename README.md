# EDUWEL EDU PICO Learning Repository

Welcome to the EDUWEL EDU PICO Learning Repository! This comprehensive educational resource contains structured learning materials for microcontroller programming, electronics, and CircuitPython development using the EDU PICO platform.

## 📚 Repository Structure

### EDU PICO Course Materials
The `EDU PICO` directory contains a structured curriculum for learning microcontroller programming with CircuitPython on the EDU PICO platform.

#### **Level 1 - Fundamentals (CH1-CH16)**
Progressive lessons introducing core sensors, actuators, and programming concepts:

- **CH1**: Buttons - Button counter program with press detection and debouncing
- **CH2**: Potentiometer - Real-time analog input reading with voltage/percentage display and visual bar
- **CH3**: NeoPixel RGB LED - Interactive color mixing using button selection and potentiometer brightness control
- **CH4**: Color Sensor - RGB color detection and identification using APDS9960
- **CH5**: Proximity Sensor - Distance measurement with 5-level LED visual feedback
- **CH6**: Gesture Sensor - Directional gesture tracking (up, down, left, right) with NeoPixel indicators
- **CH7**: Temperature & Humidity Sensor - Environmental monitoring with AHT20 sensor
- **CH8**: PDM Microphone - Sound level detection with clap counter and LED response
- **CH9**: Buzzer - Musical note generation with doorbell sounds and scale playback
- **CH10**: Audio Jack - MP3 player with button-controlled playlist navigation
- **CH11**: Servo Motor - Continuous servo control with potentiometer speed adjustment
- **CH12**: DC Motor - Bidirectional motor control with variable speed using PWM
- **CH13**: USB Relay - Simple on/off relay control via serial input
- **CH14**: OLED Display - Graphics library demonstration with text, shapes, and scrolling animations
- **CH15**: Web Server Part 1 - Access Point mode web server for relay control
- **CH16**: Web Server Part 2 - Station mode web server connecting to existing WiFi networks

#### **Level 2 - Integration Projects (P1-P4)**
Hands-on projects combining multiple sensors and components:

- **P1**: Gesture Password - Multi-factor security system with gesture-based unlock and relay control
- **P2**: MP3 Player - Full-featured audio player with play/pause, skip, and long-press controls
- **P3**: Catch the Ball Game - OLED-based arcade game with potentiometer paddle and scoring system
- **P4**: Smart Fan - DC motor fan with dual control modes (manual potentiometer and preset speeds)

#### **Level 3 - Advanced Applications (P1-P4)**
Complex real-world applications integrating multiple systems:

- **P1**: Environmental Dashboard - Cloud-connected monitoring system with InfluxDB data logging for temperature, humidity, sound, and light
- **P2**: Weather Station - Live weather data display using external API with OLED visualization
- **P3**: Smart Home Control Panel - Web-controlled interface for managing relay, NeoPixels, and DC motor
- **P4**: NeoPixel Light Show - Audio-reactive LED spectrum analyzer using FFT and microphone input

#### **Extra**
- **Simon Says Game** - Memory challenge game with 5 LED colors, buzzer feedback, lives system, and high score tracking

### Running Examples
Each chapter contains ready-to-run Python scripts. Navigate to any chapter directory and run the code using Thonny