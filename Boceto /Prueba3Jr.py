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

# Umbral de tolerancia para la comparación de claves
UMBRAL_SIMILITUD = 10  # Se puede ajustar este valor

def grabar_voz():
    print("Grabando...")
    grabacion = sd.rec(int(DURACION * FRECUENCIA_MUESTREO), samplerate=FRECUENCIA_MUESTREO, channels=1)
    sd.wait()
    grabacion = grabacion.flatten()
    return grabacion

def extraer_frecuencias(grabacion):
    transformada = np.abs(fft(grabacion))[:len(grabacion) // 2]
    return np.argsort(transformada)[-16:]

def generar_clave_desde_voz():
    grabacion = grabar_voz()
    frecuencias = extraer_frecuencias(grabacion)
    clave_voz = np.array(frecuencias[:16], dtype=np.uint8).reshape((4, 4))
    print("Clave generada desde la voz:")
    print(clave_voz)
    return clave_voz

def matriz_a_bytes(matriz):
    return matriz.flatten().tobytes()

def cifrar_aes(datos, matriz_key):
    clave = matriz_a_bytes(matriz_key)
    cipher = AES.new(clave, AES.MODE_CBC)
    iv = cipher.iv
    # Agregar padding manual
    padding_length = AES.block_size - (len(datos) % AES.block_size)
    datos_padded = datos + bytes([padding_length]) * padding_length
    cifrado = cipher.encrypt(datos_padded)
    print("Clave de cifrado (bytes):", clave)
    print("IV usado para cifrar:", iv)
    return cifrado, iv

def descifrar_aes(datos_cifrados, matriz_key, iv):
    clave = matriz_a_bytes(matriz_key)
    print("Clave de descifrado (bytes):", clave)
    print("IV usado para descifrar:", iv)
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    datos_descifrados = cipher.decrypt(datos_cifrados)

    # Remover padding
    padding_length = datos_descifrados[-1]

    # Verificar si el padding es válido
    if padding_length < 1 or padding_length > AES.block_size:
        raise ValueError("Padding inválido en el archivo descifrado.")

    # Eliminar padding
    return datos_descifrados[:-padding_length]

# Función para comparar similitud entre claves
def comparar_claves(clave1, clave2):
    # Convertimos las claves en vectores de una dimensión para comparar la similitud
    clave1_flat = clave1.flatten()
    clave2_flat = clave2.flatten()
    
    # Calculamos la distancia euclidiana
    distancia = np.linalg.norm(clave1_flat - clave2_flat)
    
    print(f"Distancia euclidiana entre las claves: {distancia}")
    
    # Si la distancia es menor que el umbral, las claves son consideradas suficientemente similares
    return distancia < UMBRAL_SIMILITUD

def cifrar_archivo():
    archivo = filedialog.askopenfilename(title="Selecciona un archivo para cifrar")
    if not archivo:
        return None

    with open(archivo, "rb") as f:
        datos_a_cifrar = f.read()

    # Generamos la clave para cifrar (mediante la voz)
    matriz_key_cifrado = generar_clave_desde_voz()  # Esta clave se genera aquí
    cifrado, iv = cifrar_aes(datos_a_cifrar, matriz_key_cifrado)

    archivo_cifrado = archivo + ".cifrado"
    with open(archivo_cifrado, "wb") as f:
        f.write(iv + cifrado)

    print(f"Archivo cifrado guardado como '{archivo_cifrado}'")

    return matriz_key_cifrado  # Devolvemos la clave para usarla luego en el descifrado

def descifrar_archivo(matriz_key_cifrado):
    archivo_cifrado = filedialog.askopenfilename(title="Selecciona un archivo para descifrar", filetypes=[("Archivos cifrados", "*.cifrado")])
    if not archivo_cifrado:
        return

    # Generamos la clave para descifrar (mediante la voz)
    matriz_key_descifrado = generar_clave_desde_voz()

    with open(archivo_cifrado, "rb") as f:
        iv = f.read(16)  # Lee el IV (primer bloque de 16 bytes)
        datos_cifrados = f.read()  # Lee el resto de los datos cifrados

    # Usamos la clave generada para descifrar
    try:
        # Comparar las claves
        if comparar_claves(matriz_key_descifrado, matriz_key_cifrado):  # Comparación entre claves generadas
            datos_descifrados = descifrar_aes(datos_cifrados, matriz_key_descifrado, iv)
            archivo_original = archivo_cifrado.replace(".cifrado", "_descifrado" + os.path.splitext(archivo_cifrado)[1])
            with open(archivo_original, "wb") as f:
                f.write(datos_descifrados)
            print(f"Archivo descifrado guardado como '{archivo_original}'")
        else:
            print("Las claves no coinciden. No se puede descifrar el archivo.")
    except ValueError as e:
        print(f"Error durante el descifrado: {e}")

# Interfaz gráfica
root = Tk()
root.title("Cifrado y Descifrado de Archivos con Clave de Voz")
root.geometry("400x200")

Label(root, text="Cifrado y Descifrado de Archivos con Clave de Voz").pack(pady=10)

# Ahora ciframos el archivo y obtenemos la clave generada
matriz_key_cifrado = cifrar_archivo()

Button(root, text="Descifrar archivo", command=lambda: descifrar_archivo(matriz_key_cifrado)).pack(pady=10)

root.mainloop()
