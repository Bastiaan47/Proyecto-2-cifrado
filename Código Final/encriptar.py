import numpy as np
from Crypto.Cipher import AES                #se importa  el modulo de cifrado AES
from Crypto.Util.Padding import pad, unpad   #funcines para agregar y eliminar relleno de datos
import os
from scipy.linalg import inv

#[Funcion para transformar el texto a matriz numerica]
def texto_a_matriz(texto):
    try:
        matriz= np.array([[ord(char) for char in line] for line in texto.splitlines()]) #divide el texto en lineas y convierte cada caracter en su valor ASCII, para convertir las listas en matriz
        return matriz
    except Exception as e:
        print(f"!Error al convertir el texto a matriz numérica!: {e}")
        return None

#[Funcion para convertir la matriz en una clave]
def matriz_a_clave(matriz):
    clave_bytes= matriz.flatten().astype(np.uint8).tobytes()        #convierte la matriz en un arreglo unidimencional y convierte el arreglo  en bytes de 8bits
    clave_bytes= (clave_bytes * (32//len(clave_bytes)+1))[:32]  #duplica los bytes para asegurar que la clave sea de 32 bytes para luego recortarla a 32 si es que excede
    return clave_bytes

#[Funcion para calcular la inversa modular de la matriz]
def inversa_modular_matriz(matriz, mod=256):
    determinante = int(round(np.linalg.det(matriz)))  #calcular el determinante de la matriz
    determinante_inv = pow(determinante, -1, mod)     #calcular el inverso modular del determinante
    matriz_inversa = determinante_inv * np.round(determinante * np.linalg.inv(matriz)).astype(int) % mod #multiplica la inversa por el inverso del determinante para obtener la matriz inversa modular; Tambien calcula la inversa de la matriz 
    return matriz_inversa

#[Funcion para realizar el Cifrado Cipher Hill]
def encriptar_Cipher_Hill(data, key_matrix):
    data_bytes= np.frombuffer(data, dtype=np.uint8)  #conversion data a bytes

    while len(data_bytes) % 2 != 0: #rellena con un espacio si la longitud no es par
        data_bytes= np.append(data_bytes, ord(' ')) 

    data_matrix= data_bytes.reshape(-1, 2)                 #reorganiza los datos en una matriz de 2 columnas 
    cipher_matrix= np.dot(data_matrix, key_matrix) % 256   #multiplica la matriz de datos por la matriz clave y aplica el modulo 256
    return cipher_matrix.astype(np.uint8).tobytes()        #convierte la matriz cifrada devuelta a bytes

#[Funcion para desencriptar el cifrado Cipher Hill]
def hill_cipher_decrypt(data, key_matrix_inv):
    data_bytes= np.frombuffer(data, dtype=np.uint8)              #convierte data a un arreglo de unit8
    data_matrix= data_bytes.reshape(-1, 2)                       #reorganiza los datos cifrados en una matriz
    decrypted_matrix= np.dot(data_matrix, key_matrix_inv) % 256  #multiplica la matriz de datos cifrados por la inversa de la clave y aplica el modulo 256
    return decrypted_matrix.astype(np.uint8).tobytes()            #convierte la matriz descifrada devuelta a bytes


#[Funcion para hacer la doble encriptación con AES]
def doble_encriptacion_hill_aes(nombre_archivo, hill_key_matrix, matriz_clave, archivo_salida):
    try:
        with open(nombre_archivo, 'rb') as f: #abre el archivo en binario y lo lee como bytes 
            datos= f.read()

        extension= os.path.splitext(nombre_archivo)[1].encode('utf-8')     #extrae la extencion del archivo
        extension_len= len(extension)                                      #guarda extencion
        texto_hill_cifrado= encriptar_Cipher_Hill(datos, hill_key_matrix)  #cifra usando HILL
        clave_aes= matriz_a_clave(matriz_clave)                            #genera una clave para AES
        cipher= AES.new(clave_aes, AES.MODE_CBC)                           #configura el cifrado AES en modo CBC
        iv= cipher.iv                                                      #extrae el vector de inicializacion generado (necesario para descifrar)
        datos_cifrados= cipher.encrypt(pad(texto_hill_cifrado, AES.block_size)) #aplica padding y cifra lo datos HILL con AES
        with open(archivo_salida, 'wb') as f:  #guarda la extencion, el vector de inicializacion y los datos cifrados en el archivo de salida
            f.write(extension_len.to_bytes(1, 'big'))
            f.write(extension)
            f.write(iv)
            f.write(datos_cifrados)
    except Exception as e:
        print(f"!No se pudo realizar la doble encriptación!: {e}")

#[Funcion para desencriptar archivo]
def desencriptar_archivo(nombre_archivo_cifrado, matriz_clave_descifrado, hill_key_matrix, archivo_salida_base):
    try:
        with open(nombre_archivo_cifrado, 'rb') as f:  #lee la extencion, el vector de inicializacion y los datos cifrados
            extension_len= int.from_bytes(f.read(1), 'big')
            extension= f.read(extension_len).decode('utf-8')
            iv= f.read(16)
            datos_cifrados= f.read()

        clave_descifrado= matriz_a_clave(matriz_clave_descifrado)                              #convierte la matriz de clave de descifrado en una clave de 32bytes 
        cipher= AES.new(clave_descifrado, AES.MODE_CBC, iv)                                    #crea un objeto de cifrado AES en modo CBC usando la clave
        datos_descifrados_aes= unpad(cipher.decrypt(datos_cifrados), AES.block_size)           #desencripta los datos con AES y elimina el padding
        hill_key_matrix_inv= inversa_modular_matriz(hill_key_matrix)                           #calcula la matriz inversa de la clave hill para el descifrado
        texto_descifrado_hill= hill_cipher_decrypt(datos_descifrados_aes, hill_key_matrix_inv) #aplica la funcion de decifrado hill
        archivo_salida= archivo_salida_base + extension                                        #genera el nombrea añadiendo la extensión
        with open(archivo_salida, 'wb') as f:                                                  #escribe el contenido cifrado
            f.write(texto_descifrado_hill)
    except Exception as e:
        print(f"!Error al descifrar el archivo!: {e}")
