radio.on()
radio.setGroup(1)
let strip = neopixel.create(DigitalPin.P0, 64, NeoPixelMode.RGB)
let nivel = 0
let nivel_suavizado = 0
let t = 0
//  Anillos desde el centro
let anillos = [[27, 28, 35, 36], [19, 20, 21, 26, 29, 34, 43, 44, 45], [10, 11, 12, 13, 18, 22, 25, 30, 33, 37, 42, 46, 49, 50, 51], [2, 3, 4, 9, 14, 17, 23, 24, 31, 32, 38, 39, 47, 52, 53, 54], [0, 1, 5, 6, 7, 8, 15, 16, 40, 41, 48, 55, 56, 57, 58, 59, 60, 61, 62, 63]]
//  Función HUE → RGB (compatible)
function hue_to_rgb(hue: number): number {
    hue = hue % 360
    let section = Math.idiv(hue, 60)
    let offset = Math.idiv(hue % 60 * 255, 60)
    if (section == 0) {
        return neopixel.rgb(255, offset, 0)
    } else if (section == 1) {
        return neopixel.rgb(255 - offset, 255, 0)
    } else if (section == 2) {
        return neopixel.rgb(0, 255, offset)
    } else if (section == 3) {
        return neopixel.rgb(0, 255 - offset, 255)
    } else if (section == 4) {
        return neopixel.rgb(offset, 0, 255)
    } else {
        return neopixel.rgb(255, 0, 255 - offset)
    }
    
}

//  Receptor de movimiento
radio.onReceivedString(function on_received_string(receivedString: string) {
    let x: number;
    let y: number;
    let z: number;
    let total: number;
    let delta: number;
    
    let parts = _py.py_string_split(receivedString, ",")
    if (parts.length == 3) {
        try {
            x = parseInt(parts[0])
            y = parseInt(parts[1])
            z = parseInt(parts[2])
            total = x * x + y * y + z * z
            delta = Math.abs(total - 1024 * 1024)
            nivel = Math.idiv(delta, 50000)
            if (nivel > 10) {
                nivel = 10
            }
            
        }
        catch (_) {
            basic.showString("?")
        }
        
    }
    
})
//  Animación suave con color desde el centro y latido global
basic.forever(function on_forever() {
    let ring: number[];
    let hue: number;
    let color: number;
    let intensidad: number;
    let j: number;
    let pixel: number;
    let r: number;
    let g: number;
    let b: number;
    
    //  Suavizar nivel
    if (nivel_suavizado < nivel) {
        nivel_suavizado += 0.1
        if (nivel_suavizado > nivel) {
            nivel_suavizado = nivel
        }
        
    } else if (nivel_suavizado > nivel) {
        nivel_suavizado -= 0.1
        if (nivel_suavizado < nivel) {
            nivel_suavizado = nivel
        }
        
    }
    
    //  Respiración: latido triangular
    let frame = Math.trunc(t)
    let ciclo = frame % 80
    let brillo = (ciclo < 40 ? ciclo : 80 - ciclo) / 40
    //  0–1–0
    //  Hue base se desplaza con tiempo
    let hue_base = frame * 3 % 360
    //  Recorremos todos los anillos, siempre encendidos
    let i = 0
    while (i < anillos.length) {
        ring = anillos[i]
        hue = (hue_base + i * 15) % 360
        color = hue_to_rgb(hue)
        intensidad = Math.trunc(255 * brillo * (1 - i / anillos.length))
        //  centro más brillante
        j = 0
        while (j < ring.length) {
            pixel = ring[j]
            r = color >> 16 & 0xFF
            g = color >> 8 & 0xFF
            b = color & 0xFF
            r = Math.trunc(Math.idiv(r * intensidad, 255))
            g = Math.trunc(Math.idiv(g * intensidad, 255))
            b = Math.trunc(Math.idiv(b * intensidad, 255))
            strip.setPixelColor(pixel, neopixel.rgb(r, g, b))
            j += 1
        }
        i += 1
    }
    strip.show()
    //  Tiempo avanza más rápido con mayor movimiento
    t = t + 1 + Math.trunc(nivel_suavizado)
    basic.pause(60)
})
