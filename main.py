from microbit import *
import radio
import neopixel

radio.on()
radio.set_group(1)

strip = neopixel.create(DigitalPin.P0, 64, NeoPixelMode.RGB)

nivel = 0            # Nivel recibido del otro microbit
nivel_suavizado = 0  # Nivel interpolado suavemente
t = 0                # Tiempo para animación

# Anillos desde el centro hacia los bordes
anillos = [
    [27, 28, 35, 36],
    [19, 20, 21, 26, 29, 34, 43, 44, 45],
    [10, 11, 12, 13, 18, 22, 25, 30, 33, 37, 42, 46, 49, 50, 51],
    [2, 3, 4, 9, 14, 17, 23, 24, 31, 32, 38, 39, 47, 52, 53, 54],
    [0, 1, 5, 6, 7, 8, 15, 16, 40, 41, 48, 55, 56, 57, 58, 59, 60, 61, 62, 63]
]

# Función HUE → RGB (versión simple para MakeCode)
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

# Receptor de datos de aceleración
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

# Animación suave y orgánica
def on_forever():
    global t, nivel_suavizado

    # Interpolación suave entre niveles
    if nivel_suavizado < nivel:
        nivel_suavizado += 0.2
        if nivel_suavizado > nivel:
            nivel_suavizado = nivel
    elif nivel_suavizado > nivel:
        nivel_suavizado -= 0.2
        if nivel_suavizado < nivel:
            nivel_suavizado = nivel

    # Latido triangular: sube y baja entre 0–1
    frame = int(t)
    ciclo = frame % 60

    brillo = (ciclo if ciclo < 30 else 60 - ciclo) / 30

    hue_base = (t * 2) % 360

    fraccion = int(nivel_suavizado * len(anillos))
    max_anillos = 1 + (fraccion // 10)



    i = 0
    while i < max_anillos:
        ring = anillos[i]
        color = hue_to_rgb(hue_base + i * 20)
        intensidad = int(255 * brillo * (1 - i / len(anillos)))  # más fuerte en centro

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
    t += 1
    basic.pause(80)

basic.forever(on_forever)
