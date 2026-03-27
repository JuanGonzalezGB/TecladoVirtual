TecladoVirtual

Es necesaria la instalación de xdotool:

	sudo apt install xdotool

--------------------------------------
DESCRIPCIÓN

Teclado virtual para Linux, pensado para rasbperry pi con pantalla 3.5" touchscreen (480x320)  que permite enviar entradas a otra aplicación usando xdotool.

Permite escribir texto, mover el cursor y enviar teclas especiales.

--------------------------------------
FUNCIONALIDADES

- Escritura de texto
- Envío a otra aplicación
- Flechas de dirección
- Backspace
- Delete
- Enter
- Teclas Función

--------------------------------------
TECLAS ESPECIALES

⏎  Enter (Return)
←  Flecha izquierda
→  Flecha derecha
↑  Flecha arriba
↓  Flecha abajo
⌫  Backspace
⌦  Delete (nuevo)

--------------------------------------
keyboards.py

Se implementaron cuatro teclados:

- VirtualKeyboard
- Numpad
- CharKeyboard
- FnKeyboard

Se añadió el botón:

⌦ DELETE

Funcionamiento:
- Se inserta el carácter "⌦" en el buffer
- No ejecuta acción inmediata
- Se procesa al enviar

--------------------------------------
main.py

En _send_text():

elif ch == "⌦":
    flush buffer
    xdotool key Delete

Resultado:
- ⌦ se convierte en tecla Delete real
- Se envía a la aplicación destino

--------------------------------------
DIFERENCIA BACKSPACE vs DELETE

Backspace (⌫):
- Borra carácter anterior dentro del input

Delete (⌦):
- Borra carácter siguiente dentro de la app destino al ser enviado

--------------------------------------
FLUJO

1. Usuario escoge ventana destino:
   - tener preparada la ventana destino(terminal, editor de texto, navegador,etc.)
   - clic en botón seleccionar destino(parte de abajo)
   - se minimizará el teclado y seleccionará la ventana que esté en primer plano o usuario seleccione
2. Usuario escribe en teclado virtual
3. Se guarda en buffer
4. Usuario presiona enviar
5. Se procesa:
   - texto → escritura
   - ⏎ → Enter
   - ⌫ → Backspace
   - ⌦ → Delete
   - flechas → navegación
5. Se envía a la app destino

--------------------------------------
RESUMEN

El sistema soporta:
- escritura
- flechas
- backspace
- delete
- enter
- envío a otra aplicación
