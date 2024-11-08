import tkinter as tk
from tkinter import filedialog, messagebox
import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
from scipy.signal import medfilt
from hashlib import sha256
from Crypto.Cipher import AES
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 1
selected_file = None
mode = None

def preprocess_audio(audio_data):


    audio_data = medfilt(audio_data, kernel_size=3)
    normalized_audio = audio_data / np.max(np.abs(audio_data))
    return normalized_audio

def extract_significant_frequencies(fft_data, num_frequencies=10):
  
    magnitudes = np.abs(fft_data)
    indices = np.argsort(magnitudes)[-num_frequencies:] 
    return indices, magnitudes[indices]

def generate_secure_key(frequencies):
   
    key_string = ''.join(map(str, frequencies))
    secure_key = sha256(key_string.encode()).digest()
    return secure_key[:16] 

def encrypt_file(file_path, key):

    with open(file_path, 'rb') as f:
        plaintext = f.read()
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    with open('archivo_encriptado.enc', 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)
    messagebox.showinfo("Éxito", "Archivo cifrado como archivo_encriptado.enc")

def decrypt_file(encrypted_path, key):

    with open(encrypted_path, 'rb') as f:
        data = f.read()
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    try:
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        original_extension = os.path.splitext(selected_file)[1]
        decrypted_filename = "archivo_desencriptado" + original_extension
        with open(decrypted_filename, 'wb') as f:
            f.write(plaintext)
        messagebox.showinfo("Éxito", f"Archivo descifrado como {decrypted_filename}")
    except ValueError:
        messagebox.showerror("Error", "Clave incorrecta o archivo alterado")

def record_audio_with_plot(filename):
 
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    
    plt.ion()
    fig, ax = plt.subplots()
    x = np.arange(0, CHUNK)
    line, = ax.plot(x, np.random.rand(CHUNK))
    ax.set_ylim(-1, 1)
    ax.set_xlim(0, CHUNK)
    plt.title("Grabación de voz - Onda de audio en vivo")

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        audio_data = np.frombuffer(data, dtype=np.int16)
        processed_data = preprocess_audio(audio_data)
        line.set_ydata(processed_data)
        fig.canvas.draw()
        fig.canvas.flush_events()

    plt.ioff()
    plt.close()

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return np.frombuffer(b''.join(frames), dtype=np.int16)

def process_file():
    """Procesa el archivo cifrando o descifrando según el modo."""
    audio_data = record_audio_with_plot("voz_usuario.wav")
    fft_data = fft(audio_data)
    indices, _ = extract_significant_frequencies(fft_data)
    key = generate_secure_key(indices)

    if mode == 'encriptar':
        encrypt_file(selected_file, key)
    elif mode == 'desencriptar':
        decrypt_file(selected_file, key)

def start_encryption():
    """Configura el modo de encriptación y permite seleccionar el archivo."""
    global mode, selected_file
    mode = 'encriptar'
    selected_file = filedialog.askopenfilename(title="Seleccionar archivo para encriptar")
    if selected_file:
        btn_record.pack(pady=10)

def start_decryption():
    """Configura el modo de desencriptación y permite seleccionar el archivo."""
    global mode, selected_file
    mode = 'desencriptar'
    selected_file = filedialog.askopenfilename(title="Seleccionar archivo para desencriptar")
    if selected_file:
        btn_record.pack(pady=10)


root = tk.Tk()
root.title("Cifrado por Voz con Transformada de Fourier")
root.geometry("400x300")

btn_encrypt = tk.Button(root, text="Seleccionar archivo para Encriptar", command=start_encryption)
btn_encrypt.pack(pady=10)

btn_decrypt = tk.Button(root, text="Seleccionar archivo para Desencriptar", command=start_decryption)
btn_decrypt.pack(pady=10)

btn_record = tk.Button(root, text="Grabar y Procesar", command=process_file)

root.mainloop()

