from view import draw
from controller import event_handler
import numpy as np
import json
import random

__all__ = ["inicia_jogo", "get_vez", "passa_vez", "get_fim_de_jogo", "lanca_dados", "verificar_casa", "validar_e_andar", "lanca_dado_colorido", "executa_dado_colorido"]

def inicia_jogo(jogadores: int, dupla: bool) -> None:
    global tabuleiro, polos, vez, metas, exploradores, modo_dupla, jogo_fim, qtd_jogadores

    if jogadores != 2 and jogadores != 4:
        raise ValueError("O jogo só pode ser jogado com 2 ou 4 pessoas")

    if jogadores == 2 and dupla:
        raise ValueError("Não é possível iniciar um jogo com 2 jogadores em dupla")

    qtd_jogadores = jogadores

    #inicia tabuleiro sem fichas

    tabuleiro = []

    for hesm in range(2):
        tabuleiro.append(list())

        for lat in range(6):
            tabuleiro[hesm].append(list())

            for long in range(12):
                tabuleiro[hesm][lat].append({"jogadores": list()})

    #insere as fichas no tabuleiro

    for hesm in range(2):
        tabuleiro[hesm][0][1]["ficha"]  = True
        tabuleiro[hesm][0][7]["ficha"]  = True
        tabuleiro[hesm][1][2]["ficha"]  = True
        tabuleiro[hesm][1][8]["ficha"]  = True
        tabuleiro[hesm][2][4]["ficha"]  = True
        tabuleiro[hesm][2][10]["ficha"] = True

    #inicia os polos

    polos = [list(), list()]

    for i in range(qtd_jogadores):
        for _ in range(6):
            #se estiver no modo dupla garente que a vez alternará entre jogadores de duplas diferentes
            polos[i%2].append(i)
            

    #inicia as metas e exploradores

    metas = list()
    exploradores = list()

    for _ in range(qtd_jogadores):
        metas.append(0)
        exploradores.append(0)

    vez = np.random.randint(0, qtd_jogadores)
    lanca_dados()
    embaralha_cartas()

    if dupla:
        modo_dupla = True
    else:
        modo_dupla = False

    jogo_fim = False

def faz_save(filename):
    global tabuleiro, polos, vez, metas, exploradores, modo_dupla, qtd_jogadores, dados, cartas

    save = {}
    save["tabuleiro"] = tabuleiro
    save["polos"] = polos
    save["vez"] = vez
    save["metas"] = metas
    save["exploradores"] = exploradores
    save["modo_dupla"] = modo_dupla
    save["qtd_jogadores"] = qtd_jogadores
    save["dados"] = dados
    save["dado_colorido"] = draw.get_dado_colorido()
    save["cartas"] = cartas

    with open(filename, "w") as file:
        json.dump(save, file)

def carrega_save(filename):
    global tabuleiro, polos, vez, metas, exploradores, modo_dupla, qtd_jogadores, dados, jogo_fim, cartas

    jogo_fim = False

    with open(filename, "r") as file:
        save = json.load(file)

    tabuleiro = save["tabuleiro"]
    polos = save["polos"]
    vez = save["vez"]
    metas = save["metas"]
    exploradores = save["exploradores"]
    modo_dupla = save["modo_dupla"]
    qtd_jogadores = save["qtd_jogadores"]
    dados = save["dados"]
    cartas = save["cartas"]

    draw.limpa_tela()
    draw.inicia_tabuleiro(True)
    event_handler.exibe_save()

    for hesm_i, hesm in enumerate(tabuleiro):
        for lat_i, lat in enumerate(hesm):
            for long_i, long in enumerate(lat):
                for jogador in long["jogadores"]:
                    casa = draw.get_casa(lat_i, long_i)
                    draw.insere_jogador_casa(casa, hesm_i, jogador)

    for polo in range(2):
        casa = draw.get_casa(6, 12)

        for jogador in polos[polo]:
            draw.insere_jogador_casa(casa, polo, jogador)

    if save["dado_colorido"]:
        draw.exibe_dado_colorido(save["dado_colorido"])
                


def get_vez() -> int:
    global vez
    
    return vez

def get_njogadores():
    global qtd_jogadores

    return qtd_jogadores

def get_modo_dupla():
    global modo_dupla

    return modo_dupla

def passa_vez() -> None:
    global vez

    vez = (vez + 1) % qtd_jogadores

    lanca_dados()

def get_fim_de_jogo() -> bool:
    global jogo_fim

    return jogo_fim

def get_dados() -> int:
    global dados

    return dados

def lanca_dados():
    global dados

    dados = [0, 0]
    
    dados[0] = np.random.randint(1, 7)
    dados[1] = np.random.randint(1, 7)

def define_dados(d1, d2):
    global dados

    dados = [0, 0]

    for e, el in enumerate([d1, d2]):
        if el == "aleatório":
            dados[e] = np.random.randint(1, 7)
        
        else:
            dados[e] = int(el)

def embaralha_cartas():
    global cartas

    arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    cartas = random.sample(arr, len(arr))

def verifica_polo(x: int, y: int) -> bool:
    if x == 6 and y == 12:
        return True
    else:
        return False

def casa_vazia(x: int, y: int, z: int) -> bool:
    global tabuleiro, vez, modo_dupla


    if verifica_polo(x, y):
        #polos são territórios neutros
        return True

    if len(tabuleiro[z][x][y]["jogadores"]) > 1:
        if vez in tabuleiro[z][x][y]["jogadores"]:
            #existe um explorador do jogador
            return True

        if modo_dupla and (vez + 2) % 4 in tabuleiro[z][x][y]["jogadores"]:
            #se existir um explorador de sua dupla na casa
            return True

        return False

    return True
        

def andar_lat(x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, dado: int, sentido: int) -> bool:
    '''função que anda latitudinalmente checando casa a casa para possíveis casas fechadas
       se o sentido for o número 1 anda em direção ao polo do hemisfério atual (z0),
       anda na direção oposta se sentido for o número -1'''

    x = x0
    y = y0
    z = z0

    if verifica_polo(x0, y0):
        polo = True

    else:
        polo = False

    if polo and z0 != z1:
        #impossível sair de um polo e chegar a outro hemisfério com um dado
        return False

    if sentido > 0:
        sentido = 1
    else:
        sentido = -1

    for i in range(dado):
        if polo:
            #está em um polo
            x = 5

            if y1 == 12:
                #se a direção final for um polo e não estiver na casa de parada
                return False

            elif y1 == y0:
                #não é possível voltar casas
                return False
            
            else:
                y = y1

            sentido = -1
            polo = False

        else:
            x = x + sentido


        if x < 0:
            #fora do mapa
            if y not in  [0, 5, 6, 11]:
                #não estiver nas casa de passagem entre hemisférios
                return False

            else:
                #passou de hemisfério, muda o sentido, hemisfério e a longitude
                
                if y == 0:
                    y = 5
                elif y == 5:
                    y = 0
                elif y == 6:
                    y = 11
                else:
                    y = 6

                x = 0
                z = (z + 1) % 2

                sentido = -sentido

        elif x == 6:
            #chegou em um polo
            polo = True
            y = 12
            continue

        if not casa_vazia(x, y, z):
            return False

    if x == x1 and y == y1 and z == z1:
        return True

    else:
        return False

def andar_long(x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, dado: int) -> bool:
    '''função que anda longitudinalmente checando casa a casa para possíveis casas fechadas'''

    #testando se é possível chegar na longitude desejada
    if (y0 + dado) % 12 == y1:
        sentido = 1
    elif (y0 - dado) % 12 == y1:
        sentido = -1
    else:
        return False

    for _ in range(dado):

        y0 = (y0 + sentido) % 12

        if not casa_vazia(x0, y0, z0):
            return False

    return True

def remover_explorador(jogador: int, x: int, y: int, z: int) -> bool:
    global tabuleiro, polos

    if verifica_polo(x, y):
        #polo
        if not jogador in polos[vez%2]:
            #não existe explorador do jogador no polo
            return False
        
        polos[vez%2].remove(jogador)
        
    else:
        if not jogador in tabuleiro[z][x][y]["jogadores"]:
            #não existe explorador
            return False
        
        tabuleiro[z][x][y]["jogadores"].remove(jogador)

    return True
    
def andar(x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, dado: int) -> None:
    global tabuleiro, polos, vez, metas, exploradores, modo_dupla, jogo_fim

    remover_explorador(vez, x0, y0, z0)        

    status = None
    if verifica_polo(x1, y1):
        if z0 != (vez % 2):
            #chegou no polo oposto
            exploradores[vez] += 1
            
            if exploradores[vez] == 6:
                jogo_fim = True

            status = ("polo", )

        else:
            #chegou no polo de início
            polos[vez%2].append(vez)

        return status
            
    
    if len(tabuleiro[z1][x1][y1]["jogadores"]) > 0 and tabuleiro[z1][x1][y1]["jogadores"].count(vez) == 0:
        #caso captura de explorador
        if not modo_dupla or tabuleiro[z1][x1][y1]["jogadores"][0] != (vez + 2) % 4:
            #se nao estiver no modo dupla ou nao for o explorador dupla do jogador da vez
            cap = tabuleiro[z1][x1][y1]["jogadores"].pop()
            polos[cap%2].append(cap)

            status = ("captura", cap)
    else:
        #caso meta é conquistada
        if "ficha" in tabuleiro[z1][x1][y1]:
            del tabuleiro[z1][x1][y1]["ficha"]

            metas[vez] += 1

            status = ("ficha", )
        

    tabuleiro[z1][x1][y1]["jogadores"].append(vez)

    return status

def verificar_casa(x: int, y: int, z: int) -> bool:
    global tabuleiro, polos, vez

    if x < 0 or x > 6:
        return False
    if y < 0 or y > 12:
        return False
    if z < 0 or z > 1:
        return False

    if verifica_polo(x, y):
        if vez in polos[z]:
           return True

        return False

    else:
        if vez in tabuleiro[z][x][y]["jogadores"]:
            return True

        return False

def validar_e_andar(x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, dado: int) -> bool:
    global tabuleiro, jogo_fim, qtd_jogadores, cartas

    if jogo_fim:
        return False

    if not verificar_casa(x0, y0, z0):
        #posicao inicial não possui exploradores do jogador da vez
        return False

    if x1 < 0 or x1 > 6:
        return False
    if y1 < 0 or y1 > 12:
        return False
    if z1 < 0 or z1 > 1:
        return False
    if dado < 1 or dado > 6:
        return False
    #não é necessário verificar para x0, y0 e z0 pois a função verificar_casa já faz isso


    if x0 == x1 and y0 == y1 and z0 == z1:
        #não é possível ficar no mesmo lugar
        return False



    if z0 != z1:
        #se mudou de hemisferio
        val = andar_lat(x0, y0, z0, x1, y1, z1, dado, -1)

    else:
        if x0 == x1:
            #andando longitudinalmente
            val = andar_long(x0, y0, z0, x1, y1, z1, dado)

        else:
            if y0 == y1:
                #andando latitudinalmente e não passa pelo polo 
                val = andar_lat(x0, y0, z0, x1, y1, z1, dado, x1-x0)

            else:
                #andando latitudinalmente passando pelo polo ou andando na diagonal
                val = andar_lat(x0, y0, z0, x1, y1, z1, dado, 1)

    if not val:
        return False

    status = andar(x0, y0, z0, x1, y1, z1, dado)

    if status:
        if status[0] == "ficha":
            #retira uma carta
            return (status[0], cartas.pop())

        return status

    return True

def lanca_dado_colorido():
    return np.random.choice([0, 1, 2, 3, None, None])

def executa_dado_colorido(x: int, y: int, z: int, dado: int) -> bool:
    '''função executa a ação do dado colorido, dado é um parâmetro que varia de 0 a 3
       (modo no qual os jogadores são identificados dentro do módulo'''
    
    global polos, vez, exploradores, modo_dupla, qtd_jogadores, jogo_fim

    if dado < 0 or dado > 3:
        return False
    if x < 0 or x > 6:
        return False
    if y < 0 or y > 12:
        return False
    if z < 0 or z > 1:
        return False

    if not remover_explorador(dado, x, y, z):
        #não encontrou explorador do jogado na posição
        return False

    if vez == dado or (modo_dupla and vez % 2 == dado):
        #se for o explorador do jogador ou de sua dupla

        exploradores[dado] += 1
            
        if exploradores[dado] == 6:
            jogo_fim = True

    else:
        #captura o explorador do adversário

        polos[dado%2].append(dado)

    return True



def get_ganhadores():
    global modo_dupla, exploradores, metas, qtd_jogadores

    pontos = [0, 0, 0, 0]

    jogador_terminou = exploradores.index(6)

    pontos[jogador_terminou] += 1

    for i in range(len(exploradores)):
        pontos[i] += exploradores[i]
        pontos[i] += metas[i]

    ganhador = pontos.index(max(pontos))

    if modo_dupla:
        return (ganhador, (ganhador + 2) % 2)

    else:
        return (ganhador, )

