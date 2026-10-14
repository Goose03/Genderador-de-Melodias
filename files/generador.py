import math
import random
import struct
import sys
import wave

NOTAS = ["DO", "RE", "MI", "FA", "SOL", "LA", "SI", "DO'"]
FRECUENCIAS = {
    "DO": 261.63, "RE": 293.66, "MI": 329.63, "FA": 349.23,
    "SOL": 392.00, "LA": 440.00, "SI": 493.88, "DO'": 523.25,
}

MATRIZ = [
    [0.05, 0.25, 0.30, 0.10, 0.20, 0.05, 0.025, 0.025],  # DO
    [0.30, 0.05, 0.30, 0.20, 0.05, 0.05, 0.05, 0.00],    # RE
    [0.10, 0.30, 0.05, 0.30, 0.15, 0.05, 0.025, 0.025],  # MI
    [0.05, 0.05, 0.30, 0.05, 0.35, 0.10, 0.05, 0.05],    # FA
    [0.10, 0.05, 0.10, 0.25, 0.05, 0.30, 0.10, 0.05],    # SOL
    [0.05, 0.05, 0.05, 0.10, 0.35, 0.05, 0.30, 0.05],    # LA
    [0.15, 0.00, 0.05, 0.05, 0.10, 0.30, 0.05, 0.30],    # SI
    [0.30, 0.05, 0.05, 0.05, 0.15, 0.05, 0.30, 0.05],    # DO'
]

FRECUENCIA_MUESTREO = 44100

def validar_matriz():
    """Revisa que la matriz sea cuadrada y que cada fila sume 1."""
    for i, fila in enumerate(MATRIZ):
        assert len(fila) == len(NOTAS), f"La fila {NOTAS[i]} tiene tamaño incorrecto"
        assert abs(sum(fila) - 1.0) < 1e-9, f"La fila {NOTAS[i]} suma {sum(fila)}, no 1"


def imprimir_matriz():
    print("Matriz de transiciones (fila = nota actual, columna = siguiente):\n")
    print("      " + "".join(f"{n:>7}" for n in NOTAS))
    for nota, fila in zip(NOTAS, MATRIZ):
        print(f"{nota:>5} " + "".join(f"{p:7.3f}" for p in fila))
    print()



def siguiente_nota(indice_actual):
    r = random.random()
    acumulado = 0.0
    for j, p in enumerate(MATRIZ[indice_actual]):
        acumulado += p
        if r < acumulado:
            return j
    return len(NOTAS) - 1


def crear_muestras(frecuencia, duracion):
    n = int(FRECUENCIA_MUESTREO * duracion)
    fade = int(0.01 * FRECUENCIA_MUESTREO)
    muestras = []
    for i in range(n):
        valor = math.sin(2 * math.pi * frecuencia * i / FRECUENCIA_MUESTREO)
        if i < fade:
            valor *= i / fade
        elif i > n - fade:
            valor *= (n - i) / fade
        muestras.append(valor * 0.5)
    return muestras


def reproducir(frecuencia, duracion):
    try:
        import numpy as np
        import sounddevice as sd
        sd.play(np.array(crear_muestras(frecuencia, duracion), dtype="float32"),
                FRECUENCIA_MUESTREO)
        sd.wait()
    except Exception:
        pass


def guardar_wav(muestras, nombre="melodia.wav"):
    with wave.open(nombre, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(FRECUENCIA_MUESTREO)
        f.writeframes(b"".join(struct.pack("<h", int(m * 32767)) for m in muestras))
    print(f"\nMelodia guardada en '{nombre}'")


def generar_melodia(num_transiciones=16, duracion=0.4, semilla=None):
    if semilla is not None:
        random.seed(semilla)

    validar_matriz()
    imprimir_matriz()

    actual = 0
    todas_las_muestras = []
    melodia = []

    print(f"Generando {num_transiciones} transiciones...\n")
    print(f"Inicio: {NOTAS[actual]}")
    reproducir(FRECUENCIAS[NOTAS[actual]], duracion)
    todas_las_muestras += crear_muestras(FRECUENCIAS[NOTAS[actual]], duracion)
    melodia.append(NOTAS[actual])

    for paso in range(1, num_transiciones + 1):
        nueva = siguiente_nota(actual)
        print(f"{paso:>3}. {NOTAS[actual]:>3} -> {NOTAS[nueva]:<3} "
              f"(prob. {MATRIZ[actual][nueva]:.3f})")
        actual = nueva
        frecuencia = FRECUENCIAS[NOTAS[actual]]
        reproducir(frecuencia, duracion)
        todas_las_muestras += crear_muestras(frecuencia, duracion)
        melodia.append(NOTAS[actual])

    print("\nMelodia completa:", " ".join(melodia))
    guardar_wav(todas_las_muestras)
    return melodia


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    generar_melodia(num_transiciones=n)