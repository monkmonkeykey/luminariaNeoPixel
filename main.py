from microbit import *
import radio
import neopixel

radio.on()
radio.set_group(1)
serial.redirect_to_usb()

strip = neopixel.create(DigitalPin.P0, 64, NeoPixelMode.RGB)

def on_received_string(receivedString):
    parts = receivedString.split(",")
    if len(parts) == 3:
        try:
            x = int(parts[0])
            y = int(parts[1])
            z = int(parts[2])

            # Calculamos movimiento total sin usar sqrt
            total = x * x + y * y + z * z
            reposo = 1024 * 1024
            delta = abs(total - reposo)

            # Escalamos a un nivel entre 0 y 10
            nivel = delta // 50000
            if nivel > 10:
                nivel = 10

            # Mostrar nivel en pantalla y por serial
            #basic.show_number(nivel)
            #serial.write_line("Nivel: " + str(nivel))

            # Color según nivel
            if nivel < 3:
                color = neopixel.rgb(0, 0, 150)  # Azul
            elif nivel < 7:
                color = neopixel.rgb(150, 75, 0)  # Intermedio
            else:
                color = neopixel.rgb(150, 0, 0)  # Rojo

            for i in range(64):
                strip.set_pixel_color(i, color)
            strip.show()

        except:
            basic.show_string("?")

radio.on_received_string(on_received_string)

def on_forever():
    basic.pause(10)

basic.forever(on_forever)
