from view import draw
from model import game_rules

jogada_ant = None
estado = None
meio_x = 364
root = None
canvas = None

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

def tela_inicial(event):
    global estado

    x = event.x
    y = event.y

    if checa_retangulo(x, y, 44, 243, 351, 396):
        #se o jogador clicar novo jogo
        estado = "sel_jogadores"

        draw.limpa_tela()
        draw.sel_jogadores()

def sel_jogadores(event):
    global estado

    x = event.x
    y = event.y

    if checa_retangulo(x, y, 44, 243, 351, 396):
        #se o jogador clicar 2 jogadores

        estado = "jogo"

        game_rules.inicia_jogo(2, False)

        draw.limpa_tela()
        draw.inicia_tabuleiro()

    elif checa_retangulo(x, y, 368, 243, 675, 396):
        #se o jogador selecinou 4 jogadores

        estado = "sel_dupla"

        draw.limpa_tela()
        draw.sel_dupla()

def sel_dupla(event):
    global estado

    x = event.x
    y = event.y

    selecionado = False

    if checa_retangulo(x, y, 44, 243, 351, 396):
        #se o jogador selecionar modo competitivo
        game_rules.inicia_jogo(4, False)
        selecionado = True

    elif checa_retangulo(x, y, 368, 243, 675, 396):
        #se o jogador selecionar o modo dupla
        game_rules.inicia_jogo(4, True)
        selecionado = True

    if selecionado:
        draw.limpa_tela()
        draw.inicia_tabuleiro()

        estado = "jogo"

def jogo(event):
    global jogada_ant, meio_x, estado

    x = event.x
    y = event.y

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

            for e, el in enumerate(d):
                ret = game_rules.validar_e_andar(x0, y0, z0, x1, y1, z1, el)
                if ret:

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

                    if ret == True or (type(ret) == tuple and ret[0] != "polo"):
                        draw.remove_jogador_casa(jogada_ant, z0, vez)
                        draw.insere_jogador_casa(casa, z1, vez)


                    draw.remove_dado(e)

                    fim_de_jogo = game_rules.get_fim_de_jogo()

                    if fim_de_jogo:
                        estado = "vitoria"

                        draw.limpa_tela()
                        draw.tela_vitoria()

                        return

                    jogada_ant = None

                    if len(d) == 0:
                        game_rules.passa_vez()
                        draw.exibe_dado()

                    return


            jogada_ant = None
        
        else:
            #executa dado colorido

            x1 = casa["game_coords"]["x"]
            y1 = casa["game_coords"]["y"]
            z1 = z
            dado_colorido = draw.get_dado_colorido()

            ret = game_rules.executa_dado_colorido(x1, y1, z1, dado_colorido[0])

            if ret:
                draw.remove_jogador_casa(casa, z1, dado_colorido[0])

                vez = game_rules.get_vez()
                dupla = game_rules.get_modo_dupla()

                if dado_colorido[0] % 2 != vez % 2 or (dupla == False and dado_colorido[0] != vez):
                    polo = dado_colorido[0] % 2
                    casa_polo = draw.get_casa(6, 12)
                    
                    draw.insere_jogador_casa(casa_polo, polo, dado_colorido[0])

                draw.limpa_dado_colorido()

                fim_de_jogo = game_rules.get_fim_de_jogo()

                if fim_de_jogo:
                    estado = "vitoria"

                    draw.limpa_tela()
                    draw.tela_vitoria()

                    return

                jogada_ant = None


    else:
        jogada_ant = None

def vitoria(event):
    global estado, canvas

    x = event.x
    y = event.y

    if checa_retangulo(x, y, 44, 533, 351, 686):
        #opcao jogar novamente
        evento = "inicial"

        draw.limpa_tela()
        draw.tela_inicial(canvas)

    elif checa_retangulo(x, y, 368, 533, 675, 686):
        #sair do jogo

        root.destroy()

def click(event):
    
    if estado == "inicial":
        tela_inicial(event)

    elif estado == "sel_jogadores":
        sel_jogadores(event)

    elif estado == "sel_dupla":
        sel_dupla(event)

    elif estado == "jogo":
        jogo(event)

    else:
        #vitoria
        vitoria(event)