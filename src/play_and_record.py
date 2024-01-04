import sounddevice as sd
import soundfile as sf
import numpy as np
import pyaudio
from scipy.signal import correlate

def play_and_record(filename, duration, rate=44100, chunksize=1024):
    # Load audio file
    audio_data, _ = sf.read(filename, dtype=np.float32)

    # Initialize PyAudio for recording
    p = pyaudio.PyAudio()
    stream_in = p.open(format=pyaudio.paFloat32,
                       channels=1,
                       rate=rate,
                       input=True,
                       frames_per_buffer=chunksize)

    print("Playing...")
    # Initialize SoundDevice for playback
    sd.play(audio_data, samplerate=rate, blocking=False)

    # Record simultaneously
    print("Recording...")
    frames = []
    for i in range(int(rate / chunksize * duration)):
        data = stream_in.read(chunksize)
        frames.append(data)

    print("Finished playing and recording.")

    # Stop and close the recording stream
    stream_in.stop_stream()
    stream_in.close()

    # Terminate PyAudio
    p.terminate()

    # Process the recorded data as needed
    recorded_data = np.frombuffer(b''.join(frames), dtype=np.float32)
    #
    # print("Recorded data:")
    # print(recorded_data)
    # print()
    #
    # print("\nAudio data:")
    # print(audio_data)
    # print()

    sf.write("recorded.wav", recorded_data, rate)

    audio_data = audio_data.astype(np.float32) / np.max(np.abs(audio_data))
    recorded_data = recorded_data.astype(np.float32) / np.max(np.abs(recorded_data))

    correlation = correlate(recorded_data, audio_data, mode='full')

    print(f"{len(recorded_data)}, {len(audio_data)}, {len(correlation)}")

    # Find the index of the peak in the correlation
    delay_index = np.argmax(correlation)

    print(delay_index)

    # Calculate delay in seconds
    delay_seconds = abs(delay_index - len(correlation) / 2) / rate

    print(f"Delay between speaker and microphone: {delay_seconds} seconds")

# Example usage
play_and_record('song.wav', duration=5)
