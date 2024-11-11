import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from scipy.fft import fft
from scipy.spatial.distance import euclidean
import speech_recognition as sr

def grabar_audio(duration=5, sample_rate=44100, guardar_como=None):
    try:
        print("Grabando...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
        sd.wait()
        print("Grabación completada.")
        audio_data = audio_data.flatten()
        if guardar_como is not None:
            audio_data_16bit = (audio_data * 32767).astype(np.int16)
            wavfile.write(guardar_como, sample_rate, audio_data_16bit)
        return audio_data
    except Exception as e:
        print(f"Error al grabar audio: {e}")
        return None

def calcular_huella_espectral(audio_data):
    fft_data = np.abs(fft(audio_data))
    huella = fft_data[:len(fft_data) // 2]
    huella_normalizada = huella / np.max(huella)
    return huella_normalizada

def comparar_huellas(huella1, huella2, tolerancia=15):
    distancia = euclidean(huella1, huella2)
    print(f"Distancia entre huellas: {distancia}")
    return distancia <= tolerancia

def transcribir_audio_en_memoria(archivo_wav):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(archivo_wav) as source:
            audio = recognizer.record(source)
            texto = recognizer.recognize_google(audio, language='es-ES')
            return texto
    except Exception as e:
        print(f"Error al transcribir el audio: {e}")
        return None
