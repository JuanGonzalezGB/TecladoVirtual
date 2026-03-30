"""
app.py — GUI con sistema de temas integrado
"""
import tkinter as tk

from keyboards import VirtualKeyboard, Numpad, CharKeyboard, FnKeyboard, ModifierState
from controlador.controller import WindowController

from estilo.estiloFactory import EstiloFactory
from controlador.controladorTemas import etiquetar
from vista.gui_dictionary import *
from vista.selectema import ThemeSelector


class App:
    def __init__(self, root: tk.Tk, config):
        self.root = root
        self.config = config

        self.estilo = EstiloFactory.definirEstilo(self.config.get_theme())

        self.root.title("Virtual Input Sender")
        self.root.configure(bg=self.estilo.bg)
        self.root.geometry("480x280")
        self.root.attributes("-zoomed", True)

        self.mode = 0
        self.ctrl = WindowController()
        self.modifiers = ModifierState()

        self._build()

    # ------------------------------------------------------------------
    # GUI
    # ------------------------------------------------------------------

    def _build(self):
        container = tk.Frame(self.root, bg=self.estilo.bg)
        etiquetar(container, ROL_BG, ROL_WHITE)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=self.estilo.bg, highlightthickness=0)
        self.canvas._bg_rol = ROL_BG

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.estilo.bg)
        etiquetar(self.scrollable_frame, ROL_BG, ROL_WHITE)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ✅ Scroll correcto (Linux / Windows / Mac)
        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        # ------------------ TEXT AREA ------------------

        self.entry = tk.Text(
            self.scrollable_frame,
            bg=self.estilo.bg2,
            fg=self.estilo.white,
            insertbackground=self.estilo.cyan,
            font=("monospace", 12),
            relief="flat", bd=6,
            height=2, width=40
        )
        etiquetar(self.entry, ROL_BG2, ROL_WHITE)
        self.entry.pack(pady=10, padx=10)

        # ------------------ LABEL ------------------

        self.label_target = tk.Label(
            self.scrollable_frame,
            text=f"Destino: {self.ctrl.target_name}",
            bg=self.estilo.bg,
            fg=self.estilo.cyan,
            font=("monospace", 9)
        )
        etiquetar(self.label_target, ROL_BG, ROL_CYAN)
        self.label_target.pack(pady=(5, 0))

        # ------------------ KEYBOARD ------------------

        self.kb_frame = tk.Frame(self.scrollable_frame, bg=self.estilo.bg)
        etiquetar(self.kb_frame, ROL_BG, ROL_WHITE)
        self.kb_frame.pack(pady=(10, 80))

        self.keyboard = VirtualKeyboard(
            self.kb_frame, self.entry, self.modifiers, self.estilo
        )
        self.keyboard.pack()

        # ------------------ CONTROLES ------------------
# ------------------ FOOTER (FUERA DEL SCROLL) ------------------

        footer = tk.Frame(self.root, bg=self.estilo.bg)
        footer.place(relx=0, rely=1, anchor="sw", relwidth=1)

        controls = tk.Frame(footer, bg=self.estilo.bg)
        etiquetar(controls, ROL_BG, ROL_WHITE)
        controls.pack(pady=6)

        btn1 = tk.Button(
            controls, text="Cambiar Teclado",
            command=self._switch_keyboard,
            width=11,
            bg=self.estilo.bg2, fg=self.estilo.cyan
        )
        etiquetar(btn1, ROL_BG2, ROL_CYAN)
        btn1.pack(side="left", padx=5)

        btn2 = tk.Button(
            controls, text="Seleccionar Destino",
            command=self._select_target,
            width=13,
            bg=self.estilo.bg2, fg=self.estilo.cyan
        )
        etiquetar(btn2, ROL_BG2, ROL_CYAN)
        btn2.pack(side="left", padx=5)

        btn3 = tk.Button(
            controls, text="Enviar a Destino",
            command=self._send_text,
            width=11,
            bg=self.estilo.boton, fg=self.estilo.cyan
        )
        etiquetar(btn3, ROL_BOTON, ROL_CYAN)
        btn3.pack(side="left", padx=5)

        btn4 = tk.Button(
            controls, text="🎨",
            command=self._open_theme_selector,
            width=3,
            bg=self.estilo.bg2, fg=self.estilo.cyan
        )
        etiquetar(btn4, ROL_BG2, ROL_CYAN)
        btn4.pack(side="left", padx=5)

    # ------------------------------------------------------------------
    # Scroll FIX
    # ------------------------------------------------------------------

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    # ------------------------------------------------------------------
    # Theme selector
    # ------------------------------------------------------------------

    def _open_theme_selector(self):
        ThemeSelector(self.root, self)

    # ------------------------------------------------------------------
    # Callbacks (SIN CAMBIOS)
    # ------------------------------------------------------------------

    def _switch_keyboard(self):
        scroll_pos = self.canvas.yview()[0]

        for widget in self.kb_frame.winfo_children():
            widget.destroy()

        self.mode = (self.mode + 1) % 4
        keyboards = [VirtualKeyboard, CharKeyboard, Numpad, FnKeyboard]
        kb_class = keyboards[self.mode]

        self.modifiers.clear_callbacks()

        # 🔥 SIEMPRE pedir el estilo actual
        estilo_actual = EstiloFactory.definirEstilo(self.config.get_theme())

        if kb_class is FnKeyboard:
            self.keyboard = FnKeyboard(
                self.kb_frame, self.entry, self.modifiers, estilo_actual, self.ctrl
            )
        else:
            self.keyboard = kb_class(
                self.kb_frame, self.entry, self.modifiers, estilo_actual
    )

        self.keyboard.pack()

        def _restore(event):
            self.scrollable_frame.unbind("<Configure>", bind_id)
            self.canvas.yview_moveto(scroll_pos)

        bind_id = self.scrollable_frame.bind("<Configure>", _restore)

        self.entry.focus_set()
        self.root.focus_force()

    def _select_target(self):
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
            buffer = ""
            i = 0

            while i < len(text):
                if text[i].isspace():
                    buffer += text[i]
                    i += 1
                    continue

                if text[i].isalpha():
                    start = i
                    while i < len(text) and not text[i].isspace():
                        i += 1
                    part = text[start:i]

                    if "+" in part:
                        if buffer:
                            self.ctrl.send_text(buffer)
                            buffer = ""
                        self.ctrl.send_hotkey(part)
                    else:
                        buffer += part
                else:
                    buffer += text[i]
                    i += 1

            if buffer:
                self.ctrl.send_text(buffer)

        except Exception as e:
            self._show_error(str(e))

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------

    def _show_error(self, msg: str):
        self.label_target.config(text=f"⚠ {msg}", fg=self.estilo.red)
        self.label_target._fg_rol = ROL_RED

        self.root.after(3000, lambda: self._restore_label())

    def _restore_label(self):
        self.label_target.config(
            text=f"Destino: {self.ctrl.target_name}",
            fg=self.estilo.cyan
        )
        self.label_target._fg_rol = ROL_CYAN