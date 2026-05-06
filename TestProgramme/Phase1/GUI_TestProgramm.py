from tkinter import *
from tkinter import ttk
import random

root = Tk()
frm = ttk.Frame(root, padding=10)
label_var = StringVar()
randomNumberLabel = ttk.Label(root, textvariable=label_var, font=("Arial", 24))
randomNumberLabel.pack(padx=20, pady=20)
def update_number():
    label_var.set(random.randint(1, 10))
    root.after(2000, update_number)

update_number()
root.mainloop()