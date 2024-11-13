import numpy as np
import sounddevice as sd                     #grabar y reproducir audio
from scipy.io import wavfile                 #leer y escribir  ".wav"
from scipy.fft import fft                    #transformada rapida de fourier
from scipy.spatial.distance import euclidean #calcular distancia entre 2 arrays
import speech_recognition as sr              #pasar de audio a texto

#[Funcion para Grabar Audio]
def grabar_audio(duration=5, sample_rate=44100, guardar_como=None):
    try:
        audio_data= sd.rec(int(duration*sample_rate), samplerate=sample_rate, channels=1, dtype='float64') #inicia grabacion de audio
        sd.wait()                                    #pausa cuando la grabacion este completa
        audio_data = audio_data.flatten()            #convierte audio_data en un array unidimensional
        if guardar_como is not None:                                   #asegurarce de que se a pasado un archivo para guardar el audio 
            audio_data_16bit = (audio_data * 32767).astype(np.int16)   #convierte los datos de audio a 16 bits
            wavfile.write(guardar_como, sample_rate, audio_data_16bit) #guarda el archivo en .wav
        return audio_data
    except Exception as e:
        print(f"!ERROR AL GUARDAR AUDIO!: {e}")
        return None
    
#[Funcion para calcular las caracteristicas de las Frecuencias]
def calcular_caract_Frecuencias(audio_data):
    fft_data= np.abs(fft(audio_data))         #aplica Transformada de Fourier para obtenen la magnitud de las freecuencias 
    huella= fft_data[:len(fft_data)//2]       #se toma la mitad de los datos de Fourier (Frec superiores son reflejos de  las inferirores)
    huella_normalizada= huella/np.max(huella) #se normaliza la huella por mel max. valor para que quede en el rango [0, 1]
    return huella_normalizada                 

#[Funcion para saber si las frecuencias son similares]
def comparar_Frecuencias(huella1, huella2, tolerancia=15):
    distancia= euclidean(huella1, huella2)  #calcular distancia euclidiana entre huella 1 y 2
    return distancia <= tolerancia          #si es menor o igual son similares , si no, no

#[Funcion para transcribir el audio a texto en la memoria] 
def transcribir_audio_en_memoria(archivo_wav):
    recognizer=sr.Recognizer()    #crea una insancia para reconocer voz 
    try:
        with sr.AudioFile(archivo_wav) as source: #abre el archivo de audio 
            audio= recognizer.record(source)      #lee el audio completo 
            texto= recognizer.recognize_google(audio, language='es-ES') #usa un API de google para pasar de audio a texto
            return texto
    except Exception as e:
        print(f"!Error al transcribir el audio!: {e}")
        return None