"""
controller.py — lógica de negocio separada del GUI
Maneja todo lo relacionado con xdotool y la ventana destino.
"""
import subprocess


# Caracteres especiales que se traducen a teclas xdotool
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
    "Esc":  "Escape",
    "Tab":  "Tab",
    "Alt":  "alt",
    "Ins":  "Insert",
    "Home": "Home",
    "End":  "End",
    "PgUp": "Prior",
    "PgDn": "Next",
}

# Modificadores que se combinan con otras teclas
_MODIFIERS = {
    "Alt":   "alt",
    "Ctrl":  "ctrl",
    "Shift": "shift",
}


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
        """
        Captura la ventana que tenga el foco en ese momento.
        Devuelve (window_id, window_name).
        Lanza RuntimeError si xdotool falla.
        """
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
        """
        Envía una combinación de teclas directamente a la ventana destino.
        Ejemplo: key="ctrl+c"
        Lanza ValueError si no hay ventana seleccionada.
        """
        if not self.target_window:
            raise ValueError("No hay ventana destino seleccionada.")
        try:
            subprocess.run(["xdotool", "windowactivate", self.target_window], check=True)
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
        """
        Envía `text` a la ventana destino.
        Los caracteres especiales (⏎ ← → ↑ ↓ ⌦) se convierten en teclas.
        Lanza ValueError si no hay ventana seleccionada.
        Lanza RuntimeError si xdotool falla.
        """
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
        """Recorre el texto y manda cada carácter o tecla especial."""
        buffer = ""
        i = 0
        while i < len(text):
            # Combinaciones Alt+Fx  (ej: "Alt+F4")
            combo = self._match_combo(text, i)
            if combo:
                self._flush_buffer(buffer)
                buffer = ""
                modifier, key = combo
                xkey = f"{_MODIFIERS[modifier]}+{_SPECIAL_KEYS.get(key, key)}"
                subprocess.run(["xdotool", "key", xkey])
                i += len(modifier) + 1 + len(key)  # "Alt" + "+" + "F4"
                continue

            # Teclas especiales simples (más largas primero)
            matched = None
            for key in sorted(_SPECIAL_KEYS, key=len, reverse=True):
                if text[i:].startswith(key):
                    matched = key
                    break

            if matched:
                self._flush_buffer(buffer)
                buffer = ""
                subprocess.run(["xdotool", "key", _SPECIAL_KEYS[matched]])
                i += len(matched)
            else:
                buffer += text[i]
                i += 1

        self._flush_buffer(buffer)

    @staticmethod
    def _match_combo(text: str, i: int):
        """Detecta patrón Modificador+Tecla en la posición i.
        Devuelve (modifier, key) o None."""
        for mod in _MODIFIERS:
            prefix = mod + "+"
            if text[i:].startswith(prefix):
                rest = text[i + len(prefix):]
                for key in sorted(_SPECIAL_KEYS, key=len, reverse=True):
                    if rest.startswith(key):
                        return mod, key
        return None

    @staticmethod
    def _flush_buffer(buffer: str) -> None:
        if buffer:
            subprocess.run(["xdotool", "type", "--delay", "5", buffer])
