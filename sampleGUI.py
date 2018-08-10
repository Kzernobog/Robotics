import tkinter as tk
from tkinter import ttk
win = tk.Tk()
win.title("Sample")
tabcontrol = ttk.Notebook(win)
tab1 = ttk.Frame(tabcontrol)
tabcontrol.add(tab1, text='Tab 1')
tab2 = ttk.Frame(tabcontrol)
tabcontrol.add(tab2, text='Tab2')
tabcontrol.pack(expand=1, fill='both')

# main loop
win.mainloop()
