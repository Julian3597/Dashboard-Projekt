import tkinter as tk
from dataclasses import dataclass


# Views

class ViewContainer(tk.Frame):
    def __init__(self):
            super().__init__()
            self.label1 = tk.Label(self, text="Label 1")
            self.label1.pack()
            self.vA = ViewA()
            self.vA.pack()

class ViewA(tk.Frame):
    def __init__(self):
        super().__init__()
        tk.Button(
            self,
        text="Test",
        command=lambda: print("test")
        ).pack()




app = ViewContainer()
app.pack(fill="both", expand=True)

app.mainloop()