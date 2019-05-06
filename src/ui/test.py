from Tkinter import *

window = Tk()
window.title("Energy Grid Management")
lbl = Label(window, text="Hello", font="")
lbl.grid(column=0, row=0)
btn = Button(window, text="Click Me")
btn.grid(column=1, row=0)
window.geometry('350x200')
window.mainloop()
