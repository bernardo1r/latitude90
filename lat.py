import tkinter
from tkinter.constants import E
from model import game_rules
from view import draw
from controller import event_handler
top = tkinter.Tk()

cnv = tkinter.Canvas(top, height=724, width=720)
cnv.pack()

cnv.bind('<ButtonRelease-1>', event_handler.click)

event_handler.set_root(top)
event_handler.set_canvas(cnv)
draw.tela_inicial(cnv)

top.mainloop()
