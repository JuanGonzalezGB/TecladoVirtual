"""
app.py — GUI puro, sin lógica de xdotool
"""
import tkinter as tk

from keyboards import VirtualKeyboard, Numpad, CharKeyboard
from controller import WindowController

BG   = "#0f0f12"
BG2  = "#161620"
CYAN = "#7fd4c1"
WHITE = "#e0e0e8"


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Virtual Input Sender")
        self.root.configure(bg=BG)

        self.mode = 0
        self.ctrl = WindowController()   # ← toda la lógica vive aquí

        self._build()

    # ------------------------------------------------------------------
    # Construcción del GUI
    # ------------------------------------------------------------------

    def _build(self):
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=BG)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

        # Área de texto
        self.entry = tk.Text(
            self.scrollable_frame,
            bg=BG2, fg=WHITE,
            insertbackground=CYAN,
            font=("monospace", 12),
            relief="flat", bd=6,
            height=2, width=40
        )
        self.entry.pack(pady=10, padx=10)

        # Etiqueta de destino
        self.label_target = tk.Label(
            self.scrollable_frame,
            text=f"Destino: {self.ctrl.target_name}",
            bg=BG, fg=CYAN,
            font=("monospace", 9)
        )
        self.label_target.pack(pady=(5, 0))

        # Teclado
        self.kb_frame = tk.Frame(self.scrollable_frame, bg=BG)
        self.kb_frame.pack(pady=10)
        self.keyboard = VirtualKeyboard(self.kb_frame, self.entry)
        self.keyboard.pack()

        # Botones de control
        controls = tk.Frame(self.scrollable_frame, bg=BG)
        controls.pack(pady=10)

        tk.Button(controls, text="Switch Keyboard",
                  command=self._switch_keyboard,
                  bg=BG2, fg=CYAN).pack(side="left", padx=5)

        tk.Button(controls, text="Seleccionar destino",
                  command=self._select_target,
                  bg=BG2, fg=CYAN).pack(side="left", padx=5)

        tk.Button(controls, text="Enviar a otra app",
                  command=self._send_text,
                  bg="#0f2520", fg=CYAN).pack(side="left", padx=5)

    # ------------------------------------------------------------------
    # Callbacks del GUI  (solo coordinan, no tienen lógica propia)
    # ------------------------------------------------------------------

    def _switch_keyboard(self):
        scroll_pos = self.canvas.yview()[0]  # guarda posición antes de redibujar

        for widget in self.kb_frame.winfo_children():
            widget.destroy()

        self.mode = (self.mode + 1) % 3
        keyboards = [VirtualKeyboard, CharKeyboard, Numpad]
        self.keyboard = keyboards[self.mode](self.kb_frame, self.entry)
        self.keyboard.pack()

        # after() espera a que tkinter recalcule el scrollregion antes de restaurar
        self.root.after(0, lambda: self.canvas.yview_moveto(scroll_pos))

    def _select_target(self):
        """Minimiza la app y captura la ventana que quede enfocada."""
        self.root.iconify()
        self.root.after(1500, self._on_capture)

    def _on_capture(self):
        try:
            _, name = self.ctrl.capture_focused_window()
            self.label_target.config(text=f"Destino: {name}")
        except RuntimeError as e:
            self._show_error(str(e))
        finally:
            self.root.deiconify()

    def _send_text(self):
        text = self.entry.get("1.0", "end-1c")
        try:
            self.ctrl.send_text(text)
        except (ValueError, RuntimeError) as e:
            self._show_error(str(e))

    # ------------------------------------------------------------------
    # Utilidades de GUI
    # ------------------------------------------------------------------

    def _show_error(self, msg: str):
        """Muestra el error en la etiqueta de destino temporalmente."""
        self.label_target.config(text=f"⚠ {msg}", fg="#e05050")
        self.root.after(3000, lambda: self.label_target.config(
            text=f"Destino: {self.ctrl.target_name}", fg=CYAN
        ))
