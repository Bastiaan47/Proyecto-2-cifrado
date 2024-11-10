import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
from scipy.fftpack import fft
from tkinter import Tk, filedialog, Button, Label
from Crypto.Cipher import AES
import os

# Configuraciones de grabación
DURACION = 2
FRECUENCIA_MUESTREO = 44100
TOLERANCIA = 500  # Tolerancia incrementada para las diferencias de valores en la matriz

# Número de reintentos y capturas promedio
NUM_REINTENTOS = 3

def capturar_voz(nombre_archivo="voz.wav"):
    print("Iniciando grabación... Hable ahora.")
    voz = sd.rec(int(DURACION * FRECUENCIA_MUESTREO), samplerate=FRECUENCIA_MUESTREO, channels=1, dtype='float64')
    sd.wait()
    print(f"Grabación completada. Archivo guardado como {nombre_archivo}.")
    voz_int16 = np.int16(voz / np.max(np.abs(voz)) * 32767)
    wavfile.write(nombre_archivo, FRECUENCIA_MUESTREO, voz_int16)
    return voz.flatten()

def procesar_fft(voz):
    print("Procesando la FFT de la señal de voz...")
    coeficientes_fft = fft(voz)
    magnitudes = np.abs(coeficientes_fft[:len(coeficientes_fft) // 2])
    coeficientes_normalizados = magnitudes / np.max(magnitudes)
    coeficientes_int = np.int32(coeficientes_normalizados * 100000)
    print("FFT procesada y coeficientes obtenidos.")
    return coeficientes_int

def generar_matriz_key(coeficientes, N=16):
    print("Generando matriz clave a partir de los coeficientes FFT...")
    if len(coeficientes) < N:
        raise ValueError("No hay suficientes coeficientes para generar la matriz clave.")
    matriz_key = coeficientes[:N]
    matriz_key = np.resize(matriz_key, (4, 4)).astype(np.uint8)
    print("Matriz clave generada:", matriz_key)
    return matriz_key

def matriz_a_bytes(matriz):
    return matriz.flatten().tobytes()

def cifrar_aes(datos, matriz_key):
    print("Cifrando datos con la clave generada...")
    clave = matriz_a_bytes(matriz_key)
    cipher = AES.new(clave, AES.MODE_CBC)
    iv = cipher.iv
    padding_length = AES.block_size - (len(datos) % AES.block_size)
    datos_padded = datos + bytes([padding_length]) * padding_length
    cifrado = cipher.encrypt(datos_padded)
    print("Datos cifrados correctamente.")
    return cifrado, iv

def descifrar_aes(datos_cifrados, matriz_key, iv):
    print("Intentando descifrar datos...")
    clave = matriz_a_bytes(matriz_key)
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    datos_descifrados = cipher.decrypt(datos_cifrados)
    padding_length = datos_descifrados[-1]
    if padding_length < 1 or padding_length > AES.block_size:
        raise ValueError("Padding inválido en el archivo descifrado.")
    print("Datos descifrados correctamente.")
    return datos_descifrados[:-padding_length]

def comparar_matrices(matriz1, matriz2, tolerancia=TOLERANCIA):
    print("Comparando matrices clave...")
    diferencias = np.abs(matriz1 - matriz2)
    if np.all(diferencias <= tolerancia):
        print("Las matrices son similares dentro de la tolerancia establecida.")
        return True
    else:
        print("Las matrices no son suficientemente similares.")
        return False

def intentar_generar_matriz_key():
    print("Intentando generar matriz clave con múltiples intentos...")
    for intento in range(NUM_REINTENTOS):
        print(f"Intento {intento + 1} de {NUM_REINTENTOS}")
        voz = capturar_voz(f"voz_intento_{intento}.wav")
        coeficientes_int = procesar_fft(voz)
        matriz_key = generar_matriz_key(coeficientes_int)
        yield matriz_key
    print("Finalizados los intentos de generación de matriz clave.")

def cifrar_archivo():
    archivo = filedialog.askopenfilename(title="Selecciona un archivo para cifrar")
    if not archivo:
        print("No se seleccionó ningún archivo.")
        return

    with open(archivo, "rb") as f:
        datos_a_cifrar = f.read()
    print(f"Archivo {archivo} leído para cifrado.")

    voz = capturar_voz("voz_para_cifrado.wav")
    coeficientes_int = procesar_fft(voz)
    matriz_key_cifrado = generar_matriz_key(coeficientes_int)

    np.save("clave.npy", matriz_key_cifrado)
    print("Matriz clave de cifrado guardada como 'clave.npy'.")

    cifrado, iv = cifrar_aes(datos_a_cifrar, matriz_key_cifrado)

    archivo_cifrado = archivo + ".cifrado"
    with open(archivo_cifrado, "wb") as f:
        f.write(iv + cifrado)
    print(f"Archivo cifrado guardado como '{archivo_cifrado}'.")

def descifrar_archivo():
    archivo_cifrado = filedialog.askopenfilename(title="Selecciona un archivo para descifrar", filetypes=[("Archivos cifrados", "*.cifrado")])
    if not archivo_cifrado:
        print("No se seleccionó ningún archivo.")
        return

    matriz_key_cifrado = np.load("clave.npy")
    print("Matriz clave cargada desde 'clave.npy'.")

    with open(archivo_cifrado, "rb") as f:
        iv = f.read(16)
        datos_cifrados = f.read()
    print(f"Archivo cifrado {archivo_cifrado} leído para descifrado.")

    for matriz_key_descifrado in intentar_generar_matriz_key():
        if comparar_matrices(matriz_key_cifrado, matriz_key_descifrado):
            try:
                datos_descifrados = descifrar_aes(datos_cifrados, matriz_key_descifrado, iv)
                archivo_original = archivo_cifrado.replace(".cifrado", "_descifrado")
                with open(archivo_original, "wb") as f:
                    f.write(datos_descifrados)
                print(f"Archivo descifrado guardado como '{archivo_original}'")
                return
            except ValueError as e:
                print("Error durante el descifrado:", e)
                continue

    print("No se pudo descifrar el archivo con las claves generadas.")

# Interfaz gráfica
root = Tk()
root.title("Cifrado y Descifrado de Archivos con Matriz Clave")
root.geometry("400x200")

Label(root, text="Cifrado y Descifrado de Archivos con Matriz Clave").pack(pady=10)

Button(root, text="Cifrar archivo", command=cifrar_archivo).pack(pady=10)
Button(root, text="Descifrar archivo", command=descifrar_archivo).pack(pady=10)

root.mainloop()
