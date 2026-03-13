import numpy as np
import wave

# V12 Omega Audio Spec
SAMPLE_RATE = 44100
DURATION = 3.0  # Seconds of audio
num_samples = int(SAMPLE_RATE * DURATION)

def sonify_substrate(c_real, c_imag, filename="mandel_tension.wav"):
    c = complex(c_real, c_imag)
    z = 0 + 0j
    T_sys = 0.0
    decay = 0.1
    audio = []

    print(f"Auditing Substrate at Coordinate: {c}")

    for _ in range(num_samples):
        # 1. Iterate the Substrate
        z = z**2 + c
        
        # 2. V12 Logic: Mass is the magnitude (Distance from Zero)
        mass = np.abs(z)
        T_sys = (T_sys + mass) * (1 - decay)
        
        # 3. Sonification: Map i to the Sine wave
        # Imaginary part creates the 'Timbre'
        wave_val = np.sin(np.real(z) + np.imag(z))
        audio.append(wave_val)

        # 4. Resilience Check: If it escapes, it's a 'Fracture'
        if mass > 2:
            z = 0 + 0j # Reset the substrate (Recursive Loop)
            T_sys = 0 # Tension resets on collapse

    # Normalize and save to .wav
    audio = np.array(audio)
    audio = (audio / (np.max(np.abs(audio)) + 1e-6) * 32767).astype(np.int16)

    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(audio.tobytes())
    
    print(f"SUCCESS: {filename} generated.")

# AUDIT 1: The "Seahorse Valley" (High Metastability / Musical)
sonify_substrate(-0.75, 0.1, "seahorse_tension.wav")

# AUDIT 2: The "Deep Black" (Stable / Low Tension)
sonify_substrate(0.1, 0.1, "stable_core.wav")
