import tkinter as tk
from tkinter import messagebox, ttk
import math
import cmath
import re

class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Científica Avanzada")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")

        self.expression = ""
        self.history = []
        self.angle_mode = "rad"  # rad o deg
        self.last_result = None

        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10), padding=5)
        self.style.configure("TLabel", font=("Arial", 12), background="#2c3e50", foreground="white")

        # Crear widgets
        self.create_widgets()

        # Atajos de teclado
        self.root.bind("<Return>", lambda event: self.calculate_result())
        self.root.bind("<BackSpace>", lambda event: self.backspace())
        self.root.bind("<Escape>", lambda event: self.clear())

    def create_widgets(self):
        # Frame para pantalla y botones superiores
        top_frame = tk.Frame(self.root, bg="#2c3e50")
        top_frame.pack(pady=10)

        # Pantalla de entrada
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(top_frame, textvariable=self.entry_var, font=("Arial", 18), justify="right", bd=10, relief=tk.GROOVE, width=30)
        self.entry.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

        # Botones de modo y constantes
        self.mode_btn = tk.Button(top_frame, text="Modo: RAD", command=self.toggle_mode, bg="#e67e22", fg="white", font=("Arial", 10))
        self.mode_btn.grid(row=1, column=0, padx=2, pady=2)
        constants = [("π", "math.pi"), ("e", "math.e")]
        for i, (text, value) in enumerate(constants):
            btn = tk.Button(top_frame, text=text, command=lambda v=value: self.append_constant(v), bg="#3498db", fg="white", font=("Arial", 10))
            btn.grid(row=1, column=i+1, padx=2, pady=2)

        # Botones principales (operaciones básicas)
        buttons = [
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3),
            ('0', 5, 0), ('.', 5, 1), ('=', 5, 2), ('+', 5, 3),
            ('C', 6, 0), ('⌫', 6, 1), ('(', 6, 2), (')', 6, 3),
        ]

        for (text, row, col) in buttons:
            if text == '=':
                btn = tk.Button(top_frame, text=text, command=self.calculate_result, bg="#2ecc71", fg="white", font=("Arial", 12))
            elif text in ('C', '⌫'):
                btn = tk.Button(top_frame, text=text, command=self.clear if text == 'C' else self.backspace, bg="#e74c3c", fg="white")
            else:
                btn = tk.Button(top_frame, text=text, command=lambda t=text: self.append(t), bg="#ecf0f1", font=("Arial", 12))
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2, ipadx=10, ipady=10)

        # Frame para funciones científicas
        sci_frame = tk.LabelFrame(self.root, text="Funciones Científicas", bg="#2c3e50", fg="white", font=("Arial", 10, "bold"))
        sci_frame.pack(pady=10, fill="x", padx=10)

        functions = [
            ("sin", "math.sin"), ("cos", "math.cos"), ("tan", "math.tan"),
            ("asin", "math.asin"), ("acos", "math.acos"), ("atan", "math.atan"),
            ("log", "math.log10"), ("ln", "math.log"), ("√", "math.sqrt"),
            ("x²", "**2"), ("x³", "**3"), ("xʸ", "**"),
            ("eˣ", "math.exp"), ("10ˣ", "lambda x: 10**x"), ("|x|", "abs")
        ]

        row, col = 0, 0
        for text, func in functions:
            btn = tk.Button(sci_frame, text=text, command=lambda f=func, t=text: self.apply_function(f, t), bg="#9b59b6", fg="white", width=8)
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 4:
                col = 0
                row += 1

        # Botón de historial
        self.history_btn = tk.Button(self.root, text="📜 Historial", command=self.show_history, bg="#f1c40f", fg="black")
        self.history_btn.pack(pady=5)

        # Label para mostrar último resultado
        self.result_label = tk.Label(self.root, text="", bg="#2c3e50", fg="#f39c12", font=("Arial", 10))
        self.result_label.pack()

        # Ajustar grid
        for i in range(7):
            top_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            top_frame.grid_columnconfigure(i, weight=1)

    def append(self, char):
        self.expression += char
        self.entry_var.set(self.expression)

    def append_constant(self, const_value):
        try:
            value = eval(const_value)
            self.expression += str(value)
            self.entry_var.set(self.expression)
        except:
            pass

    def backspace(self):
        self.expression = self.expression[:-1]
        self.entry_var.set(self.expression)

    def clear(self):
        self.expression = ""
        self.entry_var.set("")
        self.result_label.config(text="")

    def apply_function(self, func_name, display_name):
        try:
            if not self.expression:
                if self.last_result is not None:
                    self.expression = str(self.last_result)
                else:
                    return

            # Manejo especial para xʸ
            if display_name == "xʸ":
                self.expression += "**"
                self.entry_var.set(self.expression)
                return

            # Evaluar expresión actual
            value = self.evaluate_expression(self.expression)

            # Convertir ángulo si es necesario
            if any(x in func_name for x in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']):
                if self.angle_mode == "deg" and 'a' not in func_name:  # trig directa
                    value = math.radians(value)
                elif self.angle_mode == "deg" and 'a' in func_name:  # inversa
                    value = math.degrees(value) if func_name != 'atan' else value

            # Aplicar función
            if callable(func_name):
                result = func_name(value)
            else:
                # Para funciones como "**2"
                if display_name == "x²":
                    result = value ** 2
                elif display_name == "x³":
                    result = value ** 3
                elif display_name == "10ˣ":
                    result = 10 ** value
                else:
                    result = eval(func_name)(value)

            self.last_result = result
            self.expression = str(result)
            self.entry_var.set(self.expression)
            self.result_label.config(text=f"= {result}")
            self.add_to_history(f"{display_name}({value}) = {result}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la función: {str(e)}")

    def evaluate_expression(self, expr):
        """Evalúa una expresión matemática de forma segura"""
        # Reemplazar ^ por **
        expr = expr.replace('^', '**')
        # Permitir solo caracteres seguros
        allowed_chars = set("0123456789+-*/(). %**")
        if not all(c in allowed_chars or c.isalpha() for c in expr):
            raise ValueError("Caracteres no permitidos")
        try:
            # Usar eval con restricciones
            return eval(expr, {"__builtins__": None}, {"math": math, "cmath": cmath, "abs": abs})
        except:
            raise

    def calculate_result(self):
        try:
            result = self.evaluate_expression(self.expression)
            self.last_result = result
            self.add_to_history(f"{self.expression} = {result}")
            self.expression = str(result)
            self.entry_var.set(self.expression)
            self.result_label.config(text=f"= {result}")
        except ZeroDivisionError:
            messagebox.showerror("Error", "División entre cero")
            self.clear()
        except Exception as e:
            messagebox.showerror("Error", f"Expresión inválida: {str(e)}")
            self.clear()

    def toggle_mode(self):
        self.angle_mode = "deg" if self.angle_mode == "rad" else "rad"
        self.mode_btn.config(text=f"Modo: {self.angle_mode.upper()}")
        messagebox.showinfo("Modo cambiado", f"Modo angular: {self.angle_mode.upper()}")

    def add_to_history(self, entry):
        self.history.append(entry)
        if len(self.history) > 50:
            self.history.pop(0)

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Historial de cálculos")
        history_window.geometry("400x300")
        history_window.configure(bg="#34495e")

        listbox = tk.Listbox(history_window, font=("Courier", 10), bg="#ecf0f1")
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for item in reversed(self.history):
            listbox.insert(tk.END, item)

        btn_close = tk.Button(history_window, text="Cerrar", command=history_window.destroy, bg="#e74c3c", fg="white")
        btn_close.pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()