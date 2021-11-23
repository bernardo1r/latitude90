import tkinter
import math
import copy
from model import game_rules
from PIL import Image, ImageTk

__all__ = ["checa_casa", "carrega_dados"]

fronteiras = []
colors = ["green", "yellow", "black", "blue"]
img_tab = None
canvas_obj = {}
grossura_borda = 2
c_x = 197
c_y = 367
meio_x = 364
dados = []
canv_dados = []

def faz_pos_rel(x, y, c_x, c_y):
    return x-c_x, -(y-c_y)

def diminui_vetor(x, y, n_mod):
    mag = math.sqrt(x*x + y*y)
        
    new_x = x*n_mod/mag
    new_y = y*n_mod/mag

    return new_x, new_y

def rotaciona_vetor(x, y, theta):
    x_new = x*math.cos(theta) - y*math.sin(theta)
    y_new = x*math.sin(theta) + y*math.cos(theta)

    return x_new, y_new

def produto_vetorial(a, b):
    return a[0]*b[1] - a[1]*b[0]

def subtrai_vetor(x1, y1, x2, y2):
    return x1-x2, y1-y2

def checa_casa_trapezio(obj, x, y):
    a_x = obj["front"]["a"]["x"]
    a_y = obj["front"]["a"]["y"]
    b_x = obj["front"]["b"]["x"]
    b_y = obj["front"]["b"]["y"]
    c_x = obj["front"]["c"]["x"]
    c_y = obj["front"]["c"]["y"]
    d_x = obj["front"]["d"]["x"]
    d_y = obj["front"]["d"]["y"]


    p_a = subtrai_vetor(x, y, a_x, a_y)
    b_a = subtrai_vetor(b_x, b_y, a_x, a_y)
    p_d = subtrai_vetor(x, y, d_x, d_y)
    c_d = subtrai_vetor(c_x, c_y, d_x, d_y)

    d_a = subtrai_vetor(d_x, d_y, a_x, a_y)
    p_b = subtrai_vetor(x, y, b_x, b_y)
    c_b = subtrai_vetor(c_x, c_y, b_x, b_y)

    if produto_vetorial(p_a, b_a) * produto_vetorial(p_d, c_d) <= 0 and \
       produto_vetorial(p_a, d_a) * produto_vetorial(p_b, c_b) <= 0:
        #dentro
        return True

    return False


def checa_casa_polo(obj, x, y):
    r = obj["front"]["circ"]["r"]
    c_x = obj["front"]["circ"]["x"]
    c_y = obj["front"]["circ"]["y"]

    if r**2 - ((c_x - x)**2 + (c_y - y)**2) >= 0:
        if x >= obj["front"]["lines"][0] and x <= obj["front"]["lines"][1]:
            return True

    return False
    

def faz_fronteiras_polo():
    global fronteiras, c_x, c_y
    
    setor = {}
    setor["front"] = {"tipo": "polo", "circ": {"x": 0, "y": 0, "r": 34}, "lines": [169-c_x, 229-c_x]}
    setor["game_coords"] = {"x": 6, "y": 12}

    fronteiras.append(setor)

def faz_fronteiras_trapezio(grossura_borda):
    global fronterias, c_x, c_y

    setor1 = {}
    setor1["front"] = {"tipo": "trapezio", "a": {"x": 35, "y": 367}, "b": {"x": 34, "y": 276}, "c": {"x": 52, "y": 287}, "d": {"x": 53, "y": 367}}
    setor1["game_coords"] = {"x": 0, "y": 0}
    setor2 = {}
    setor2["front"] = {"tipo": "trapezio", "a": {"x": 35, "y": 461}, "b": {"x": 35, "y": 370}, "c": {"x": 53, "y": 370}, "d": {"x": 53, "y": 450}}
    setor2["game_coords"] = {"x": 0, "y": 11}
    #coordenadas relativas ao centro do hemisfério AB e CD são bases e AD e BC são lados
    #setor1 é o trapezio com lado mais externo vermelho e setor2 o com o lado mais externo laranja
    
    altura_casa_horizontal = 19
    raio_maior_horizontal = 163

    altura_casa_inclinado = 24
    raio_maior_inclinado = 191
    for setor in [setor1, setor2]:
        for v in ["a", "b", "c", "d"]:
            setor["front"][v]["x"], setor["front"][v]["y"] = faz_pos_rel(setor["front"][v]["x"], setor["front"][v]["y"], c_x, c_y)

    for _ in range(6):
        #latitude em latitude até os polos
        for l in range(2):
            #longitude em longitude não conectadas

            if l == 0:
                setor1["game_coords"]["y"] = 0
                setor2["game_coords"]["y"] = 11

            else:
                setor1["game_coords"]["y"] = 6
                setor2["game_coords"]["y"] = 5

            for setor in [setor1, setor2]:
                fronteiras.append(copy.deepcopy(setor))
                
                for v in ["a", "b", "c", "d"]:
                    #espelhas as coordenadas
                    setor["front"][v]["x"] *= -1
                    setor["front"][v]["y"] *= -1

        setor1["game_coords"]["x"] += 1
        setor2["game_coords"]["x"] += 1


        raio_maior_inclinado -= altura_casa_inclinado + grossura_borda
        raio_maior_horizontal -= altura_casa_horizontal + grossura_borda

        raio_menor_inclinado = raio_maior_inclinado  - altura_casa_inclinado
        raio_menor_horizontal = raio_maior_horizontal - altura_casa_horizontal

        #reduz os vetores para ficar com a nova modulo
        setor1["front"]["a"]["x"], setor1["front"]["a"]["y"] = diminui_vetor(setor1["front"]["a"]["x"], setor1["front"]["a"]["y"], raio_maior_horizontal)
        setor1["front"]["b"]["x"], setor1["front"]["b"]["y"] = diminui_vetor(setor1["front"]["b"]["x"], setor1["front"]["b"]["y"], raio_maior_inclinado)
        setor1["front"]["c"]["x"], setor1["front"]["c"]["y"] = diminui_vetor(setor1["front"]["c"]["x"], setor1["front"]["c"]["y"], raio_menor_inclinado)
        setor1["front"]["d"]["x"], setor1["front"]["d"]["y"] = diminui_vetor(setor1["front"]["d"]["x"], setor1["front"]["d"]["y"], raio_menor_horizontal)

        setor2["front"]["a"]["x"], setor2["front"]["a"]["y"] = diminui_vetor(setor2["front"]["a"]["x"], setor2["front"]["a"]["y"], raio_maior_inclinado)
        setor2["front"]["b"]["x"], setor2["front"]["b"]["y"] = diminui_vetor(setor2["front"]["b"]["x"], setor2["front"]["b"]["y"], raio_maior_horizontal)
        setor2["front"]["c"]["x"], setor2["front"]["c"]["y"] = diminui_vetor(setor2["front"]["c"]["x"], setor2["front"]["c"]["y"], raio_menor_horizontal)
        setor2["front"]["d"]["x"], setor2["front"]["d"]["y"] = diminui_vetor(setor2["front"]["d"]["x"], setor2["front"]["d"]["y"], raio_menor_inclinado)




def faz_fronteiras_circulares(grossura_borda):
    global fronteiras, c_x, c_y
    
    setor = {}
    setor["front"] = {"tipo": "circular", "v_fim": {"x": 33-c_x, "y": -(272-c_y)}, "v_inicio": {"x": 99-c_x, "y": -(203-c_y)}}
    setor["game_coords"] = {"x": 0, "y": 1}
    #coordenadas relativas ao centro do hemisfério com sentido dos eixos (x positivo para direita, y positivo para cima)


    altura_casa = 24
    raio_maior = 191
    for _ in range(6):
        #latitude em latitude
        raio_menor = raio_maior - altura_casa
        setor["front"]["r_maior"] = raio_maior
        setor["front"]["r_menor"] = raio_menor
    
        for _ in range(2):
            #setor circulares conectados na mesma latitude
            for _ in range(4):
                #longitude em longitude
                fronteiras.append(copy.deepcopy(setor))

                setor["game_coords"]["y"] += 1
                for v in ["v_fim", "v_inicio"]:
                    #rotaciona os vetores 30 graus
                    setor["front"][v]["x"], setor["front"][v]["y"] = rotaciona_vetor(setor["front"][v]["x"], setor["front"][v]["y"], -math.pi/6)

            setor["game_coords"]["y"] += 2
            for v in ["v_fim", "v_inicio"]:
                #rotaciona os vetores 60 graus
                setor["front"][v]["x"], setor["front"][v]["y"] = rotaciona_vetor(setor["front"][v]["x"], setor["front"][v]["y"], -math.pi/3)

        setor["game_coords"]["x"] += 1
        setor["game_coords"]["y"] = 1
    
        raio_maior -= altura_casa + grossura_borda
    
        for v in ["v_fim", "v_inicio"]:
            #reduz o vetor para ficar com a nova modulo
            setor["front"][v]["x"], setor["front"][v]["y"] = diminui_vetor(setor["front"][v]["x"], setor["front"][v]["y"], raio_maior)

            

def faz_fronteiras():
    global fronteiras, grossura_borda, c_x, c_y

    fronteiras = []

    faz_fronteiras_circulares(grossura_borda)
    faz_fronteiras_trapezio(grossura_borda)
    faz_fronteiras_polo()
            
                
    
def checa_casa_circular(obj, x, y):
    v_inicio = obj["front"]["v_inicio"]
    v_fim = obj["front"]["v_fim"]
    r_maior = obj["front"]["r_maior"]
    r_menor = obj["front"]["r_menor"]

    dist_quad = x*x + y*y
    
    if not checa_clockwise(x, y, v_inicio["x"], v_inicio["y"]) and \
    checa_clockwise(x, y, v_fim["x"], v_fim["y"]) and \
    dist_quad < r_maior*r_maior and dist_quad > r_menor*r_menor:
        #esta dentro da casa
        return True
    
    return False


def checa_casa(x, y):
    global c_x, c_y, meio_x


    if x > meio_x:
        c_x_buf = c_x + 333
        z = 1
    else:
        c_x_buf = c_x
        z = 0

    x, y = faz_pos_rel(x, y, c_x_buf, c_y)

    for casa in fronteiras:
        if casa["front"]["tipo"] == "trapezio":
            if checa_casa_trapezio(casa, x, y):
                return casa["game_coords"]["x"], casa["game_coords"]["y"], z

        elif casa["front"]["tipo"] == "circular":
            if checa_casa_circular(casa, x, y):
                return casa["game_coords"]["x"], casa["game_coords"]["y"], z

        elif casa["front"]["tipo"] == "polo":
            if checa_casa_polo(casa, x, y):
                return casa["game_coords"]["x"], casa["game_coords"]["y"], z
            
        else:
            return False

    return False

def checa_clockwise(x, y, borda_x, borda_y):
    if borda_y*x - borda_x*y > 0:
        return True
    return False


def click(event):
    global casas
    c_y = 367
    if event.x > 364:
        c_x = 530
    else:
        c_x = 197
    print(event.x, event.y)

    coords = checa_casa(event.x, event.y)
    if coords:
        print(f"{coords[0]}, {coords[1]}, {coords[2]}")

def carrega_dados():
    global dados

    for i in range(6):
        img_dado = Image.open(f"./view/imgs/Dado{i+1}.png")
        img_dado = img_dado.resize((80, 80), Image.ANTIALIAS)
        img_dado = ImageTk.PhotoImage(image=img_dado)

        dados.append(img_dado)

def exibe_dado(canvas):
    global colors, canv_dados, dados

    for fundo, dado in canv_dados:
        canvas.delete(fundo)
        canvas.delete(dado)


    vez = game_rules.get_vez()
    color_v = colors[vez]

    d = game_rules.get_dados()

    for i in range(2):
        print((i*10+i*100))
        canv_dados.append([canvas.create_rectangle(5+(i*5+i*100), 617, 105+(i*5+i*100), 717, fill=color_v, outline=color_v),
                           canvas.create_image(15+(i*5+i*100), 627, anchor=tkinter.NW, image=dados[d[i]-1])])


def inicia_tabuleiro(canvas):
    global img_tab
    
    img_tab = tkinter.PhotoImage(file="./view/imgs/Latitude90-Tabuleiro.png")
    canvas.create_image(0, 0, anchor=tkinter.NW, image=img_tab)

    faz_fronteiras()
    carrega_dados()

    exibe_dado(canvas)
    
    

    '''for i in range(720):
        print(i)
        for j in range(724):
            if checa_casa(i, j):
                canvas.create_rectangle(i, j, i, j, outline="red")'''

