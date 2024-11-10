import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
from scipy.fftpack import fft
from tkinter import Tk, filedialog, Button, Label
from Crypto.Cipher import AES
import os

# Configuraciones de grabación
DURACION = 2  # Duración de la grabación en segundos
FRECUENCIA_MUESTREO = 44100  # Frecuencia de muestreo en Hz
TOLERANCIA = 200  # Tolerancia en valor absoluto para comparación de coeficientes de clave

# Generar clave fija para pruebas (4x4 matriz de 8-bit enteros)
def generar_clave_fija():
    clave_fija = np.ones((4, 4), dtype=np.uint8) * 42  # Valor 42 es solo un ejemplo
    print("Usando clave fija para pruebas:")
    print(clave_fija)
    return clave_fija

def matriz_a_bytes(matriz):
    return matriz.flatten().tobytes()

def cifrar_aes(datos, matriz_key):
    clave = matriz_a_bytes(matriz_key)
    cipher = AES.new(clave, AES.MODE_CBC)
    iv = cipher.iv
    padding_length = AES.block_size - (len(datos) % AES.block_size)
    datos_padded = datos + bytes([padding_length]) * padding_length
    cifrado = cipher.encrypt(datos_padded)
    print(f"IV usado para cifrar: {iv}")
    return cifrado, iv

def descifrar_aes(datos_cifrados, matriz_key, iv):
    clave = matriz_a_bytes(matriz_key)
    print(f"IV usado para descifrar: {iv}")
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    datos_descifrados = cipher.decrypt(datos_cifrados)
    padding_length = datos_descifrados[-1]

    # Verificar padding_length antes de eliminarlo
    if padding_length < 1 or padding_length > AES.block_size:
        raise ValueError("Padding inválido en el archivo descifrado.")
    
    return datos_descifrados[:-padding_length]

def cifrar_archivo():
    archivo = filedialog.askopenfilename(title="Selecciona un archivo para cifrar")
    if not archivo:
        return

    with open(archivo, "rb") as f:
        datos_a_cifrar = f.read()

    matriz_key = generar_clave_fija()
    cifrado, iv = cifrar_aes(datos_a_cifrar, matriz_key)

    archivo_cifrado = archivo + ".cifrado"
    with open(archivo_cifrado, "wb") as f:
        f.write(iv + cifrado)

    print(f"Archivo cifrado guardado como '{archivo_cifrado}'")

def descifrar_archivo():
    archivo_cifrado = filedialog.askopenfilename(title="Selecciona un archivo para descifrar", filetypes=[("Archivos cifrados", "*.cifrado")])
    if not archivo_cifrado:
        return

    with open(archivo_cifrado, "rb") as f:
        iv = f.read(16)
        datos_cifrados = f.read()

    matriz_key = generar_clave_fija()
    try:
        datos_descifrados = descifrar_aes(datos_cifrados, matriz_key, iv)
        archivo_original = archivo_cifrado.replace(".cifrado", "_descifrado" + os.path.splitext(archivo_cifrado)[1])
        with open(archivo_original, "wb") as f:
            f.write(datos_descifrados)
        print(f"Archivo descifrado guardado como '{archivo_original}'")
    except ValueError as e:
        print(f"Error durante el descifrado: {e}")

# Interfaz gráfica
root = Tk()
root.title("Cifrado y Descifrado de Archivos con Clave Fija")
root.geometry("400x200")

Label(root, text="Cifrado y Descifrado de Archivos con Clave Fija").pack(pady=10)

Button(root, text="Cifrar archivo", command=cifrar_archivo).pack(pady=10)
Button(root, text="Descifrar archivo", command=descifrar_archivo).pack(pady=10)

root.mainloop()
