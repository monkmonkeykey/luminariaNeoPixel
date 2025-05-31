radio.on()
radio.setGroup(1)
serial.redirectToUSB()
let strip = neopixel.create(DigitalPin.P0, 64, NeoPixelMode.RGB)
radio.onReceivedString(function on_received_string(receivedString: string) {
    let x: number;
    let y: number;
    let z: number;
    let total: number;
    let reposo: number;
    let delta: number;
    let nivel: number;
    let color: number;
    let parts = _py.py_string_split(receivedString, ",")
    if (parts.length == 3) {
        try {
            x = parseInt(parts[0])
            y = parseInt(parts[1])
            z = parseInt(parts[2])
            //  Calculamos movimiento total sin usar sqrt
            total = x * x + y * y + z * z
            reposo = 1024 * 1024
            delta = Math.abs(total - reposo)
            //  Escalamos a un nivel entre 0 y 10
            nivel = Math.idiv(delta, 50000)
            if (nivel > 10) {
                nivel = 10
            }
            
            //  Mostrar nivel en pantalla y por serial
            // basic.show_number(nivel)
            // serial.write_line("Nivel: " + str(nivel))
            //  Color según nivel
            if (nivel < 3) {
                color = neopixel.rgb(0, 0, 150)
            } else if (nivel < 7) {
                //  Azul
                color = neopixel.rgb(150, 75, 0)
            } else {
                //  Intermedio
                color = neopixel.rgb(150, 0, 0)
            }
            
            //  Rojo
            for (let i = 0; i < 64; i++) {
                strip.setPixelColor(i, color)
            }
            strip.show()
        }
        catch (_) {
            basic.showString("?")
        }
        
    }
    
})
basic.forever(function on_forever() {
    basic.pause(10)
})
