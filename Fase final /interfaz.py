import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  
import threading  
import time
import os
import numpy as np
from audio import grabar_audio, calcular_huella_espectral, transcribir_audio_en_memoria, comparar_huellas
from encriptar import doble_encriptacion_hill_aes, desencriptar_archivo, texto_a_matriz_numerica

archivo_a_cifrar = None
huella_original = None
matriz_original = None
animacion_event = threading.Event()

def seleccionar_archivo():
    global archivo_a_cifrar
    archivo_a_cifrar = filedialog.askopenfilename(title="Seleccionar archivo")
    if archivo_a_cifrar:
        lbl_archivo.config(text=f"Archivo seleccionado: {os.path.basename(archivo_a_cifrar)}")

def mostrar_mensaje(texto):
    lbl_estado.config(text=texto)
    lbl_estado.update()

def grabar_clave_encriptado():
    if archivo_a_cifrar is None:
        mostrar_mensaje("seleccione un archivo para grabar la clave.")
        messagebox.showwarning("Advertencia", "seleccione un archivo antes de grabar la clave de encriptado.")
        return
    
    mostrar_mensaje("grabando clave de encriptado...")
    audio= grabar_audio(guardar_como="clave_encriptado.wav")
    if audio is not None:
        global huella_original, matriz_original
        huella_original= calcular_huella_espectral(audio)
        texto= transcribir_audio_en_memoria("clave_encriptado.wav")
        matriz_original= texto_a_matriz_numerica(texto) if texto else None
        mostrar_mensaje("Clave de encriptado grabada correctamente.")
        messagebox.showinfo("Éxito", "Clave de encriptado grabada correctamente.")

def grabar_clave_desencriptado():
    if archivo_a_cifrar is None:
        mostrar_mensaje("Seleccione un archivo para grabar la clave.")
        messagebox.showwarning("Advertencia", "Seleccione un archivo antes de grabar la clave de desencriptado.")
        return
    mostrar_mensaje("Grabando clave de desencriptado...")
    audio = grabar_audio(guardar_como="clave_desencriptado.wav")
    if audio is not None:
        huella_descifrado= calcular_huella_espectral(audio)
        if comparar_huellas(huella_original, huella_descifrado):
            texto= transcribir_audio_en_memoria("clave_desencriptado.wav")
            matriz_descifrado= texto_a_matriz_numerica(texto) if texto else None    
            if matriz_descifrado is not None and not np.array_equal(matriz_descifrado, matriz_original):
                mostrar_mensaje("Clave de desencriptado incorrecta, vuelva a grabar.")
                messagebox.showerror("Error", "Clave de desencriptado incorrecta, vuelva a grabar.")
                return

            try:
                desencriptar_archivo("archivo_cifrado.aes", matriz_descifrado, np.array([[3, 3], [2, 5]]), "archivo_descifrado.txt")
                mostrar_mensaje("Archivo desencriptado correctamente.")
                messagebox.showinfo("Éxito", "Archivo desencriptado correctamente.")
            
            except Exception as e:
                if "padding" in str(e).lower() or "incorrect" in str(e).lower():
                    mostrar_mensaje("Clave de desencriptado incorrecta, vuelva a grabar.")
                    messagebox.showerror("Error", "Clave de desencriptado incorrecta, vuelva a grabar.")
                else:
                    mostrar_mensaje("Error al descifrar el archivo.")
                    messagebox.showerror("Error", f"Error al descifrar el archivo: {e}")
                return
        else:
            mostrar_mensaje("Clave de desencriptado incorrecta, vuelva a grabar.")
            messagebox.showerror("Error", "Clave de desencriptado incorrecta, vuelva a grabar.")
            
def verificar_preparativos():
    if not archivo_a_cifrar:
        messagebox.showwarning("Advertencia", "Selecciona un archivo antes de continuar.")
        return False
    if matriz_original is None:
        messagebox.showwarning("Advertencia", "Graba una clave de encriptado antes de continuar.")
        return False
    return True

def animacion_progreso():
    for i in range(5):
        mostrar_mensaje("Procesando" + "." * (i % 3 + 1))
        time.sleep(0.5)
    mostrar_mensaje("")

def encriptar():
    if verificar_preparativos():
        mostrar_mensaje("Encriptando archivo...")
        hill_key_matrix = np.array([[3, 3], [2, 5]])
        animacion_event.clear()
        threading.Thread(target=animacion_progreso).start()

        # Llamada al proceso de encriptado en un nuevo hilo
        def proceso_encriptado():
            doble_encriptacion_hill_aes(archivo_a_cifrar, hill_key_matrix, matriz_original, "archivo_cifrado.aes")
            animacion_event.set()  # Finaliza la animación
            mostrar_mensaje("Archivo encriptado correctamente.")
            messagebox.showinfo("Éxito", "Archivo encriptado correctamente.")

        threading.Thread(target=proceso_encriptado).start()

# Interfaz gráfica
root = tk.Tk()
root.title("Sistema de Encriptado con Clave de Audio")
root.geometry("600x500")
root.resizable(False, False)
# Fondo con imagen
bg_image = Image.open("encripta2.jpg")
bg_photo = ImageTk.PhotoImage(bg_image.resize((600, 500), Image.LANCZOS))
background_label = tk.Label(root, image=bg_photo)
background_label.place(relwidth=1, relheight=1)

# Frame principal
frame = tk.Frame(root, bg="#f0f0f0", bd=5)
frame.pack(pady=20)

# Estilo del botón y los labels
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), background="#1e3d59", foreground="black", width=25, padding=10)
style.map("TButton",
          background=[("active", "gray")],
          foreground=[("active", "#00008B")])

titulo = tk.Label(root, text="SISTEMA DE ENCRIPTADO CON CLAVE DE AUDIO", font=("Helvetica", 16, "bold"), bg="#d1d1d1")
titulo.pack(pady=10)

btn_seleccionar_archivo = ttk.Button(frame, text="Seleccionar archivo", command=seleccionar_archivo)
btn_seleccionar_archivo.grid(row=0, column=0, pady=10)

lbl_archivo = tk.Label(frame, text="Archivo seleccionado: Ninguno", font=("Helvetica", 10), bg="#f0f0f0")
lbl_archivo.grid(row=1, column=0, pady=5)

btn_grabar_clave_encriptado = ttk.Button(frame, text="Grabar clave para encriptar", command=grabar_clave_encriptado)
btn_grabar_clave_encriptado.grid(row=2, column=0, pady=10)

btn_grabar_clave_desencriptado = ttk.Button(frame, text="Grabar clave para desencriptar", command=grabar_clave_desencriptado)
btn_grabar_clave_desencriptado.grid(row=4, column=0, pady=10)

btn_encriptar = ttk.Button(frame, text="Encriptar archivo", command=encriptar)
btn_encriptar.grid(row=3, column=0, pady=10)

lbl_estado = tk.Label(root, text="", font=("Helvetica", 12), bg="#d1d1d1")
lbl_estado.pack(pady=10)

root.mainloop()
