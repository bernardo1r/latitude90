import tkinter
from view import draw
from controller import event_handler

top = tkinter.Tk()
top.title("Latitude 90º")

cnv = tkinter.Canvas(top, height=724, width=720)
cnv.pack()

cnv.bind('<ButtonRelease-1>', event_handler.click)

event_handler.set_root(top)
event_handler.set_canvas(cnv)
draw.tela_inicial(cnv)

top.mainloop()
