import tkinter as tk
import subprocess
import time

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

        self.mode = 0  # 0=text, 1=num, 2=char

        self._build()

    def _build(self):
        # Entry
        self.entry = tk.Entry(
            self.root,
            bg=BG2,
            fg=WHITE,
            insertbackground=CYAN,
            font=("monospace", 12),
            relief="flat",
            bd=6,
            width=40
        )
        self.entry.pack(pady=10, padx=10)

        # Frame teclado
        self.kb_frame = tk.Frame(self.root, bg=BG)
        self.kb_frame.pack()

        # Inicial
        self.keyboard = VirtualKeyboard(self.kb_frame, self.entry)
        self.keyboard.pack()

        # Botones control
        controls = tk.Frame(self.root, bg=BG)
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
            text="Enviar a otra app",
            command=self._send_text,
            bg="#0f2520",
            fg=CYAN
        ).pack(side="left", padx=5)

    def _switch_keyboard(self):
        self.keyboard.destroy()

        self.mode = (self.mode + 1) % 3

        if self.mode == 0:
            self.keyboard = VirtualKeyboard(self.kb_frame, self.entry)
        elif self.mode == 1:
            self.keyboard = Numpad(self.kb_frame, self.entry)
        else:
            self.keyboard = CharKeyboard(self.kb_frame, self.entry)

        self.keyboard.pack()

    def _send_text(self):
        text = self.entry.get()

        if not text:
            return

        print("Tienes 3 segundos para cambiar de ventana...")
        time.sleep(3)

        try:
            buffer = ""

            for ch in text:
                if ch == "⏎":
                    if buffer:
                        subprocess.run([
                            "xdotool", "type", "--delay", "5", buffer
                        ])
                        buffer = ""

                    subprocess.run(["xdotool", "key", "Return"])

                else:
                    buffer += ch

            if buffer:
                subprocess.run([
                    "xdotool", "type", "--delay", "5", buffer
                ])

        except Exception as e:
            print("Error enviando texto:", e)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
