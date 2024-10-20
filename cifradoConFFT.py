#librerias necesarias 
import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
#aumentar record_seconds para que la grabacion dure mas tiempo
def record_audio_with_plot(output_filename, record_seconds=2, sample_rate=44100, channels=1):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=channels,
                        rate=sample_rate, input=True,
                        frames_per_buffer=1024)

    frames = []
    plt.ion()  # Modo interactivo para actualizar en vivo
    fig, ax = plt.subplots()
    x = np.arange(0, 1024)
    line, = ax.plot(x, np.random.rand(1024))
    ax.set_ylim(-5000, 5000)
    ax.set_xlim(0, 1024)
    plt.title("Grabación de voz - Onda de audio en vivo")

    print("Grabando...")
    for _ in range(0, int(sample_rate / 1024 * record_seconds)):
        data = stream.read(1024)
        frames.append(data)

        # Convertir los datos de audio en un array de NumPy
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Actualizar el gráfico en vivo
        line.set_ydata(audio_data)
        fig.canvas.draw()
        fig.canvas.flush_events()

    print("Grabación completada.")
    plt.ioff()  # Apagar el modo interactivo
    plt.show()

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Guardar el audio en archivo .wav
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Procesar el audio grabado y realizar la FFT
    signal = np.frombuffer(b''.join(frames), dtype=np.int16)

    # Realizar la FFT
    fft_data = np.fft.fft(signal)
    freq = np.fft.fftfreq(len(fft_data), 1 / sample_rate)
    #muestra los coeficientes de fourier en la consola
    print("Coeficientes de Fourier:")
    print(fft_data)

    # Magnitud de la FFT (espectro de frecuencias)
    magnitude = np.abs(fft_data)

    
    mask = freq >= 0
    freq = freq[mask]
    magnitude = magnitude[mask]

    # Graficar el espectro de frecuencias
    plt.figure()
    plt.plot(freq, magnitude)
    plt.title("Espectro de Frecuencias")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Magnitud")
    plt.grid(True)
    plt.xlim(0, 5000)  # se puede modificar para que la grafica se vea mejor
    plt.show()

record_audio_with_plot("voz_usuario_con_grafico.wav")
