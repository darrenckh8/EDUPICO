% Parameters
Fs = 10000;              % Sampling frequency (Hz)
f_signal = 10;           % Sine wave frequency (Hz) - One full cycle in 0.1s
f_pwm = 1000;            % PWM frequency (Hz) - higher frequency for smoother PWM steps
T = 0.1;                 % Total time (seconds) - 0.1s for one sine wave cycle
t = 0:1/Fs:T;            % Time vector

% Analog sine wave (0 to 1)
analog_signal = 0.5 + 0.5 * sin(2*pi*f_signal*t);

% Generate PWM signal
pwm_period = 1/f_pwm;
samples_per_pwm = round(pwm_period * Fs);
pwm_signal = zeros(size(t));

for i = 1:samples_per_pwm:length(t)-samples_per_pwm
    duty = analog_signal(i);  % Duty cycle (0 to 1)
    high_samples = round(duty * samples_per_pwm);
    pwm_signal(i:i+high_samples-1) = 1;
end

% Plotting
figure;
plot(t, analog_signal, 'b', 'LineWidth', 2); hold on;
stairs(t, pwm_signal, 'r', 'LineWidth', 1.5);
title('Full Sine Wave and PWM Signal (One Cycle)');
xlabel('Time (s)');
ylabel('Amplitude');
legend('Analog Sine Wave', 'PWM Signal');
grid on;
ylim([-0.2 1.2]);
