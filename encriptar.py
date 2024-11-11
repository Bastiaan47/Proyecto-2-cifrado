import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
from scipy.linalg import inv

def texto_a_matriz_numerica(texto):
    try:
        matriz = np.array([[ord(char) for char in line] for line in texto.splitlines()])
        return matriz
    except Exception as e:
        print(f"Error al convertir el texto a matriz numérica: {e}")
        return None

def matriz_a_clave(matriz):
    clave_bytes = matriz.flatten().astype(np.uint8).tobytes()
    clave_bytes = (clave_bytes * (32 // len(clave_bytes) + 1))[:32]
    return clave_bytes

def inversa_modular_matriz(matriz, mod=256):
    determinante = int(round(np.linalg.det(matriz)))
    determinante_inv = pow(determinante, -1, mod)
    matriz_inversa = determinante_inv * np.round(determinante * np.linalg.inv(matriz)).astype(int) % mod
    return matriz_inversa

def hill_cipher_encrypt(data, key_matrix):
    data_bytes = [ord(char) for char in data]
    while len(data_bytes) % 2 != 0:
        data_bytes.append(ord(' '))
    data_matrix = np.array(data_bytes).reshape(-1, 2)
    cipher_matrix = np.dot(data_matrix, key_matrix) % 256
    return ''.join([chr(num) for num in cipher_matrix.flatten()])

def hill_cipher_decrypt(data, key_matrix_inv):
    data_bytes = [ord(char) for char in data]
    data_matrix = np.array(data_bytes).reshape(-1, 2)
    decrypted_matrix = np.dot(data_matrix, key_matrix_inv) % 256
    return ''.join([chr(num) for num in decrypted_matrix.flatten()])

def doble_encriptacion_hill_aes(nombre_archivo, hill_key_matrix, matriz_clave, archivo_salida):
    try:
        with open(nombre_archivo, 'r') as f:
            datos_texto = f.read()
        texto_hill_cifrado = hill_cipher_encrypt(datos_texto.strip(), hill_key_matrix)
        clave_aes = matriz_a_clave(matriz_clave)
        cipher = AES.new(clave_aes, AES.MODE_CBC)
        iv = cipher.iv
        datos_cifrados = cipher.encrypt(pad(texto_hill_cifrado.encode(), AES.block_size))
        with open(archivo_salida, 'wb') as f:
            f.write(iv + datos_cifrados)
        print(f"Archivo cifrado en: {archivo_salida}")
    except Exception as e:
        print(f"No se pudo realizar la doble encriptación: {e}")

def desencriptar_archivo(nombre_archivo_cifrado, matriz_clave_descifrado, hill_key_matrix, archivo_salida):
    try:
        with open(nombre_archivo_cifrado, 'rb') as f:
            contenido = f.read()
        iv = contenido[:16]
        datos_cifrados = contenido[16:]
        clave_descifrado = matriz_a_clave(matriz_clave_descifrado)
        cipher = AES.new(clave_descifrado, AES.MODE_CBC, iv)
        datos_descifrados_aes = unpad(cipher.decrypt(datos_cifrados), AES.block_size)
        hill_key_matrix_inv = inversa_modular_matriz(hill_key_matrix)
        texto_descifrado_hill = hill_cipher_decrypt(datos_descifrados_aes.decode(), hill_key_matrix_inv)
        with open(archivo_salida, 'w') as f:
            f.write(texto_descifrado_hill)
        print(f"Archivo descifrado guardado en {archivo_salida}")
    except Exception as e:
        print(f"Error al descifrar el archivo: {e}")
