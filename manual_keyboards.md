# Manual de implementación — keyboards.py

## Visión general

`vista/keyboards.py` provee widgets de teclado virtual reutilizables
construidos sobre `tk.Frame`. Diseñados para pantallas táctiles (480×300)
donde no hay teclado físico disponible.

| Widget            | Uso                                              |
|-------------------|--------------------------------------------------|
| `VirtualKeyboard` | Texto libre — letras, números, espacio           |
| `CharKeyboard`    | Símbolos — `!@#$%` `[]{}` `.:,;` etc.           |
| `Numpad`          | IPs, puertos, subredes, números                  |
| `FnKeyboard`      | Teclas F1–F12, modificadores y teclas de sistema |

`VirtualKeyboard` incluye acceso interno a `CharKeyboard` (botón `#@`)
y a `Numpad` (botón `123`) — no hace falta instanciarlos por separado.

---

## Requisitos

- Python 3.10+
- tkinter
- Un objeto `estilo` con los atributos de color definidos (ver sección Estilo)

---

## El objeto estilo

Los teclados no hardcodean ningún color. Reciben un objeto `estilo` con
estos atributos como mínimo:

```python
estilo.bg      # fondo principal
estilo.bg2     # fondo de botones
estilo.border  # fondo activo de botones
estilo.white   # texto principal
estilo.cyan    # texto de acento / teclas especiales
estilo.orange  # tecla de borrado ⌫
estilo.muted   # texto secundario (Limpiar, abc)
```

Cualquier objeto que tenga estos atributos funciona — no es necesario
heredar de ninguna clase específica.

---

## Firma de cada clase

```python
VirtualKeyboard(estilo, parent, entry, **kwargs)
CharKeyboard(estilo, parent, entry, on_back=None, **kwargs)
Numpad(estilo, parent, entry, on_back=None, **kwargs)
FnKeyboard(estilo, parent, entry, on_back=None, **kwargs)
```

| Parámetro  | Tipo       | Descripción                                           |
|------------|------------|-------------------------------------------------------|
| `estilo`   | objeto     | Objeto con atributos de color                         |
| `parent`   | tk.Widget  | Widget contenedor padre                               |
| `entry`    | tk.Entry   | Campo de texto donde se insertará el texto            |
| `on_back`  | callable   | Función para volver al teclado anterior (opcional)    |
| `**kwargs` | dict       | Se pasan al `tk.Frame` base                           |

---

## Uso básico

### Numpad — teclado numérico

```python
from vista.keyboards import Numpad

entry = tk.Entry(parent, ...)
numpad = Numpad(estilo, parent, entry)
numpad.pack()
```

Incluye: dígitos `0-9`, punto `.`, dos puntos `:`, barra `/`, borrar `⌫`
y botón `Limpiar`. Si se pasa `on_back`, aparece un botón `abc` para volver.

### VirtualKeyboard — teclado de letras

```python
from vista.keyboards import VirtualKeyboard

entry = tk.Entry(parent, ...)
teclado = VirtualKeyboard(estilo, parent, entry)
teclado.pack()
```

Incluye acceso a `CharKeyboard` (botón `#@`) y a `Numpad` (botón `123`).
Ambas alternaciones se manejan internamente — destruyen el widget actual
y crean el nuevo en el mismo contenedor.

---

## FnKeyboard — teclas de función y modificadores

`FnKeyboard` agrupa las teclas que no caben en el QWERTY ni en el Numpad:
F1–F12, modificadores (Alt, Ctrl, Shift), teclas de sistema y flechas.

```python
from vista.keyboards import FnKeyboard

entry = tk.Entry(parent, ...)
fn_kb = FnKeyboard(estilo, parent, entry)
fn_kb.pack()
```

### Contenido de FnKeyboard

| Grupo          | Teclas                                           |
|----------------|--------------------------------------------------|
| Función        | F1 F2 F3 F4 F5 F6 / F7 F8 F9 F10 F11 F12        |
| Modificadores  | Alt · Ctrl · Shift (toggle — se activan al click)|
| Sistema        | Esc Tab Ins Home End PgUp PgDn                   |
| Flechas        | ← → ↑ ↓                                         |
| Edición        | ⏎ ⌫ ⌦ Limpiar                                   |
| Clipboard      | Copiar · Cortar · Pegar                          |

### Modificadores

Los botones Alt, Ctrl y Shift son **toggle** — se activan al primer click
y se desactivan al siguiente. Su estado visual cambia de color para indicar
que están activos.

Cuando un modificador está activo y se pulsa una tecla (Fn u otra), el
texto insertado en el entry lleva el prefijo del modificador:

```
Ctrl activo + F4  →  inserta "Ctrl+F4"
Alt activo  + F4  →  inserta "Alt+F4"
```

El modificador se consume automáticamente tras la primera pulsación de tecla.
Si se pulsa el mismo modificador otra vez sin haber pulsado ninguna tecla,
se desactiva.

`ModifierState` gestiona el estado de los modificadores. Se instancia
internamente por `FnKeyboard` — no es necesario manejarlo desde fuera.

### Colores de modificadores

Cada modificador tiene un color semántico fijo definido en `MOD_COLORS`:

```python
MOD_COLORS = {
    "Alt":   estilo.cyan,
    "Ctrl":  estilo.orange,
    "Shift": estilo.green,
}
```

Cuando un modificador está **inactivo**, el botón muestra el color del texto
sobre fondo `bg2`. Cuando está **activo**, el fondo se llena con el color
del modificador y el texto se invierte a `bg`.

### Acceso desde VirtualKeyboard

Si se quiere agregar un botón `Fn` en el QWERTY para alternar a `FnKeyboard`,
seguir el mismo patrón que `#@` y `123`:

```python
_btn(sp2, "Fn", 4, e.orange, e,
     self._to_fn).pack(side="left", padx=1)

def _to_fn(self):
    parent = self.master
    self.destroy()
    FnKeyboard(self._estilo, parent, self._entry,
               on_back=lambda: _show_kb(parent, self._estilo,
                                        self._entry, "qwerty")).pack()
```

---

## Patrón recomendado: _show_kb

El helper `_show_kb` es la forma canónica de mostrar o cambiar teclados.
Destruye los hijos del frame contenedor y crea el nuevo widget:

```python
from vista.keyboards import _show_kb

# Mostrar Numpad con botón para volver a QWERTY
_show_kb(self._kb_frame, self.estilo, self._entry, "numpad")

# Mostrar QWERTY
_show_kb(self._kb_frame, self.estilo, self._entry, "qwerty")

# Mostrar FnKeyboard con botón para volver a QWERTY
_show_kb(self._kb_frame, self.estilo, self._entry, "fn")
```

### Integración en un diálogo

```python
class MiDialogo(tk.Toplevel):
    def __init__(self, parent, estilo):
        ...
        self.entry_nombre = tk.Entry(...)
        self.entry_ip     = tk.Entry(...)

        self._kb_frame = tk.Frame(self, bg=estilo.bg)
        self._kb_frame.pack()

        # Campos de texto → QWERTY
        self.entry_nombre.bind(
            "<FocusIn>",
            lambda e: _show_kb(self._kb_frame, self.estilo,
                               self.entry_nombre, "qwerty")
        )

        # Campos numéricos → Numpad
        self.entry_ip.bind(
            "<FocusIn>",
            lambda e: _show_kb(self._kb_frame, self.estilo,
                               self.entry_ip, "numpad")
        )

        # Teclado inicial
        _show_kb(self._kb_frame, self.estilo, self.entry_nombre, "qwerty")
```

---

## Alternancia entre teclados

La alternancia es automática dentro de `VirtualKeyboard`:

- Botón `#@` → reemplaza por `CharKeyboard` con botón `abc` para volver
- Botón `123` → reemplaza por `Numpad` con botón `abc` para volver

Si se instancia `Numpad` directamente (sin pasar por `VirtualKeyboard`),
se puede agregar el botón `abc` pasando `on_back`:

```python
Numpad(estilo, kb_frame, entry,
       on_back=lambda: _show_kb(kb_frame, estilo, entry, "qwerty")).pack()
```

`_show_kb("numpad", ...)` ya incluye este `on_back` automáticamente.

---

## Compatibilidad con sistema de temas

Los teclados reciben `estilo` como primer argumento y usan sus atributos
directamente — son compatibles con el sistema de temas sin configuración
extra.

Como los teclados se destruyen y recrean en cada `_show_kb()`, al recrearse
usan `self.estilo` del diálogo padre, que ya refleja el tema activo gracias
a `apply_estilo()`. **No es necesario etiquetarlos con `etiquetar()`**.

Si el tema cambia mientras el diálogo está abierto, basta con llamar
`_show_kb(...)` otra vez para que el nuevo teclado use los colores actuales.

---

## Usar con campos dentro de un scroll

Si el campo y el teclado están dentro de un canvas con scroll, el
`_kb_frame` debe estar dentro del `scroll_frame`:

```python
# Correcto
self.entry     = tk.Entry(scroll_frame, ...)
self._kb_frame = tk.Frame(scroll_frame, bg=estilo.bg)

# Incorrecto — teclado fuera del scroll
self.entry     = tk.Entry(scroll_frame, ...)
self._kb_frame = tk.Frame(self, bg=estilo.bg)  # self = Toplevel
```

### Patrón: ventana con altura fija y teclado accesible por scroll (opcional)

Útil cuando la ventana tiene altura limitada y el teclado no cabe a la vista.
El header y el footer se mantienen fijos; solo el contenido intermedio scrollea.

```python
class MiVentana(tk.Toplevel):
    def _build_ui(self):
        # ── Header fijo ──────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=estilo.bg)
        hdr.pack(fill="x")
        # ... widgets del header ...

        # ── Área scrollable ──────────────────────────────────────────────
        container = tk.Frame(self, bg=estilo.bg)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=estilo.bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                 command=canvas.yview)

        scroll_frame = tk.Frame(canvas, bg=estilo.bg)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Scroll táctil
        canvas.bind("<Button-1>", lambda e: canvas.scan_mark(e.x, e.y))
        canvas.bind("<B1-Motion>",
                    lambda e: canvas.scan_dragto(e.x, e.y, gain=1))

        # Scroll mouse
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * (e.delta / 120)), "units"))
        canvas.bind_all("<Button-4>",
                        lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",
                        lambda e: canvas.yview_scroll(1, "units"))

        # Campos y teclado dentro del scroll_frame
        self._entry    = tk.Entry(scroll_frame, ...)
        self._kb_frame = tk.Frame(scroll_frame, bg=estilo.bg)
        self._kb_frame.pack(pady=(8, 6))
        _show_kb(self._kb_frame, estilo, self._entry, "numpad")

        # ── Footer fijo ──────────────────────────────────────────────────
        sep = tk.Frame(self, bg=estilo.border, height=1)
        sep.pack(fill="x")
        ftr = tk.Frame(self, bg=estilo.bg)
        ftr.pack(fill="x")
        # ... botones del footer ...
```

La clave es que `header` y `footer` se paquetan directamente en `self`
(el `Toplevel`), mientras que `container` (con el canvas) usa
`expand=True` para ocupar el espacio restante entre ambos.

---

## Agregar teclas al Numpad

La segunda fila del Numpad está definida como una lista de tuplas
`(texto, fg, ancho, comando)` en `_build()`. Para agregar una tecla:

```python
for text, fg, width, cmd in [
    (".",  estilo.white,  3, lambda: self._entry.insert("insert", ".")),
    (":",  estilo.white,  3, lambda: self._entry.insert("insert", ":")),
    ("/",  estilo.white,  3, lambda: self._entry.insert("insert", "/")),
    # Nueva tecla:
    ("-",  estilo.white,  3, lambda: self._entry.insert("insert", "-")),
    ("⌫",  estilo.orange, 3, lambda: _backspace_entry(self._entry)),
    ...
]:
```

## Agregar símbolos al CharKeyboard

Los símbolos están en `CharKeyboard._KEYS` como listas de caracteres:

```python
_KEYS = [
    list("!@#$%^&*()"),
    list("[]{}<>/\\|"),
    list("+=~`"),
    list(".,:;\"'¿?"),
]
```

Para agregar una fila o símbolo, modificar estas listas. Cada botón tiene
ancho fijo de 3 — si el símbolo es muy ancho, ajustar `width` en `_build()`.

---

## Resumen de reglas

- Siempre pasar `estilo` como primer argumento
- Usar `VirtualKeyboard` para texto libre — incluye acceso a símbolos y numpad
- Usar `Numpad` directamente para campos numéricos / IPs
- Usar `FnKeyboard` para teclas de función, modificadores y flechas
- Usar `_show_kb()` para cambiar teclados desde código externo — acepta `"qwerty"`, `"numpad"` y `"fn"`
- Colocar `_kb_frame` dentro del scroll si el diálogo tiene scroll
- No usar `pack_forget` / `pack` con instancias persistentes dentro de scroll
- Los teclados **no necesitan** `etiquetar()` porque se recrean en cada llamada
- `ModifierState` es interno a `FnKeyboard` — no instanciar desde fuera
