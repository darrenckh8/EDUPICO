% Parameters
Fs = 10000;             % Sampling frequency (Hz)
f_signal = 440;         % Frequency of sound (Hz) - A4 note (440 Hz)
T = 0.05;               % Time duration (seconds) for one cycle of tone
t = 0:1/Fs:T;           % Time vector

% Buzzer - Square Wave (for buzzer tone)
buzzer_wave = square(2*pi*f_signal*t); % Square wave (on/off)

% Speaker - Sine Wave (for speaker tone)
speaker_wave = sin(2*pi*f_signal*t);   % Sine wave (smooth tone)

% Plotting
figure;

% Plot Buzzer Wave (Square Wave)
subplot(2,1,1);
plot(t, buzzer_wave, 'r', 'LineWidth', 2);
title('Buzzer Wave - Square Wave (440 Hz)');
xlabel('Time (s)');
ylabel('Amplitude');
grid on;
ylim([-1.2 1.2]);

% Plot Speaker Wave (Sine Wave)
subplot(2,1,2);
plot(t, speaker_wave, 'b', 'LineWidth', 2);
title('Speaker Wave - Sine Wave (440 Hz)');
xlabel('Time (s)');
ylabel('Amplitude');
grid on;
ylim([-1.2 1.2]);
