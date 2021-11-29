from os import remove
import tkinter
import math
import copy
from tkinter.constants import ANCHOR
from model import game_rules
from controller import event_handler
from PIL import Image, ImageTk
from tkinter import ttk

__all__ = ["checa_casa", "carrega_dados", "get_meio_x"]

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
n_jogadores = 0
modo_dupla = False
raio_explorador = 10
telas = []
dado_combo = []
dado_button = None
canv_dado_colorido = None
dado_colorido = None
dado_colorido_button = None
dado_colorido_combo = None

canvas = None


def faz_pos_rel(x, y, c_x, c_y):
    return x-c_x, -(y-c_y)

def faz_pos_abs(x, y, z):
    global c_x, c_y, meio_x

    x_buff = c_x
    if z > 0:
        x_buff += 333

    return x+x_buff, (-y)+c_y

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
    setor["front"]["pos_jogadores"] = [{"x": -15, "y": 0}, {"x": 20, "y": 0}]
    setor["game_coords"] = {"x": 6, "y": 12}

    fronteiras.append(setor)

def faz_base_media_trapezio(obj):
    base_ab_2 = (obj["front"]["a"]["x"]-obj["front"]["b"]["x"])**2 + (obj["front"]["a"]["y"]-obj["front"]["b"]["y"])**2
    base_cd_2 = (obj["front"]["c"]["x"]-obj["front"]["d"]["x"])**2 + (obj["front"]["c"]["y"]-obj["front"]["d"]["y"])**2

    base_med_2 = (base_ab_2 + base_cd_2) / 2

    return math.sqrt(base_med_2)

def faz_fronteiras_trapezio(grossura_borda):
    global fronterias, c_x, c_y

    setor1 = {}
    setor1["front"] = {"tipo": "trapezio", "a": {"x": 35, "y": 367}, "b": {"x": 34, "y": 276}, "c": {"x": 52, "y": 287}, "d": {"x": 53, "y": 367}}
    setor1["game_coords"] = {"x": 0, "y": 0}
    setor1["front"]["pos_jogadores"] = [{},{}]

    vet_setor1 = {"x": 44, "y": 366}


    setor2 = {}
    setor2["front"] = {"tipo": "trapezio", "a": {"x": 35, "y": 461}, "b": {"x": 35, "y": 370}, "c": {"x": 53, "y": 370}, "d": {"x": 53, "y": 450}}
    setor2["game_coords"] = {"x": 0, "y": 11}
    setor2["front"]["pos_jogadores"] = [{},{}]
    
    vet_setor2 = {"x": 44, "y": 371}
    #coordenadas relativas ao centro do hemisfério AB e CD são bases e AD e BC são lados
    #setor1 é o trapezio com lado mais externo vermelho e setor2 o com o lado mais externo laranja
    
    altura_casa_horizontal = 20
    raio_maior_horizontal = 163

    altura_casa_inclinado = 24
    raio_maior_inclinado = 191

    for setor in [setor1, setor2]:
        for v in ["a", "b", "c", "d"]:
            setor["front"][v]["x"], setor["front"][v]["y"] = faz_pos_rel(setor["front"][v]["x"], setor["front"][v]["y"], c_x, c_y)

    for v in [vet_setor1, vet_setor2]:
        v["x"], v["y"] = faz_pos_rel(v["x"], v["y"], c_x, c_y)

    for _ in range(6):
        #latitude em latitude até os polos
        for l in range(2):
            #longitude em longitude não conectadas

            #define posicao dos jogadores no trapezio
            base_media = faz_base_media_trapezio(setor1)
            setor1["front"]["pos_jogadores"] = [{**vet_setor1}, {**vet_setor1}]
            setor2["front"]["pos_jogadores"] = [{**vet_setor2}, {**vet_setor2}]

            if l == 0:
                for i in range(2):
                    setor1["front"]["pos_jogadores"][i]["y"] += base_media/4 + i*base_media/2
                    setor2["front"]["pos_jogadores"][i]["y"] -= base_media/4 + i*base_media/2

            else:
                for i in range(2):
                    setor1["front"]["pos_jogadores"][i]["y"] -= base_media/4 + i*base_media/2
                    setor2["front"]["pos_jogadores"][i]["y"] += base_media/4 + i*base_media/2
                

            if l == 0:
                setor1["game_coords"]["y"] = 0
                setor2["game_coords"]["y"] = 11

            else:
                setor1["game_coords"]["y"] = 6
                setor2["game_coords"]["y"] = 5


            for setor in [setor1, setor2]:
                fronteiras.append(copy.deepcopy(setor))
                
                #espelhas as coordenadas
                for v in ["a", "b", "c", "d"]: 
                    setor["front"][v]["x"] *= -1
                    setor["front"][v]["y"] *= -1

            for v in [vet_setor1, vet_setor2]:
                v["x"] *= -1
                v["y"] *= -1

        setor1["game_coords"]["x"] += 1
        setor2["game_coords"]["x"] += 1


        raio_maior_inclinado -= altura_casa_inclinado + grossura_borda
        raio_maior_horizontal -= altura_casa_horizontal + grossura_borda

        raio_menor_inclinado = raio_maior_inclinado   - altura_casa_inclinado
        raio_menor_horizontal = raio_maior_horizontal - altura_casa_horizontal

        raio_meio_horizontal = raio_maior_horizontal - (altura_casa_horizontal/2)


        #reduz os vetores para ficar com a nova modulo
        setor1["front"]["a"]["x"], setor1["front"]["a"]["y"] = diminui_vetor(setor1["front"]["a"]["x"], setor1["front"]["a"]["y"], raio_maior_horizontal)
        setor1["front"]["b"]["x"], setor1["front"]["b"]["y"] = diminui_vetor(setor1["front"]["b"]["x"], setor1["front"]["b"]["y"], raio_maior_inclinado)
        setor1["front"]["c"]["x"], setor1["front"]["c"]["y"] = diminui_vetor(setor1["front"]["c"]["x"], setor1["front"]["c"]["y"], raio_menor_inclinado)
        setor1["front"]["d"]["x"], setor1["front"]["d"]["y"] = diminui_vetor(setor1["front"]["d"]["x"], setor1["front"]["d"]["y"], raio_menor_horizontal)
        vet_setor1["x"], vet_setor1["y"] = diminui_vetor(vet_setor1["x"], vet_setor1["y"], raio_meio_horizontal) 

        setor2["front"]["a"]["x"], setor2["front"]["a"]["y"] = diminui_vetor(setor2["front"]["a"]["x"], setor2["front"]["a"]["y"], raio_maior_inclinado)
        setor2["front"]["b"]["x"], setor2["front"]["b"]["y"] = diminui_vetor(setor2["front"]["b"]["x"], setor2["front"]["b"]["y"], raio_maior_horizontal)
        setor2["front"]["c"]["x"], setor2["front"]["c"]["y"] = diminui_vetor(setor2["front"]["c"]["x"], setor2["front"]["c"]["y"], raio_menor_horizontal)
        setor2["front"]["d"]["x"], setor2["front"]["d"]["y"] = diminui_vetor(setor2["front"]["d"]["x"], setor2["front"]["d"]["y"], raio_menor_inclinado)
        vet_setor2["x"], vet_setor2["y"] = diminui_vetor(vet_setor2["x"], vet_setor2["y"], raio_meio_horizontal) 


def faz_fronteiras_circulares(grossura_borda):
    global fronteiras, c_x, c_y
    
    setor = {}
    setor["front"] = {"tipo": "circular", "v_fim": {"x": 33-c_x, "y": -(272-c_y)}, "v_inicio": {"x": 99-c_x, "y": -(203-c_y)}}
    setor["game_coords"] = {"x": 0, "y": 1}
    #coordenadas relativas ao centro do hemisfério com sentido dos eixos (x positivo para direita, y positivo para cima)

    setor["front"]["pos_jogadores"] = []
    setor["front"]["pos_jogadores"].append({"x": 43-c_x, "y": -(277-c_y)})
    setor["front"]["pos_jogadores"].append({"x": 43-c_x, "y": -(277-c_y)})

    #rotaciona o vetor 7.5 graus
    setor["front"]["pos_jogadores"][0]["x"], setor["front"]["pos_jogadores"][0]["y"] = rotaciona_vetor(setor["front"]["pos_jogadores"][0]["x"], 
                                                                                                       setor["front"]["pos_jogadores"][0]["y"],
                                                                                                       -math.pi/24)
    #rotaciona o vetor 22.5 graus
    setor["front"]["pos_jogadores"][1]["x"], setor["front"]["pos_jogadores"][1]["y"] = rotaciona_vetor(setor["front"]["pos_jogadores"][1]["x"], 
                                                                                                       setor["front"]["pos_jogadores"][1]["y"],
                                                                                                       (-math.pi/24)+(-math.pi/12))                                                                                                                                                                                                                              

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

                #rotaciona os vetores 30 graus
                for v in [setor["front"]["v_fim"], setor["front"]["v_inicio"], setor["front"]["pos_jogadores"][0], setor["front"]["pos_jogadores"][1]]:
                    v["x"], v["y"] = rotaciona_vetor(v["x"], v["y"], -math.pi/6)

            setor["game_coords"]["y"] += 2

            #rotaciona os vetores 60 graus
            for v in [setor["front"]["v_fim"], setor["front"]["v_inicio"], setor["front"]["pos_jogadores"][0], setor["front"]["pos_jogadores"][1]]:
                v["x"], v["y"] = rotaciona_vetor(v["x"], v["y"], -math.pi/3)

        setor["game_coords"]["x"] += 1
        setor["game_coords"]["y"] = 1
    
        raio_maior -= altura_casa + grossura_borda
        raio_meio = raio_maior - (altura_casa/2)
    
        #reduz os vetor para ficarem com novos modulos
        for v in [setor["front"]["v_fim"], setor["front"]["v_inicio"]]:
            v["x"], v["y"] = diminui_vetor(v["x"], v["y"], raio_maior)

        for v in [setor["front"]["pos_jogadores"][0], setor["front"]["pos_jogadores"][1]]:
            v["x"], v["y"] = diminui_vetor(v["x"], v["y"], raio_meio)
            

def faz_fronteiras():
    global fronteiras, grossura_borda, c_x, c_y

    fronteiras = []

    faz_fronteiras_circulares(grossura_borda)
    faz_fronteiras_trapezio(grossura_borda)
    faz_fronteiras_polo()

    for casa in fronteiras:
        casa["canv_obj"] = [[], []]
            
                
    
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

def get_casa(x, y):
    #função recebe coordenadas do tabuleiro conforme game_rules e retorna a casa com essas coordenadas
    global fronteiras

    for casa in fronteiras:
        if casa["game_coords"]["x"] == x and casa["game_coords"]["y"] == y:
            return casa

    return False

def checa_casa(x, y):
    global c_x, c_y, meio_x, fronteiras


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
                return casa

        elif casa["front"]["tipo"] == "circular":
            if checa_casa_circular(casa, x, y):
                return casa

        elif casa["front"]["tipo"] == "polo":
            if checa_casa_polo(casa, x, y):
                return casa
            
        else:
            return False

    return False
                    

def checa_clockwise(x, y, borda_x, borda_y):
    if borda_y*x - borda_x*y > 0:
        return True
    return False
    
        
def remove_dado(idx):
    global canvas, canv_dados, dados_coord

    canvas.delete(canv_dados[idx][1])
    canvas.delete(canv_dados[idx][2])
        
    canv_dados.pop(idx)

    if idx == 0 and len(canv_dados) > 0:
        #coloca o dado mais a direita na esquerda
        global colors 

        canvas.delete(canv_dados[0][1])
        canvas.delete(canv_dados[0][2])

        vez = game_rules.get_vez()
        color_v = colors[vez]

        f_x = dados_coord[0]["fundo"]["x"]
        f_y = dados_coord[0]["fundo"]["y"]
        f_lado = dados_coord[0]["fundo_lado"]

        d_x = dados_coord[0]["img"]["x"]
        d_y = dados_coord[0]["img"]["y"]

        canv_dados[0][1] = canvas.create_rectangle(f_x, f_y, f_x + f_lado, f_y + f_lado, fill=color_v, outline=color_v)
        canv_dados[0][2] = canvas.create_image(d_x, d_y, anchor=tkinter.NW, image=dados[canv_dados[0][0]-1])



def carrega_dados():
    global dados, dados_coord, dado_colorido

    dados_coord = [{"fundo": {"x": 5, "y": 617}, "fundo_lado": 100, "img": {"x": 15, "y": 627}},
                   {"fundo": {"x": 110, "y": 617}, "fundo_lado": 100, "img": {"x": 120, "y": 627}}]

    for i in range(6):
        img_dado = Image.open(f"./view/imgs/Dado{i+1}.png")
        img_dado = img_dado.resize((80, 80), Image.ANTIALIAS)
        img_dado = ImageTk.PhotoImage(image=img_dado)

        dados.append(img_dado)

    dado_colorido = tkinter.PhotoImage(file="./view/imgs/dado_colorido_nada.png")

def limpa_dados():
    global canv_dados, canvas

    for dado in canv_dados:
        canvas.delete(dado[1])
        canvas.delete(dado[2])
        remove_dado(0)

def lanca_dados():
    global dado_combo

    game_rules.define_dados(dado_combo[0].get(), dado_combo[1].get())

    exibe_dado()

def lanca_dado_colorido():
    global dado_colorido_combo

    cor = dado_colorido_combo.get()
    if cor != "nada":
        cor = int(cor) - 1

    limpa_dado_colorido()
    exibe_dado_colorido(cor)

def exibe_dado_colorido(cor=None):
    global colors, canvas, canv_dado_colorido, dado_colorido_combo, dado_colorido_button, dado_colorido

    limpa_dado_colorido()

    if cor == None:
        cor = game_rules.lanca_dado_colorido()

    elif cor == "nada":
        cor = None

    njogadores = game_rules.get_njogadores()


    if cor != None and cor < njogadores:
        canv_dado_colorido = (cor, canvas.create_rectangle(615, 619, 714, 718, fill=colors[cor], outline=colors[cor]))

    else:
        canv_dado_colorido = (cor, canvas.create_image(615, 619, anchor=tkinter.NW, image=dado_colorido))

    dado_colorido_combo = ttk.Combobox(canvas, state="readonly", width=10, height=10, values=("nada", "1", "2", "3", "4"))
    dado_colorido_combo.place(x=612, y=665, anchor=tkinter.NE)
    dado_colorido_combo.current(0)


    dado_colorido_button = tkinter.Button(canvas, text="lançar dados", command=lanca_dado_colorido)
    dado_colorido_button.place(x=610, y = 690, anchor=tkinter.NE)

def limpa_dado_colorido():
    global canvas, canv_dado_colorido, dado_colorido_button, dado_colorido_combo

    if canv_dado_colorido:
        canvas.delete(canv_dado_colorido[1])
        canv_dado_colorido = None

        dado_colorido_combo.destroy()
        dado_colorido_button.destroy()

def get_dado_colorido():
    global canv_dado_colorido

    return canv_dado_colorido

def exibe_dado(trocar_dado_colorido=False):
    global colors, canv_dados, dados, dados_coord, canvas

    limpa_dados()
    limpa_dado_colorido()

    canv_dados = []

    vez = game_rules.get_vez()
    color_v = colors[vez]

    d = game_rules.get_dados()

    if not trocar_dado_colorido and d[0] == d[1]:
        exibe_dado_colorido()

    i = 0
    for info in dados_coord:
        f_x = info["fundo"]["x"]
        f_y = info["fundo"]["y"]
        f_lado = info["fundo_lado"]

        d_x = info["img"]["x"]
        d_y = info["img"]["y"]

        canv_dados.append([d[i], canvas.create_rectangle(f_x, f_y, f_x + f_lado, f_y + f_lado, fill=color_v, outline=color_v),
                           canvas.create_image(d_x, d_y, anchor=tkinter.NW, image=dados[d[i]-1])])

        i += 1


def insere_jogador_casa(casa, z, jogador):
    global raio_explorador, colors, canvas

    idx = -1
    new = True

    for e, el in enumerate(casa["canv_obj"][z]):
        
        if el["jogador"] == jogador:
            idx = e
            new = False

    if not new:
        casa["canv_obj"][z][idx]["qtd"]["num"] += 1
        canvas.delete(casa["canv_obj"][z][idx]["qtd"]["text"])

    else:
        idx = len(casa["canv_obj"][z])


    x = casa["front"]["pos_jogadores"][idx]["x"]
    y = casa["front"]["pos_jogadores"][idx]["y"]

    x, y = faz_pos_abs(x, y, z)
    
    cor_jogador = colors[jogador]
    if cor_jogador == "yellow":
        cor_txt = "black"
    else:
        cor_txt = "white"

    if new:
        exp = {}
        exp["jogador"] = jogador
        exp["circ"] = canvas.create_oval(x-raio_explorador, y-raio_explorador, x+raio_explorador, y+raio_explorador, fill=cor_jogador)
        exp["qtd"] = {}
        exp["qtd"]["num"] = 1

        casa["canv_obj"][z].append(exp)

    casa["canv_obj"][z][idx]["qtd"]["text"] = canvas.create_text(x, y, text=str(casa["canv_obj"][z][idx]["qtd"]["num"]), fill=cor_txt)
    

def remove_jogador_casa(casa, z, jogador):
    global canvas

    idx = None
    for e, el in enumerate(casa["canv_obj"][z]):
        if el["jogador"] == jogador:
            idx = e

    if idx == None:
        #tentando remove um jogador que não está na casa
        return

    exp = casa["canv_obj"][z][idx]
    if exp["qtd"]["num"] == 1:
        #se só houver um explorador na casa
        canvas.delete(exp["circ"])
        canvas.delete(exp["qtd"]["text"])
        casa["canv_obj"][z].pop(idx)

        if idx == 0 and len(casa["canv_obj"][z]) != 0:
            #se o explorador for o primeiro da lista e a lista não estiver vazia após sua remoção
            #coloca o explorador do outro jogador na primeira posicao

            qtd_exp = casa["canv_obj"][z][0]["qtd"]["num"]
            vez_exp = casa["canv_obj"][z][0]["jogador"]

            for _ in range(qtd_exp):
                remove_jogador_casa(casa, z, vez_exp)

            for _ in range(qtd_exp):
                insere_jogador_casa(casa, z, vez_exp)

    else:
        exp["qtd"]["num"] -= 1

        x = casa["front"]["pos_jogadores"][idx]["x"]
        y = casa["front"]["pos_jogadores"][idx]["y"]

        x, y = faz_pos_abs(x, y, z)
    
        cor_jogador = colors[jogador]
        if cor_jogador == "yellow":
            cor_txt = "black"
        else:
            cor_txt = "white"

        canvas.delete(exp["qtd"]["text"])
        casa["canv_obj"][z][idx]["qtd"]["text"] = canvas.create_text(x, y, text=str(casa["canv_obj"][z][idx]["qtd"]["num"]), fill=cor_txt)

def preenche_polos():
    global fronteiras, n_jogadores, canvas

    for casa in fronteiras:
        if casa["front"]["tipo"] == "polo":
            for i in range(n_jogadores):
                for _ in range(6):
                    insere_jogador_casa(casa, i % 2, i)

def limpa_tela():
    global canvas, telas

    for i in range(len(telas)):

        tela = telas.pop()
        canvas.delete(tela[1])



def tela_inicial(cnv):
    global canvas, telas

    canvas = cnv

    event_handler.set_estado(("inicial", ))

    img = tkinter.PhotoImage(file="./view/imgs/inicial1.png")
    telas.append((img, canvas.create_image(0, 0, anch=tkinter.NW, image=img)))


def sel_jogadores():
    global canvas, telas

    img = tkinter.PhotoImage(file="./view/imgs/inicial2.png")
    telas.append((img, canvas.create_image(0, 0, anch=tkinter.NW, image=img)))

def sel_dupla():
    global canvas, telas

    img = tkinter.PhotoImage(file="./view/imgs/dupla.png")
    telas.append((img, canvas.create_image(0, 0, anch=tkinter.NW, image=img)))

def limpa_objetos():
    global canvas, dado_combo, dado_button

    for dado in dado_combo:
        dado.destroy()

    dado_button.destroy()

    limpa_dados()
    limpa_dado_colorido()
    limpa_save()

def tela_vitoria():
    global canvas, telas

    limpa_objetos()
    ganhadores = game_rules.get_ganhadores()

    if (len(ganhadores) == 2):
        if ganhadores[0] == 0:
            img = tkinter.PhotoImage(file="./view/imgs/duplafinal1.png")
        else:
            img = tkinter.PhotoImage(file="./view/imgs/duplafinal2.png")

    else:
        img = tkinter.PhotoImage(file=f"./view/imgs/final{ganhadores[0]+1}.png")

    telas.append((img, canvas.create_image(0, 0, anchor=tkinter.NW, image=img)))

def mostra_carta(c):
    global carta

    img = tkinter.PhotoImage(file=f"./view/imgs/C{c:02}.png")

    carta = (img, canvas.create_image(279, 10, anchor=tkinter.NW, image=img))
    

def limpa_carta():
    global carta, canvas

    if carta:
        canvas.delete(carta[1])

    carta = None

def exibe_save():
    global save, canvas

    img = tkinter.PhotoImage(file="./view/imgs/save.png")

    save = (img, canvas.create_image(567, 6, anchor=tkinter.NW, image=img))

def limpa_save():
    global save, canvas

    if save:
        canvas.delete(save[1])

    save = None

def inicia_tabuleiro(from_save=False):
    global n_jogadores, modo_dupla, canvas, telas, dado_combo, dado_button

    n_jogadores = game_rules.get_njogadores()
    modo_dupla = game_rules.get_modo_dupla()

    faz_fronteiras()
    carrega_dados()

    img = tkinter.PhotoImage(file="./view/imgs/Latitude90-Tabuleiro.png")
    telas.append((img, canvas.create_image(0, 0, anchor=tkinter.NW, image=img)))  

    dado_combo = []

    combo = ttk.Combobox(canvas, state="readonly", width=10, height=10, values=("aleatório", "1", "2", "3", "4", "5", "6"))
    combo.place(x=213, y=640, anchor=tkinter.NW)
    combo.current(0)
    dado_combo.append(combo)

    combo = ttk.Combobox(canvas, state="readonly", width=10, height=10, values=("aleatório", "1", "2", "3", "4", "5", "6"))
    combo.place(x=213, y=665, anchor=tkinter.NW)
    combo.current(0)
    dado_combo.append(combo)


    dado_button = tkinter.Button(canvas, text="lançar dados", command=lanca_dados)
    dado_button.place(x=215, y = 690)

    if from_save:
        exibe_dado(True)
    else:
        preenche_polos() 
        exibe_dado()    
    

    '''for i in range(720):
        print(i)
        for j in range(724):
            if checa_casa(i, j):
                canvas.create_rectangle(i, j, i, j, outline="red")'''
