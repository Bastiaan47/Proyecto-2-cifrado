import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
from scipy.fftpack import fft
from tkinter import Tk, filedialog, Button, Label
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os

# Configuraciones de grabación
DURACION = 1
FRECUENCIA_MUESTREO = 44100
TOLERANCIA = 500  # Tolerancia en los valores de la matriz para permitir diferencias

def capturar_voz(nombre_archivo="voz.wav"):
    print("Iniciando grabación... Hable ahora.")
    voz = sd.rec(int(DURACION * FRECUENCIA_MUESTREO), samplerate=FRECUENCIA_MUESTREO, channels=1, dtype='float64')
    sd.wait()
    voz_int16 = np.int16(voz / np.max(np.abs(voz)) * 32767)
    wavfile.write(nombre_archivo, FRECUENCIA_MUESTREO, voz_int16)
    return voz.flatten()

def procesar_fft(voz):
    coeficientes_fft = fft(voz)
    magnitudes = np.abs(coeficientes_fft[:len(coeficientes_fft) // 2])
    coeficientes_normalizados = magnitudes / np.max(magnitudes)
    coeficientes_int = np.int32(coeficientes_normalizados * 100000)
    return coeficientes_int

def generar_matriz_key(coeficientes, N=16):
    if len(coeficientes) < N:
        raise ValueError("No hay suficientes coeficientes para generar la matriz clave.")
    matriz_key = coeficientes[:N]
    matriz_key = np.resize(matriz_key, (4, 4)).astype(np.uint8)
    print("Matriz clave generada:", matriz_key)  # Mostrar la matriz clave generada
    return matriz_key

def matriz_a_bytes(matriz):
    return matriz.flatten().tobytes()

def cifrar_aes(datos, matriz_key):
    clave = matriz_a_bytes(matriz_key)
    cipher = AES.new(clave, AES.MODE_CBC)
    iv = cipher.iv
    padding_length = AES.block_size - (len(datos) % AES.block_size)
    datos_padded = datos + bytes([padding_length]) * padding_length
    cifrado = cipher.encrypt(datos_padded)
    return cifrado, iv

def descifrar_aes(datos_cifrados, matriz_key, iv):
    clave = matriz_a_bytes(matriz_key)
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    datos_descifrados = cipher.decrypt(datos_cifrados)
    try:
        datos_descifrados = unpad(datos_descifrados, AES.block_size)
    except ValueError:
        raise ValueError("Padding inválido en el archivo descifrado.")
    return datos_descifrados

def comparar_matrices(matriz1, matriz2, tolerancia=TOLERANCIA):
    diferencias = np.abs(matriz1 - matriz2)
    print("Diferencias entre matrices:", diferencias)  # Mostrar diferencias entre matrices
    return np.all(diferencias <= tolerancia)

def cifrar_archivo():
    archivo = filedialog.askopenfilename(title="Selecciona un archivo para cifrar")
    if not archivo:
        return

    with open(archivo, "rb") as f:
        datos_a_cifrar = f.read()

    voz = capturar_voz("voz_para_cifrado.wav")
    coeficientes_int = procesar_fft(voz)
    matriz_key_cifrado = generar_matriz_key(coeficientes_int)

    # Guardar la matriz de clave en un archivo
    np.save("clave.npy", matriz_key_cifrado)

    cifrado, iv = cifrar_aes(datos_a_cifrar, matriz_key_cifrado)

    archivo_cifrado = archivo + ".cifrado"
    with open(archivo_cifrado, "wb") as f:
        f.write(iv + cifrado)

    print("Archivo cifrado guardado como:", archivo_cifrado)
    
    #print("Matriz clave de cifrado:", matriz_key_cifrado)  # Mostrar matriz clave usada para cifrar

def descifrar_archivo():
    archivo_cifrado = filedialog.askopenfilename(title="Selecciona un archivo para descifrar", filetypes=[("Archivos cifrados", "*.cifrado")])
    if not archivo_cifrado:
        return

    # Cargar la matriz de clave guardada
    matriz_key_cifrado = np.load("clave.npy")
    #print("Matriz clave de cifrado cargada:", matriz_key_cifrado)  # Mostrar matriz clave cargada

    with open(archivo_cifrado, "rb") as f:
        iv = f.read(16)
        datos_cifrados = f.read()

    voz = capturar_voz("voz_para_descifrar.wav")
    coeficientes_int = procesar_fft(voz)
    matriz_key_descifrado = generar_matriz_key(coeficientes_int)
    print("Matriz clave de descifrado generada:", matriz_key_descifrado)  # Mostrar matriz clave generada para descifrar

    # Comparar matrices con tolerancia
    if not comparar_matrices(matriz_key_cifrado, matriz_key_descifrado):
        print("Las matrices de clave no coinciden dentro de la tolerancia. No se puede descifrar el archivo.")
        return

    try:
        datos_descifrados = descifrar_aes(datos_cifrados, matriz_key_cifrado, iv)
        archivo_original = archivo_cifrado.replace(".cifrado", "_descifrado")
        with open(archivo_original, "wb") as f:
            f.write(datos_descifrados)
        print(f"Archivo descifrado guardado como '{archivo_original}'")
    except ValueError as e:
        print("Error durante el descifrado:", e)

# Interfaz gráfica
root = Tk()
root.title("Cifrado y Descifrado de Archivos con Matriz Clave")
root.geometry("400x200")

Label(root, text="Cifrado y Descifrado de Archivos con Matriz Clave").pack(pady=10)

Button(root, text="Cifrar archivo", command=cifrar_archivo).pack(pady=10)
Button(root, text="Descifrar archivo", command=descifrar_archivo).pack(pady=10)

root.mainloop()
