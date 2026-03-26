import tkinter as tk
import subprocess

from keyboards import VirtualKeyboard, Numpad, CharKeyboard

BG = "#0f0f12"
CYAN = "#7fd4c1"
WHITE = "#e0e0e8"
BG2 = "#161620"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Input Sender")
        self.root.configure(bg=BG)

        self.mode = 0
        self.target_window = None
        self.target_name = "No seleccionado"

        self._build()

    def _build(self):
        # ===== SCROLL GLOBAL =====
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

        # ===== CONTENIDO =====

        # TEXT
        self.entry = tk.Text(
            self.scrollable_frame,
            bg=BG2,
            fg=WHITE,
            insertbackground=CYAN,
            font=("monospace", 12),
            relief="flat",
            bd=6,
            height=2,
            width=40
        )
        self.entry.pack(pady=10, padx=10)

        # Destino
        self.label_target = tk.Label(
            self.scrollable_frame,
            text=f"Destino: {self.target_name}",
            bg=BG,
            fg=CYAN,
            font=("monospace", 9)
        )
        self.label_target.pack(pady=(5, 0))

        # ===== FRAME FIJO TECLADO =====
        self.kb_frame = tk.Frame(self.scrollable_frame, bg=BG)
        self.kb_frame.pack(pady=10)

        self.keyboard = VirtualKeyboard(self.kb_frame, self.entry)
        self.keyboard.pack()

        # ===== BOTONES =====
        controls = tk.Frame(self.scrollable_frame, bg=BG)
        controls.pack(pady=10)

        tk.Button(
            controls,
            text="Switch Keyboard",
            command=self._switch_keyboard,
            bg=BG2,
            fg=CYAN
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="Seleccionar destino",
            command=self._select_target,
            bg=BG2,
            fg=CYAN
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="Enviar a otra app",
            command=self._send_text,
            bg="#0f2520",
            fg=CYAN
        ).pack(side="left", padx=5)

    def _switch_keyboard(self):
        for widget in self.kb_frame.winfo_children():
            widget.destroy()

        self.mode = (self.mode + 1) % 3

        if self.mode == 0:
            self.keyboard = VirtualKeyboard(self.kb_frame, self.entry)
        elif self.mode == 1:
            self.keyboard = CharKeyboard(self.kb_frame, self.entry)
        else:
            self.keyboard = Numpad(self.kb_frame, self.entry)

        self.keyboard.pack()

    # 🔥 NUEVA IMPLEMENTACIÓN CORRECTA
    def _select_target(self):
        print("Selecciona la ventana destino...")

        # Minimiza tu app
        self.root.iconify()

        # Espera y captura
        self.root.after(1500, self._capture_window)

    def _capture_window(self):
        try:
            win_id = subprocess.check_output(
                ["xdotool", "getwindowfocus"]
            ).decode().strip()

            self.target_window = win_id

            try:
                name = subprocess.check_output(
                    ["xdotool", "getwindowname", win_id]
                ).decode().strip()
            except:
                name = "Ventana desconocida"

            self.target_name = name
            self.label_target.config(text=f"Destino: {self.target_name}")

            # Restaurar app
            self.root.deiconify()

            print(f"Ventana seleccionada: {win_id} - {name}")

        except Exception as e:
            print("Error seleccionando ventana:", e)

    def _send_text(self):
        if not self.target_window:
            print("No has seleccionado una ventana destino")
            return

        text = self.entry.get("1.0", "end-1c")

        if not text:
            return

        try:
            subprocess.run(["xdotool", "windowactivate", self.target_window])

            buffer = ""

            for ch in text:
                if ch == "⏎":
                    if buffer:
                        subprocess.run(["xdotool", "type", "--delay", "5", buffer])
                        buffer = ""
                    subprocess.run(["xdotool", "key", "Return"])

                elif ch == "←":
                    if buffer:
                        subprocess.run(["xdotool", "type", "--delay", "5", buffer])
                        buffer = ""
                    subprocess.run(["xdotool", "key", "Left"])

                elif ch == "→":
                    if buffer:
                        subprocess.run(["xdotool", "type", "--delay", "5", buffer])
                        buffer = ""
                    subprocess.run(["xdotool", "key", "Right"])

                elif ch == "↑":
                    if buffer:
                        subprocess.run(["xdotool", "type", "--delay", "5", buffer])
                        buffer = ""
                    subprocess.run(["xdotool", "key", "Up"])

                elif ch == "↓":
                    if buffer:
                        subprocess.run(["xdotool", "type", "--delay", "5", buffer])
                        buffer = ""
                    subprocess.run(["xdotool", "key", "Down"])
                elif ch == "⌦":
                    if buffer:
                        subprocess.run(["xdotool", "type", "--delay", "5", buffer])
                        buffer = ""
                    subprocess.run(["xdotool", "key", "Delete"])

                else:
                    buffer += ch

            if buffer:
                subprocess.run(["xdotool", "type", "--delay", "5", buffer])

        except Exception as e:
            print("Error enviando texto:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
