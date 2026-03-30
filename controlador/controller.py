"""
controller.py — lógica de negocio separada del GUI
Maneja todo lo relacionado con xdotool y la ventana destino.
"""
import re
import subprocess


# Delimitadores de tokens de teclas especiales (deben coincidir con keyboards.py)
# ⟨⟩ son corchetes angulares Unicode (U+27E8/U+27E9), rarísimos en texto normal
_FN_PATTERN = re.compile(r"⟨([^⟩]+)⟩")

# Teclas simples → keysym xdotool
_SPECIAL_KEYS = {
    "⏎":   "Return",
    "←":   "Left",
    "→":   "Right",
    "↑":   "Up",
    "↓":   "Down",
    "⌦":   "Delete",
    # Teclas de función
    "F1":  "F1",  "F2":  "F2",  "F3":  "F3",  "F4":  "F4",
    "F5":  "F5",  "F6":  "F6",  "F7":  "F7",  "F8":  "F8",
    "F9":  "F9",  "F10": "F10", "F11": "F11", "F12": "F12",
    # Teclas extra
    "Esc":   "Escape",
    "Tab":   "Tab",
    "Ins":   "Insert",
    "Home":  "Home",
    "End":   "End",
    "PgUp":  "Prior",
    "PgDn":  "Next",
}

# Modificadores → keysym xdotool
_MODIFIERS = {
    "Alt":   "alt",
    "Ctrl":  "ctrl",
    "Shift": "shift",
}


def _token_to_xkey(token: str) -> str:
    token = token.replace("KEY:", "")
    token = token.replace("MOD:", "")

    parts = token.split("+")

    mods = [_MODIFIERS[p] for p in parts[:-1] if p in _MODIFIERS]
    key = parts[-1]

    xkey = _SPECIAL_KEYS.get(key, key)

    # 🔥 FIX CRÍTICO: xdotool necesita formato limpio
    if mods:
        return "+".join(mods + [xkey])
    return xkey

class WindowController:
    """
    Encapsula la selección de ventana destino y el envío de texto vía xdotool.
    No sabe nada de tkinter.
    """

    def __init__(self):
        self.target_window: str | None = None
        self.target_name: str = "No seleccionado"

    # ------------------------------------------------------------------
    # Selección de ventana
    # ------------------------------------------------------------------

    def capture_focused_window(self) -> tuple[str, str]:
        try:
            win_id = subprocess.check_output(
                ["xdotool", "getwindowfocus"]
            ).decode().strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"No se pudo obtener la ventana activa: {e}")

        try:
            name = subprocess.check_output(
                ["xdotool", "getwindowname", win_id]
            ).decode().strip()
        except subprocess.CalledProcessError:
            name = "Ventana desconocida"

        self.target_window = win_id
        self.target_name = name
        return win_id, name
    def send_hotkey(self, key: str) -> None:
        """Envía una combinación de teclas directamente (sin pasar por el buffer)."""
        if not self.target_window:
            raise ValueError("No hay ventana destino seleccionada.")

        try:
            subprocess.run(
                ["xdotool", "windowactivate", self.target_window],
                check=True
            )

            # 🔴 FIX: normalizar formato KEY:Ins → Insert
            if key.startswith("KEY:"):
                key = key[4:]

            # si viene ya limpio, igual normaliza
            key = _token_to_xkey(key)

            subprocess.run(["xdotool", "key", key], check=True)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error al enviar hotkey: {e}")

    def clear_target(self):
        self.target_window = None
        self.target_name = "No seleccionado"

    # ------------------------------------------------------------------
    # Envío de texto
    # ------------------------------------------------------------------

    def send_text(self, text: str) -> None:
        if not self.target_window:
            raise ValueError("No hay ventana destino seleccionada.")
        if not text:
            return
        try:
            subprocess.run(
                ["xdotool", "windowactivate", self.target_window],
                check=True
            )
            self._dispatch(text)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error al enviar texto: {e}")

    def _dispatch(self, text: str) -> None:
        last = 0
        for m in _FN_PATTERN.finditer(text):
            plain = text[last:m.start()]
            self._dispatch_plain(plain)

            token = m.group(1)

            xkey = _token_to_xkey(token)

            # 🔥 FIX REAL: separar mods correctamente
            if "+" in xkey:
                parts = xkey.split("+")
                mods, key = parts[:-1], parts[-1]

                try:
                    for mod in mods:
                        subprocess.run(["xdotool", "keydown", mod])

                    subprocess.run(["xdotool", "key", key])

                finally:
                    for mod in reversed(mods):
                        subprocess.run(["xdotool", "keyup", mod])
            else:
                subprocess.run(["xdotool", "key", xkey])

            last = m.end()

        self._dispatch_plain(text[last:])

    def _dispatch_plain(self, text: str) -> None:
        if not text:
            return
        subprocess.run(["xdotool", "type", "--delay", "5", text])

    @staticmethod
    def _flush_buffer(buffer: str) -> None:
        if buffer:
            subprocess.run(["xdotool", "type", "--delay", "5", buffer])
