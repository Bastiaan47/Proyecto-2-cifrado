import tkinter as tk
from tkinter import filedialog, messagebox
import os
import numpy as np
from audio import grabar_audio, calcular_huella_espectral, transcribir_audio_en_memoria, comparar_huellas
from encriptar import doble_encriptacion_hill_aes, desencriptar_archivo, texto_a_matriz_numerica

archivo_a_cifrar = None
huella_original = None
matriz_original = None

def seleccionar_archivo():
    global archivo_a_cifrar
    archivo_a_cifrar = filedialog.askopenfilename(title="Seleccionar archivo")
    if archivo_a_cifrar:
        lbl_archivo.config(text=f"Archivo seleccionado: {os.path.basename(archivo_a_cifrar)}")

def grabar_clave_encriptado():
    audio = grabar_audio(guardar_como="clave_encriptado.wav")
    if audio is not None:
        global huella_original, matriz_original
        huella_original = calcular_huella_espectral(audio)
        texto = transcribir_audio_en_memoria("clave_encriptado.wav")
        matriz_original = texto_a_matriz_numerica(texto) if texto else None
        messagebox.showinfo("Éxito", "Clave de encriptado grabada correctamente.")

def grabar_clave_desencriptado():
    audio = grabar_audio(guardar_como="clave_desencriptado.wav")
    if audio is not None:
        huella_descifrado = calcular_huella_espectral(audio)
        if comparar_huellas(huella_original, huella_descifrado):
            texto = transcribir_audio_en_memoria("clave_desencriptado.wav")
            matriz_descifrado = texto_a_matriz_numerica(texto) if texto else None
            desencriptar_archivo("archivo_cifrado.aes", matriz_descifrado, np.array([[3, 3], [2, 5]]), "archivo_descifrado.txt")
        else:
            messagebox.showerror("Error", "Las huellas de las claves no coinciden.")

def encriptar():
    if archivo_a_cifrar and matriz_original is not None:
        hill_key_matrix = np.array([[3, 3], [2, 5]])
        doble_encriptacion_hill_aes(archivo_a_cifrar, hill_key_matrix, matriz_original, "archivo_cifrado.aes")
    else:
        messagebox.showerror("Error", "Selecciona un archivo y graba la clave para encriptar.")

# Interfaz gráfica
root = tk.Tk()
root.title("Encriptador de Archivos con Audio")
root.geometry("500x400")
root.config(bg="#f0f0f0")

frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=20)

def estilo_boton():
    return {
        "bg": "#4CAF50",
        "fg": "white",
        "font": ("Helvetica", 12),
        "relief": "raised",
        "borderwidth": 3,
        "width": 25,
        "height": 2,
        "activebackground": "#45a049",
        "activeforeground": "white",
        "highlightcolor": "#000",
        "highlightthickness": 1
    }

btn_seleccionar_archivo = tk.Button(frame, text="Seleccionar archivo", command=seleccionar_archivo, **estilo_boton())
btn_seleccionar_archivo.grid(row=0, column=0, pady=10)

lbl_archivo = tk.Label(frame, text="Archivo seleccionado: Ninguno", bg="#f0f0f0", font=("Helvetica", 10))
lbl_archivo.grid(row=1, column=0, pady=5)

btn_grabar_clave_encriptado = tk.Button(frame, text="Grabar clave para encriptar", command=grabar_clave_encriptado, **estilo_boton())
btn_grabar_clave_encriptado.grid(row=2, column=0, pady=10)

btn_grabar_clave_desencriptado = tk.Button(frame, text="Grabar clave para desencriptar", command=grabar_clave_desencriptado, **estilo_boton())
btn_grabar_clave_desencriptado.grid(row=3, column=0, pady=10)

btn_encriptar = tk.Button(frame, text="Encriptar archivo", command=encriptar, **estilo_boton())
btn_encriptar.grid(row=4, column=0, pady=10)

root.mainloop()
