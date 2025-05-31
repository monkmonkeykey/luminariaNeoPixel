from microbit import *
import radio
import neopixel

radio.on()
radio.set_group(1)

strip = neopixel.create(DigitalPin.P0, 64, NeoPixelMode.RGB)

nivel = 0
nivel_suavizado = 0
t = 0

# Anillos desde el centro
anillos = [
    [27, 28, 35, 36],
    [19, 20, 21, 26, 29, 34, 43, 44, 45],
    [10, 11, 12, 13, 18, 22, 25, 30, 33, 37, 42, 46, 49, 50, 51],
    [2, 3, 4, 9, 14, 17, 23, 24, 31, 32, 38, 39, 47, 52, 53, 54],
    [0, 1, 5, 6, 7, 8, 15, 16, 40, 41, 48, 55, 56, 57, 58, 59, 60, 61, 62, 63]
]

# Función HUE → RGB (compatible)
def hue_to_rgb(hue):
    hue = hue % 360
    section = hue // 60
    offset = (hue % 60) * 255 // 60

    if section == 0:
        return neopixel.rgb(255, offset, 0)
    elif section == 1:
        return neopixel.rgb(255 - offset, 255, 0)
    elif section == 2:
        return neopixel.rgb(0, 255, offset)
    elif section == 3:
        return neopixel.rgb(0, 255 - offset, 255)
    elif section == 4:
        return neopixel.rgb(offset, 0, 255)
    else:
        return neopixel.rgb(255, 0, 255 - offset)

# Receptor de movimiento
def on_received_string(receivedString):
    global nivel
    parts = receivedString.split(",")
    if len(parts) == 3:
        try:
            x = int(parts[0])
            y = int(parts[1])
            z = int(parts[2])
            total = x * x + y * y + z * z
            delta = abs(total - 1024 * 1024)
            nivel = delta // 50000
            if nivel > 10:
                nivel = 10
        except:
            basic.show_string("?")

radio.on_received_string(on_received_string)

# Animación suave con color desde el centro y latido global
def on_forever():
    global t, nivel_suavizado

    # Suavizar nivel
    if nivel_suavizado < nivel:
        nivel_suavizado += 0.1
        if nivel_suavizado > nivel:
            nivel_suavizado = nivel
    elif nivel_suavizado > nivel:
        nivel_suavizado -= 0.1
        if nivel_suavizado < nivel:
            nivel_suavizado = nivel

    # Respiración: latido triangular
    frame = int(t)
    ciclo = frame % 80
    brillo = (ciclo if ciclo < 40 else 80 - ciclo) / 40  # 0–1–0

    # Hue base se desplaza con tiempo
    hue_base = (frame * 3) % 360

    # Recorremos todos los anillos, siempre encendidos
    i = 0
    while i < len(anillos):
        ring = anillos[i]
        hue = (hue_base + i * 15) % 360
        color = hue_to_rgb(hue)

        intensidad = int(255 * brillo * (1 - i / len(anillos)))  # centro más brillante

        j = 0
        while j < len(ring):
            pixel = ring[j]

            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF

            r = int(r * intensidad // 255)
            g = int(g * intensidad // 255)
            b = int(b * intensidad // 255)

            strip.set_pixel_color(pixel, neopixel.rgb(r, g, b))
            j += 1
        i += 1

    strip.show()

    # Tiempo avanza más rápido con mayor movimiento
    t = t + 1 + int(nivel_suavizado)
    basic.pause(60)

basic.forever(on_forever)
