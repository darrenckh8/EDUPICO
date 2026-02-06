% Read MP3 file
[audio_data, Fs] = audioread('sample-15s.mp3');  % audio_data is the sound data, Fs is the sampling rate

% Select a portion of the audio for clarity (first 2 seconds)
T = 15;  % Duration to plot (in seconds)
t = 0:1/Fs:T-1/Fs;  % Time vector for the first 2 seconds
audio_segment = audio_data(1:length(t), :);  % Extract the first part of the audio data

% If stereo, take only one channel (mono)
if size(audio_segment, 2) > 1
    audio_segment = audio_segment(:, 1);  % Use only the left channel
end

% Plotting the waveform
figure;
plot(t, audio_segment, 'b', 'LineWidth', 1.5);
title('Audio Waveform from MP3 (Speaker Representation)');
xlabel('Time (s)');
ylabel('Amplitude');
grid on;
xlim([0 T]);  % Limit x-axis to the first 2 seconds
