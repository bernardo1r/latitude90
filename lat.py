import tkinter
from view import draw
from model import game_rules

top = tkinter.Tk()

cnv = tkinter.Canvas(top, height=724, width=720)
cnv.pack()

cnv.bind('<ButtonRelease-1>', draw.click)

game_rules.inicia_jogo(4, True)
draw.inicia_tabuleiro(cnv)

top.mainloop()
