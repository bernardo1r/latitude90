from view import draw
from model import game_rules
from tkinter import filedialog

jogada_ant = None
estado = []
meio_x = 364
root = None
canvas = None
exibe_save = False
pode_salvar = False

def set_root(rt):
    global root

    root = rt

def set_canvas(cnv):
    global canvas

    canvas = cnv

def set_estado(s):
    global estado

    estado = s

def checa_retangulo(x, y, retx0, rety0, retx1, rety1):

    if x >= retx0 and x <= retx1 and y >= rety0 and y <= rety1:
        return True

    return False

def inicia_jogo(qtd_jogadores, modo_dupla):
    global estado
    estado = ("jogo", )

    game_rules.inicia_jogo(qtd_jogadores, modo_dupla)

    draw.limpa_tela()
    draw.inicia_tabuleiro()
    exibe_save()

def carrega_jogo(file):
    global estado

    game_rules.carrega_save(file)

    estado = ("jogo", )

def tela_inicial(event):
    global estado

    x = event.x
    y = event.y

    if checa_retangulo(x, y, 44, 243, 351, 396):
        #se o jogador clicar novo jogo
        estado = ("sel_jogadores", )

        draw.limpa_tela()
        draw.sel_jogadores()

    elif checa_retangulo(x, y, 368, 243, 675, 396):
        #se o jogador clicar em carregar jogo
        file = filedialog.askopenfilename(title="Selecione um jogo", initialdir="./saves")
        if file:
            carrega_jogo(file)

def sel_jogadores(event):
    global estado

    x = event.x
    y = event.y

    if checa_retangulo(x, y, 44, 243, 351, 396):
        #se o jogador clicar 2 jogadores
        inicia_jogo(2, False)

    elif checa_retangulo(x, y, 368, 243, 675, 396):
        #se o jogador selecinou 4 jogadores

        estado = ("sel_dupla", )

        draw.limpa_tela()
        draw.sel_dupla()

def sel_dupla(event):
    global estado

    x = event.x
    y = event.y

    if checa_retangulo(x, y, 44, 243, 351, 396):
        #se o jogador selecionar modo competitivo
        inicia_jogo(4, False)

    elif checa_retangulo(x, y, 368, 243, 675, 396):
        #se o jogador selecionar o modo dupla
        inicia_jogo(4, True)


def executa_fim_de_jogo():
    global estado
    
    estado = ("vitoria", )

    draw.limpa_tela()
    draw.tela_vitoria()

def verifica_e_executa_fim_de_jogo():
    fim_de_jogo = game_rules.get_fim_de_jogo()

    if fim_de_jogo:
        executa_fim_de_jogo()

def exibe_save():
    global pode_salvar

    pode_salvar = True
    draw.exibe_save()

def passa_vez():
    game_rules.passa_vez()
    draw.exibe_dado()
    exibe_save()

def jogo(event):
    global jogada_ant, meio_x, estado, pode_salvar

    x = event.x
    y = event.y

    if estado[0] == "ficha" and estado[1] != 1 and estado[1] != 3:
        #se for uma ficha não implementada
        estado = ("jogo", )
        draw.limpa_carta()

        d = game_rules.get_dados()
        #se for a ultima ação do jogador
        if len(d) == 0:
            passa_vez()

    if pode_salvar and checa_retangulo(x, y, 567, 6, 714, 50):
        #salva o jogo
        file = filedialog.asksaveasfilename(title="Selecione um jogo", initialdir="./saves")
        if file:
            game_rules.faz_save(file)

            root.destroy()

            return

    casa = draw.checa_casa(x, y)
    if not casa:
        
        #pode ser que o jogador clicou no dado colorido
        dado_colorido = draw.get_dado_colorido()

        if dado_colorido and dado_colorido[0] != None and checa_retangulo(x, y, 615, 619, 714, 718):
            #se houver um dado colorido checar foi clicado nele

            jogada_ant = "dado_colorido"

            return

    if casa:

        if x > meio_x:
            z = 1
        else:
            z = 0

        if jogada_ant == None:
            casa["game_coords"]["z"] = z
            
            jogada_ant = casa
            return

        elif jogada_ant != "dado_colorido":
            x0 = jogada_ant["game_coords"]["x"]
            y0 = jogada_ant["game_coords"]["y"]
            z0 = jogada_ant["game_coords"]["z"]

            x1 = casa["game_coords"]["x"]
            y1 = casa["game_coords"]["y"]
            z1 = z

            d = game_rules.get_dados()

            if estado[0] == "ficha":
                ret = None
                if estado[1] == 1:
                    #implementacao carta 1: anda um explorador 6 casas
                    ret = game_rules.validar_e_andar(x0, y0, z0, x1, y1, z1, 6)
                elif estado[1] == 3:
                    #implementacao carta 3: anda um explorador 3 casas
                    ret = game_rules.validar_e_andar(x0, y0, z0, x1, y1, z1, 3)
                    

                if ret:
                    #se fez uma jogada valida
                    draw.limpa_carta()

                    vez = game_rules.get_vez()

                    draw.remove_jogador_casa(jogada_ant, z0, vez)
                    draw.insere_jogador_casa(casa, z1, vez)

                    if len(d) == 0:
                        #se for a ultima ação do jogador
                        passa_vez()

                    estado = ("jogo", )

                    verifica_e_executa_fim_de_jogo()

                    

                
                jogada_ant = None
                return


            for e, el in enumerate(d):
                ret = game_rules.validar_e_andar(x0, y0, z0, x1, y1, z1, el)
                if ret:

                    if len(d) == 2:
                        #jogador fez sua primeira jogada válida esconde opção salvar
                        draw.limpa_save()
                        pode_salvar = False

                    d.pop(e)

                    vez = game_rules.get_vez()

                    if type(ret) == tuple:
                        if ret[0] == "polo":
                            draw.remove_jogador_casa(jogada_ant, z0, vez)

                        elif ret[0] == "captura":
                            #remove jogador inimigo da posição de destino do jogador da vez e insire no seu polo
                            polo = ret[1] % 2
                            casa_polo = draw.get_casa(6, 12)

                            draw.remove_jogador_casa(casa, z1, ret[1])
                            draw.insere_jogador_casa(casa_polo, polo, ret[1])

                        elif ret[0] == "ficha":
                            estado = ("ficha", ret[1])
                            draw.mostra_carta(ret[1])

                    if ret == True or (type(ret) == tuple and ret[0] != "polo"):
                        #se for uma jogada que não foi ao polo oposto
                        draw.remove_jogador_casa(jogada_ant, z0, vez)
                        draw.insere_jogador_casa(casa, z1, vez)

                    draw.remove_dado(e)

                    verifica_e_executa_fim_de_jogo()

                    if len(d) == 0 and (type(ret) != tuple or ret[0] != "ficha"):
                        passa_vez()

        
        else:
            #executa dado colorido

            x1 = casa["game_coords"]["x"]
            y1 = casa["game_coords"]["y"]
            z1 = z
            dado_colorido = draw.get_dado_colorido()

            ret = game_rules.executa_dado_colorido(x1, y1, z1, dado_colorido[0])

            if ret:
                #se foi uma jogada válida
                draw.remove_jogador_casa(casa, z1, dado_colorido[0])

                vez = game_rules.get_vez()
                dupla = game_rules.get_modo_dupla()

                if dado_colorido[0] % 2 != vez % 2 or (dupla == False and dado_colorido[0] != vez):
                    #se foi selecionado um explorador inimigo, coloca no polo de origem
                    polo = dado_colorido[0] % 2
                    casa_polo = draw.get_casa(6, 12)
                    
                    draw.insere_jogador_casa(casa_polo, polo, dado_colorido[0])

                draw.limpa_dado_colorido()

                verifica_e_executa_fim_de_jogo()


        jogada_ant = None


    else:
        jogada_ant = None

def vitoria(event):
    global estado, canvas

    x = event.x
    y = event.y

    if checa_retangulo(x, y, 44, 533, 351, 686):
        #opcao jogar novamente
        estado = ("inicial", )

        draw.limpa_tela()
        draw.tela_inicial(canvas)

    elif checa_retangulo(x, y, 368, 533, 675, 686):
        #sair do jogo

        root.destroy()


def click(event):
    
    if estado[0] == "inicial":
        tela_inicial(event)

    elif estado[0] == "sel_jogadores":
        sel_jogadores(event)

    elif estado[0] == "sel_dupla":
        sel_dupla(event)

    elif estado[0] == "jogo" or estado[0] == "ficha":
        jogo(event)

    else:
        #vitoria
        vitoria(event)