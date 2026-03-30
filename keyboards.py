"""
keyboards.py — teclados virtuales reutilizables
"""
import tkinter as tk


F_NORMAL = ("monospace", 9)
F_SMALL  = ("monospace", 8)


def get_mod_colors(estilo):
    return {
        "Alt": estilo.cyan,
        "Ctrl": estilo.orange,
        "Shift": estilo.blue,
    }


# =========================================
# MODIFIER STATE
# (sin cambios lógicos, solo UI externa)
# =========================================
class ModifierState:
    def __init__(self):
        self._active: set[str] = set()
        self._callbacks: list = []

    def reset(self):
        self._active.clear()
        self._refresh()

    def clear_callbacks(self):
        self._callbacks.clear()

    def register(self, mod: str, btn: tk.Button):
        self._callbacks.append((mod, btn))

    def toggle(self, mod: str):
        if mod in self._active:
            self._active.remove(mod)
        else:
            self._active.add(mod)
        self._refresh()

    def consume(self) -> str | None:
        if not self._active:
            return None
        mod = "+".join(sorted(self._active))
        self._active.clear()
        self._refresh()
        return mod

    def peek(self):
        return "+".join(sorted(self._active)) if self._active else None

    def _refresh(self):
        for mod, btn in list(self._callbacks):
            try:
                if not btn.winfo_exists():
                    continue

                active = mod in self._active

                btn.config(
                    bg=btn.cget("activebackground") if active else btn.cget("bg"),
                )

            except tk.TclError:
                pass


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

    def __init__(self, parent, entry, modifiers: ModifierState, estilo, **kwargs):
        super().__init__(parent, bg=estilo.bg, **kwargs)
        self._entry = entry
        self._modifiers = modifiers
        self._estilo = estilo
        self._uppercase = False
        self._build()

    def _build(self):
        e = self._estilo

        for row in self.KEYS:
            rf = tk.Frame(self, bg=e.bg)
            rf.pack()

            for ch in row:
                tk.Button(
                    rf, text=ch, width=3,
                    bg=e.bg2, fg=e.white,
                    font=F_SMALL, relief="flat", bd=0,
                    activebackground=e.border,
                    activeforeground=e.cyan,
                    command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        sp = tk.Frame(self, bg=e.bg)
        sp.pack(pady=(2, 0))

        self._btn_case = tk.Button(
            sp, text="abc", width=4,
            bg=e.bg2, fg=e.muted,
            font=F_SMALL, relief="flat", bd=0,
            command=self._toggle_case
        )
        self._btn_case.pack(side="left", padx=1)

        tk.Button(
            sp, text="espacio", width=8,
            bg=e.bg2, fg=e.white,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type(" ")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⏎", width=4,
            bg=e.bg2, fg=e.cyan,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⏎")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌫", width=4,
            bg=e.bg2, fg=e.orange,
            font=F_SMALL, relief="flat", bd=0,
            command=self._backspace
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌦", width=4,
            bg=e.bg2, fg=e.cyan,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⌦")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="Limpiar", width=8,
            bg=e.bg2, fg=e.muted,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._entry.delete("1.0", "end")
        ).pack(side="left", padx=1)

    def _type(self, ch: str):
        mod = self._modifiers.consume()
        if mod:
            self._entry.insert("insert", f"{mod}+{ch}")
        else:
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
    def __init__(self, parent, entry, modifiers: ModifierState, estilo, **kwargs):
        super().__init__(parent, bg=estilo.bg, **kwargs)
        self._entry = entry
        self._modifiers = modifiers
        self._estilo = estilo
        self._build()

    def _build(self):
        e = self._estilo

        rf1 = tk.Frame(self, bg=e.bg)
        rf1.pack()

        for ch in "1234567890":
            tk.Button(
                rf1, text=ch, width=2,
                bg=e.bg2, fg=e.white,
                font=F_NORMAL, relief="flat", bd=0,
                activebackground=e.border,
                activeforeground=e.cyan,
                command=lambda c=ch: self._type(c)
            ).pack(side="left", padx=1, pady=2)

        rf2 = tk.Frame(self, bg=e.bg)
        rf2.pack(pady=(2, 0))

        for ch, fg, w, cmd in [
            (".", e.white, 2, lambda: self._type(".")),
            ("/", e.white, 2, lambda: self._type("/")),
            ("⏎", e.cyan, 2, lambda: self._type("⏎")),
            ("⌫", e.orange, 2, self._backspace),
            ("⌦", e.cyan, 2, lambda: self._type("⌦")),
            ("Limpiar", e.muted, 6, lambda: self._entry.delete("1.0", "end")),
            ("⬅", e.cyan, 3, lambda: self._type("←")),
            ("➡", e.cyan, 3, lambda: self._type("→")),
            ("⬆", e.cyan, 3, lambda: self._type("↑")),
            ("⬇", e.cyan, 3, lambda: self._type("↓")),
        ]:
            tk.Button(
                rf2, text=ch, width=w,
                bg=e.bg2, fg=e.red,
                font=F_SMALL, relief="flat", bd=0,
                activebackground=e.border,
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

    def __init__(self, parent, entry, modifiers: ModifierState, estilo, **kwargs):
        super().__init__(parent, bg=estilo.bg, **kwargs)
        self._entry = entry
        self._modifiers = modifiers
        self._estilo = estilo
        self._build()

    def _build(self):
        e = self._estilo

        for row in self.KEYS:
            rf = tk.Frame(self, bg=e.bg)
            rf.pack()

            for ch in row:
                tk.Button(
                    rf, text=ch, width=3,
                    bg=e.bg2, fg=e.white,
                    font=F_SMALL, relief="flat", bd=0,
                    activebackground=e.border,
                    activeforeground=e.cyan,
                    command=lambda c=ch: self._type(c)
                ).pack(side="left", padx=1, pady=1)

        sp = tk.Frame(self, bg=e.bg)
        sp.pack(pady=(2, 0))

        tk.Button(
            sp, text="espacio", width=8,
            bg=e.bg2, fg=e.white,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type(" ")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⏎", width=4,
            bg=e.bg2, fg=e.cyan,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⏎")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌫", width=4,
            bg=e.bg2, fg=e.orange,
            font=F_SMALL, relief="flat", bd=0,
            command=self._backspace
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="⌦", width=4,
            bg=e.bg2, fg=e.cyan,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⌦")
        ).pack(side="left", padx=1)

        tk.Button(
            sp, text="Limpiar", width=8,
            bg=e.bg2, fg=e.muted,
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

    def __init__(self, parent, entry, modifiers: ModifierState, estilo, controller=None, **kwargs):
        super().__init__(parent, bg=estilo.bg, **kwargs)
        self._entry = entry
        self._modifiers = modifiers
        self._controller = controller
        self._estilo = estilo
        self._mod_colors = get_mod_colors(estilo)
        self._build()

    def _build(self):
        e = self._estilo

        for row in self.KEYS:
            rf = tk.Frame(self, bg=e.bg)
            rf.pack()

            for key in row:
                tk.Button(
                    rf, text=key, height=1, width=3,
                    bg=e.bg2, fg=e.orange,
                    font=F_NORMAL, relief="flat", bd=0,
                    activebackground=e.border,
                    activeforeground=e.cyan,
                    command=lambda k=key: self._type_fn(k)
                ).pack(side="left", padx=2, pady=1)

        sp = tk.Frame(self, bg=e.bg)
        sp.pack(pady=(4, 0))

        for mod in ("Alt", "Ctrl", "Shift"):
            color = self._mod_colors[mod]
            btn = tk.Button(
                sp, text=mod, width=2,
                bg=e.bg2, fg=color,
                font=F_SMALL, relief="flat", bd=0,
                activebackground=e.border,
                command=lambda m=mod: self._modifiers.toggle(m)
            )
            btn.pack(side="left", padx=2)
            self._modifiers.register(mod, btn)

        for key, fg in [
            ("Esc", e.cyan),
            ("Tab", e.white),
            ("Ins", e.white),
            ("Home", e.white),
            ("End", e.white),
            ("PgUp", e.white),
            ("PgDn", e.white),
        ]:
            tk.Button(
                sp, text=key, width=2,
                bg=e.bg2, fg=fg,
                font=F_SMALL, relief="flat", bd=0,
                activebackground=e.border,
                activeforeground=e.cyan,
                command=lambda k=key: self._type(k)
            ).pack(side="left", padx=2)

        sp2 = tk.Frame(self, bg=e.bg)
        sp2.pack(pady=(2, 0))

        tk.Button(
            sp2, text="⏎", width=3,
            bg=e.bg2, fg=e.cyan,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⏎")
        ).pack(side="left", padx=1)

        tk.Button(
            sp2, text="⌫", width=3,
            bg=e.bg2, fg=e.orange,
            font=F_SMALL, relief="flat", bd=0,
            command=self._backspace
        ).pack(side="left", padx=1)

        tk.Button(
            sp2, text="⌦", width=3,
            bg=e.bg2, fg=e.cyan,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._type("⌦")
        ).pack(side="left", padx=1)

        tk.Button(
            sp2, text="Limpiar", width=8,
            bg=e.bg2, fg=e.muted,
            font=F_SMALL, relief="flat", bd=0,
            command=lambda: self._entry.delete("1.0", "end")
        ).pack(side="left", padx=1)

        sp3 = tk.Frame(self, bg=e.bg)
        sp3.pack(pady=(2, 0))

        for label, hotkey in [("Copiar", "ctrl+c"), ("Cortar", "ctrl+x"), ("Pegar", "ctrl+v")]:
            tk.Button(
                sp3, text=label, width=5,
                bg=e.bg2, fg=e.blue,
                font=F_SMALL, relief="flat", bd=0,
                activebackground=e.border,
                activeforeground=e.cyan,
                command=lambda hk=hotkey: self._send_hotkey(hk)
            ).pack(side="left", padx=2)

        sp4 = tk.Frame(self, bg=e.bg)
        sp4.pack(pady=(2, 0))

        for label, sym in [("⬅", "←"), ("➡", "→"), ("⬆", "↑"), ("⬇", "↓")]:
            tk.Button(
                sp4, text=label, width=3,
                bg=e.bg2, fg=e.red,
                font=F_SMALL, relief="flat", bd=0,
                activebackground=e.border,
                activeforeground=e.cyan,
                command=lambda s=sym: self._type(s)
            ).pack(side="left", padx=2)

    def _send_hotkey(self, hotkey: str):
        if self._controller:
            try:
                self._controller.send_hotkey(hotkey)
            except (ValueError, RuntimeError) as e:
                print(f"Error hotkey: {e}")

    def _type_fn(self, key: str):
        mod = self._modifiers.consume()
        if mod:
            self._entry.insert("insert", f"{mod}+{key}")
        else:
            self._entry.insert("insert", key)

    def _type(self, key: str):
        self._entry.insert("insert", key)

    def _backspace(self):
        try:
            self._entry.delete("insert-1c", "insert")
        except:
            pass