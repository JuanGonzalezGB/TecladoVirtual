"""
keyboards.py — teclados virtuales reutilizables
"""
import tkinter as tk

BG      = "#0f0f12"
BG2     = "#161620"
BORDER  = "#1e1e2a"
ORANGE  = "#f0a030"
CYAN    = "#7fd4c1"
WHITE   = "#e0e0e8"
MUTED   = "#4a4a5a"

F_NORMAL = ("monospace", 9)
F_SMALL  = ("monospace", 8)


# =========================================
# QWERTY
# =========================================
class VirtualKeyboard(tk.Frame):
    KEYS = [
        list("1234567890"),
        list("qwertyuiop"),
        list("asdfghjklñ"),
        list("zxcvbnm.-_"),
    ]

    def __init__(self, parent, entry, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._entry = entry
        self._uppercase = False
        self._build()

    def _build(self):
        for row in self.KEYS:
            rf = tk.Frame(self, bg=BG)
            rf.pack()
            for ch in row:
                tk.Button(
                    rf, text=ch, width=3,
                    bg=BG2, fg=WHITE,
                    font=F_SMALL, relief="flat", bd=0,
                    activebackground=BORDER,
                    activeforeground=CYAN,
                    command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        sp = tk.Frame(self, bg=BG)
        sp.pack(pady=(2, 0))

        self._btn_case = tk.Button(
            sp, text="abc", width=4,
            bg=BG2, fg=MUTED,
            font=F_SMALL, relief="flat", bd=0,
            command=self._toggle_case
        )
        self._btn_case.pack(side="left", padx=1)

        tk.Button(
            sp, text="espacio", width=8,
            bg=BG2, fg=WHITE,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type(" ")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⏎", width=4,
            bg=BG2, fg=CYAN,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⏎")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌫", width=4,
            bg=BG2, fg=ORANGE,
            font=F_SMALL, relief="flat", bd=0,
            command=self._backspace
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌦", width=4,
            bg=BG2, fg=CYAN,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⌦")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="Limpiar", width=8,
            bg=BG2, fg=MUTED,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._entry.delete("1.0", "end")
        ).pack(side="left", padx=1)

    def _type(self, ch: str):
        ch = ch.upper() if self._uppercase else ch
        self._entry.insert("insert", ch)

    def _backspace(self):
        try:
            if isinstance(self._entry, tk.Text):
                if self._entry.compare("insert", ">", "1.0"):
                    self._entry.delete("insert-1c", "insert")
            else:
                pos = self._entry.index("insert")
                if pos > 0:
                    self._entry.delete(pos - 1, pos)
        except Exception:
            pass

    def _toggle_case(self):
        self._uppercase = not self._uppercase
        self._btn_case.config(text="ABC" if self._uppercase else "abc")


# =========================================
# NUMPAD
# =========================================
class Numpad(tk.Frame):
    def __init__(self, parent, entry, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._entry = entry
        self._build()

    def _build(self):
        rf1 = tk.Frame(self, bg=BG)
        rf1.pack()
        for ch in "1234567890":
            tk.Button(
                rf1, text=ch, width=2,
                bg=BG2, fg=WHITE,
                font=F_NORMAL, relief="flat", bd=0,
                activebackground=BORDER,
                activeforeground=CYAN,
                command=lambda c=ch: self._type(c)
            ).pack(side="left", padx=1, pady=2)

        rf2 = tk.Frame(self, bg=BG)
        rf2.pack(pady=(2, 0))

        for ch, fg, w, cmd in [
            (".", WHITE, 2, lambda: self._type(".")),
            ("/", WHITE, 2, lambda: self._type("/")),
            ("⏎", CYAN, 2, lambda: self._type("⏎")),
            ("⌫", ORANGE, 2, self._backspace),
            ("⌦", CYAN, 2, lambda: self._type("⌦")),
            ("Limpiar", MUTED, 6, lambda: self._entry.delete("1.0", "end")),
            ("⬅", CYAN, 3, lambda: self._type("←")),
            ("➡", CYAN, 3, lambda: self._type("→")),
            ("⬆", CYAN, 3, lambda: self._type("↑")),
            ("⬇", CYAN, 3, lambda: self._type("↓")),
        ]:
            tk.Button(
                rf2, text=ch, width=w,
                bg=BG2, fg=fg,
                font=F_SMALL, relief="flat", bd=0,
                activebackground=BORDER,
                command=cmd
            ).pack(side="left", padx=2)

    def _type(self, ch: str):
        self._entry.insert("insert", ch)

    def _backspace(self):
        try:
            self._entry.delete("insert-1c", "insert")
        except:
            pass


# =========================================
# CHARACTERS
# =========================================
class CharKeyboard(tk.Frame):
    KEYS = [
        list("!@#$%^&*()"),
        list("[]{}<>/\\|"),
        list("+=~`"),
        list(".,:;\"'¿?"),
    ]

    def __init__(self, parent, entry, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._entry = entry
        self._build()

    def _build(self):
        for row in self.KEYS:
            rf = tk.Frame(self, bg=BG)
            rf.pack()
            for ch in row:
                tk.Button(
                    rf, text=ch, width=3,
                    bg=BG2, fg=WHITE,
                    font=F_SMALL, relief="flat", bd=0,
                    activebackground=BORDER,
                    activeforeground=CYAN,
                    command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        sp = tk.Frame(self, bg=BG)
        sp.pack(pady=(2, 0))

        tk.Button(
            sp, text="espacio", width=8,
            bg=BG2, fg=WHITE,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type(" ")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⏎", width=4,
            bg=BG2, fg=CYAN,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⏎")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌫", width=4,
            bg=BG2, fg=ORANGE,
            font=F_SMALL, relief="flat", bd=0,
            command=self._backspace
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌦", width=4,
            bg=BG2, fg=CYAN,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⌦")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="Limpiar", width=8,
            bg=BG2, fg=MUTED,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._entry.delete("1.0", "end")
        ).pack(side="left", padx=1)

    def _type(self, ch: str):
        self._entry.insert("insert", ch)

    def _backspace(self):
        try:
            self._entry.delete("insert-1c", "insert")
        except:
            pass


# =========================================
# FUNCTION KEYS
# =========================================
class FnKeyboard(tk.Frame):
    KEYS = [
        ["F1", "F2", "F3", "F4", "F5", "F6"],
        ["F7", "F8", "F9", "F10", "F11", "F12"],
    ]

    def __init__(self, parent, entry, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._entry = entry
        self._alt = False
        self._btn_alt = None
        self._build()

    def _build(self):
        for row in self.KEYS:
            rf = tk.Frame(self, bg=BG)
            rf.pack()
            for key in row:
                tk.Button(
                    rf, text=key, width=4,
                    bg=BG2, fg=ORANGE,
                    font=F_NORMAL, relief="flat", bd=0,
                    activebackground=BORDER,
                    activeforeground=CYAN,
                    command=lambda k=key: self._type_fn(k)
                ).pack(side="left", padx=2, pady=2)

        # Fila 1: teclas de navegación
        sp = tk.Frame(self, bg=BG)
        sp.pack(pady=(4, 0))

        self._btn_alt = tk.Button(
            sp, text="Alt", width=4,
            bg=BG2, fg=CYAN,
            font=F_SMALL, relief="flat", bd=0,
            activebackground=BORDER,
            command=self._toggle_alt
        )
        self._btn_alt.pack(side="left", padx=2)

        for key, fg in [
            ("Esc",  CYAN),
            ("Tab",  WHITE),
            ("Ins",  WHITE),
            ("Home", WHITE),
            ("End",  WHITE),
            ("PgUp", WHITE),
            ("PgDn", WHITE),
        ]:
            tk.Button(
                sp, text=key, width=4,
                bg=BG2, fg=fg,
                font=F_SMALL, relief="flat", bd=0,
                activebackground=BORDER,
                activeforeground=CYAN,
                command=lambda k=key: self._type(k)
            ).pack(side="left", padx=2)

        # Fila 2: utilidades
        sp2 = tk.Frame(self, bg=BG)
        sp2.pack(pady=(2, 0))

        tk.Button(
            sp2, text="⏎", width=4,
            bg=BG2, fg=CYAN,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⏎")
        ).pack(side="left", padx=1)

        tk.Button(
            sp2, text="⌫", width=4,
            bg=BG2, fg=ORANGE,
            font=F_SMALL, relief="flat", bd=0,
            command=self._backspace
        ).pack(side="left", padx=1)

        tk.Button(
            sp2, text="⌦", width=4,
            bg=BG2, fg=CYAN,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⌦")
        ).pack(side="left", padx=1)

        tk.Button(
            sp2, text="Limpiar", width=8,
            bg=BG2, fg=MUTED,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._entry.delete("1.0", "end")
        ).pack(side="left", padx=1)

    def _toggle_alt(self):
        self._alt = not self._alt
        self._btn_alt.config(bg=CYAN if self._alt else BG2,
                             fg=BG  if self._alt else CYAN)

    def _type_fn(self, key: str):
        """F1-F12: si Alt está activo inserta Alt+F4, si no F4."""
        if self._alt:
            self._entry.insert("insert", f"Alt+{key}")
            self._alt = False
            self._btn_alt.config(bg=BG2, fg=CYAN)
        else:
            self._entry.insert("insert", key)

    def _type(self, key: str):
        self._entry.insert("insert", key)

    def _backspace(self):
        try:
            self._entry.delete("insert-1c", "insert")
        except:
            pass
