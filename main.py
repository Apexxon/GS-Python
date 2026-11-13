import json
# ==== Parte Enzo ====
from datetime import date


# ==== Parte do José (segundo commit)====
# ------------
# Ponto Fresco
# ------------

# Funções
def validacao(variavel):
    """Essa função recebe as opções do usuario, checa se é válida e retorna a opção já como tipo int"""
    if variavel.isdigit():
        variavel = int(variavel)
        return variavel
    else:
        return -1


def carregar_dados():
    """Função que carrega os pontos do arquivo json"""
    try:
        with open("pontos.json", "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return []


def salvar_dados(lista_pontos):
    """Função que salva os dados e envia eles pro arquivo json"""
    with open("pontos.json", "w", encoding="utf-8") as arquivo:
        json.dump(lista_pontos, arquivo, ensure_ascii=False, indent=4)


# ==== parte do Enzo: indice de calor, estados e relatos (opções 5, 6 e 7) ====
LIMITES = (27.0, 32.0, 39.0)  # Tupla: limites de atenção, alerta e perigo °C, igual do ESP32
CORRECAO_SOL = 8.0  # °C somados ao indice quando o ponto não tem cobertura, ou seja, sol direto
REGIOES = ('Leste', 'Sul', 'Norte', 'Oeste', 'Centro')
TIPOS_RELATO = ('Ônibus atrasou', 'Ponto sem cobertura', 'Bebedouro quebrado',
                'Pessoa passando mal', 'Problema de segurança', 'Outro')


def calcular_indice_calor(temp_c, umidade, sol):
    """Calcula o índice de calor em °C pela regressão de Rothfusz
    Se sol=True (ponto sem cobertura), soma a correção de sol direto."""
    t = temp_c * 9 / 5 + 32  # em °F
    ic = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + umidade * 0.094)  # fórmula simples (dias amenos)

    if (ic + t) / 2 >= 80:  # em dias quentes usa a regressão completa
        ic = (-42.379 + 2.04901523 * t + 10.14333127 * umidade
              - 0.22475541 * t * umidade - 0.00683783 * t ** 2
              - 0.05481717 * umidade ** 2 + 0.00122874 * t ** 2 * umidade
              + 0.00085282 * t * umidade ** 2 - 0.00000199 * t ** 2 * umidade ** 2)
        if umidade < 13 and 80 <= t <= 112:
            ic -= ((13 - umidade) / 4) * ((17 - abs(t - 95)) / 17) ** 0.5
        elif umidade > 85 and 80 <= t <= 87:
            ic += ((umidade - 85) / 10) * ((87 - t) / 5)

    ic_celsius = (ic - 32) * 5 / 9
    if sol:
        ic_celsius += CORRECAO_SOL
    return round(ic_celsius, 1)


def indice_da_leitura(leitura):
    """Recebe uma leitura e devolve o indice de calor dela. Sem cobertura = sol direto"""
    return calcular_indice_calor(leitura["temperatura"], leitura["umidade"], not leitura["cobertura"])


def indice_medio(leituras):
    """Recebe a lista de leituras de um ponto e devolve a média dos índices de calor."""
    soma = 0
    for leitura in leituras:
        soma += indice_da_leitura(leitura)
    return round(soma / len(leituras), 1)


def classificar_estado(ic):
    """Classifica o indice de calor em normal, atencao, alerts ou perigo."""
    if ic >= LIMITES[2]:
        return "perigo"
    elif ic >= LIMITES[1]:
        return "alerta"
    elif ic >= LIMITES[0]:
        return "atenção"
    else:
        return "normal"


def recomendacao(estado):
    """Devolve a orientação para o cidadaõ de acordo com o estado."""
    match estado:
        case "normal":
            return "Sem risco relevante. Pode esperar tranquilo."
        case "atenção":
            return "Está quente. Beba água enquanto espera."
        case "alerta":
            return "Está quente demais para esperar ao sol. Procure sombra."
        case "perigo":
            return "Calor perigoso agora. Procure sombra e água o quanto antes."
        case _:
            return "estado desconhecido."


def tem_dado_pessoal(texto):
    """relato não pode ter telefone ou documento.
    Considera suspeito um texto com 8 ou mais dígitos."""
    digitos = 0
    for caractere in texto:
        if caractere.isdigit():
            digitos += 1
    return digitos >= 8


# ==== parte do José ====

pontos = carregar_dados()  # Lista principal que guarda os dados

# Código

while True:
    print('==== PONTO FRESCO ====')
    print('Encontre seu melhor ponto.')
    print('---' * 8)
    print('1 - Cadastrar Ponto de Onibus')
    print('2 - Atualizar ou Remover ponto')
    print('3 - Lista de Pontos')
    print('4 - Registrar Leitura (Temp, Umid, Cobertura)')
    print('5 - Estado Atual')
    print('6 - Recomendação de Ponto')
    print('7 - Registrar Relato')
    print('8 - Sair')
    print('---' * 8)

    opcao = input('Digite sua opção: ')
    opcao = validacao(opcao)

    if opcao not in (1, 2, 3, 4, 5, 6, 7, 8):
        print('')
        print('-> Opção inválida, tente novamente! <-')
        print('')

    elif opcao == 1:

        print('Opção 1 - Cadastrar Ponto de Onibus')
        print('-----' * 7)

        nome = input('Digite o nome do ponto: ')

        while True:  # CHECA SE A REGIÃO EXISTE (Ex: Sul, Norte, Centro, Etc.)
            regiao = input('Digite a região: ')
            if regiao.capitalize() not in ('Leste', 'Sul', 'Norte', 'Oeste', 'Centro'):
                print('Região inválida. Tente novamente!')
            else:
                break

        while True: # CHECA SE AS COORDENADAS SÃO NÚMEROS
            coordenadas = input('Digite as coordenadas: ').strip()

            partes = coordenadas.split()

            if partes and all(p.replace('-', '').isdigit() for p in partes):
                break
            else:
                print('Erro! Digite apenas números separados por espaço. Tente novamente!')

        while True:
            cobertura = input('O Ponto tem cobertura? (S ou N) ')
            if cobertura.capitalize() not in ('Sim', 'S', 'N', 'Nao', 'Não'):
                print('Opção inválida! Digite "S" ou "N"')
            else:
                break

        novo_ponto = {
            "nome": nome.capitalize(),
            "regiao": regiao.capitalize(),
            "coordenadas": coordenadas,
            "leituras": [],  # Leituras da opção 4
            "relatos": [],  # Relatos da opção 7
            "cobertura": cobertura.capitalize()
        }

        pontos.append(novo_ponto)
        salvar_dados(pontos)

        print('\nPonto cadastrado e salvo com sucesso! Para registrar uma Leitura, selecione a opção 4.\n')


    elif opcao == 2:

        print('Opção 2 - Atualizar ou Remover ponto')
        print('-----' * 7)

        if len(pontos) == 0:
            print('Nenhum ponto cadastrado ainda!')
            print('')

        else:
            print('Pontos cadastrados:')

            for i, ponto in enumerate(pontos, start=1):
                print(f'{i} - {ponto["nome"]} ({ponto["regiao"]})')
            print('0 - Voltar ao menu principal')

            while True:
                escolha = input('Digite o número do ponto desejado: ')
                escolha = validacao(escolha)

                if escolha == 0:
                    break

                elif 1 <= escolha <= len(pontos):
                    ponto_selecionado = pontos[escolha - 1]

                    print(f'--- Ponto Selecionado: {ponto_selecionado["nome"]} ---')
                    print('1 - Atualizar Informações')
                    print('2 - Remover Ponto')
                    print('3 - Voltar')

                    sub_opc = input('Opção: ')
                    sub_opc = validacao(sub_opc)

                    if sub_opc == 1:

                        print('O que você deseja atualizar?')
                        print('1 - Nome')
                        print('2 - Região')
                        print('3 - Coordenadas')

                        campo = input('Digite o número do campo: ')
                        campo = validacao(campo)

                        if campo == 1:

                            novo_nome = input('Novo nome: ').strip()
                            if novo_nome != '':
                                ponto_selecionado['nome'] = novo_nome
                                print('Nome atualizado!')

                        elif campo == 2:
                            while True:
                                nova_reg = input('Nova região: ').capitalize()
                                if nova_reg in ('Leste', 'Sul', 'Norte', 'Oeste', 'Centro'):

                                    ponto_selecionado['regiao'] = nova_reg
                                    print('Região atualizada!')
                                    break
                                else:
                                    print('Região inválida!')

                        elif campo == 3:
                            while True:
                                novas_coords = input('Novas coordenadas: ').strip()
                                if novas_coords != '':
                                    ponto_selecionado['coordenadas'] = novas_coords
                                    print('Coordenadas atualizadas!')
                                    break
                                else:
                                    print('Coordenadas inválidas!')

                        salvar_dados(pontos)

                    elif sub_opc == 2:

                        confirmar = input(
                            f'Tem certeza que deseja apagar "{ponto_selecionado["nome"]}"? (S/N): ').strip().upper()

                        if confirmar == 'S':

                            pontos.pop(escolha - 1)

                            salvar_dados(pontos)

                            print('Ponto removido com sucesso!')

                        else:

                            print('Operação cancelada.')

                    break

                else:

                    print('Número de ponto inválido! Tente novamente.')


    elif opcao == 3:

        print('Opção 3 - Lista de Pontos')
        print('----' * 7)

        if len(pontos) == 0:
            print('Nenhum ponto cadastrado ainda!\n')

        else:
            print('Pontos cadastrados:')

            for i, ponto in enumerate(pontos, start=1):
                print(f'{i} - {ponto["nome"]} ({ponto["regiao"]})')

            print('0 - Voltar ao menu principal')
            while True:
                opc_lista = input('\nDigite o número do ponto para ver os detalhes (ou 0 para voltar): ')
                opc_lista = validacao(opc_lista)

                if opc_lista == 0:
                    break

                elif 1 <= opc_lista <= len(pontos):
                    ponto_selecionado = pontos[opc_lista - 1]

                    print(f'\n' + '=' * 30)
                    print(f'DETALHES DO PONTO: {ponto_selecionado["nome"]}')
                    print('=' * 30)

                    print(f'Região: {ponto_selecionado["regiao"]}')
                    print(f'Coordenadas: {ponto_selecionado["coordenadas"]}')
                    print(f'Possui Cobertura (No momento cadastrado): {ponto_selecionado["cobertura"]}')

                    print('\n--- Histórico de Leituras ---')
                    if len(ponto_selecionado["leituras"]) == 0:
                        print('Nenhuma leitura registrada ainda.')
                    else:
                        for index, leitura in enumerate(ponto_selecionado["leituras"], start=1):
                            cobertura_txt = "Sim" if leitura["cobertura"] else "Não"

                            print(
                                f'  {index}. Temp: {leitura["temperatura"]}°C | Umidade: {leitura["umidade"]}% | Cobertura: {cobertura_txt}')

                    print('\n--- Relatos da Comunidade ---')  # Relatos da opção 7

                    if len(ponto_selecionado["relatos"]) == 0:
                        print('Nenhum relato registrado ainda.')

                    else:

                        for index, relato in enumerate(ponto_selecionado["relatos"], start=1):
                            print(f'  {index}. {relato}')

                    print('=' * 30 + '\n')
                    break

                else:

                    print('Número de ponto inválido! Tente novamente.')

        print('Voltando ao menu...\n')


    elif opcao == 4:

        print('Opção 4 - Registrar Leitura (Temp, Umid, Cobertura)')
        print('-----' * 7)

        if len(pontos) == 0:

            print('Nenhum ponto cadastrado ainda!\n')

        else:

            for i, ponto in enumerate(pontos, start=1):
                print(f'{i} - {ponto["nome"]} ({ponto["regiao"]})')
            print('0 - Voltar ao menu principal')

            while True:
                opc_registro = input('Digite o número do ponto desejado: ')
                opc_registro = validacao(opc_registro)

                if opc_registro == 0:
                    break

                elif 1 <= opc_registro <= len(pontos):
                    ponto_selecionado = pontos[opc_registro - 1]

                    print(f'\n--- Ponto Selecionado: {ponto_selecionado["nome"]} ---')
                    print('Iniciando Registro de Leitura...\n')

                    while True:  # Pega a temperatura
                        try:
                            temperatura = float(input('Digite a temperatura (°C): ').strip())
                        except ValueError:
                            print('Erro! Digite um valor de temperatura válido (ex: 28.5 ou -2).')

                        if temperatura > 80 or temperatura < -40:
                            print('Temperatura inválida! Digite novamente.')
                        else:
                            break

                    while True:  # PEga a umidade
                        try:
                            umidade = float(input('Digite a umidade (%): ').strip())
                            if 0 <= umidade <= 100:
                                break
                            else:
                                print('Erro! A umidade deve estar entre 0 e 100.')
                        except ValueError:
                            print('Erro! Digite um valor de umidade válido.')

                    while True:  # Pega a cobertura do ponto
                        cobertura_leitura = input('O ponto possui cobertura no momento? (S/N): ').strip().capitalize()

                        if cobertura_leitura in ('Sim', 'S', 'N', 'Nao', 'Não'):
                            tem_cobertura = True if cobertura_leitura in ('Sim', 'S') else False
                            break

                        else:
                            print('Opção inválida! Digite "S" ou "N".')

                    nova_leitura = {
                        "temperatura": temperatura,
                        "umidade": umidade,
                        "cobertura": tem_cobertura
                    }
                    ponto_selecionado["leituras"].append(nova_leitura)

                    salvar_dados(pontos)
                    print('\nLeitura registrada e salva com sucesso!\n')
                    break
                else:
                    print('Número de ponto inválido! Tente novamente.')


    elif opcao == 5:  # Estado atual compara a temperatura de todas e retorna um estado (critico, favoravel, etc)
        # ==== parte do Enzo: opção 5 (Estado Atual) ====

        print('Opção 5 - Estado Atual')
        print('---' * 7)

        if len(pontos) == 0:
            print('nenhum ponto cadastrado ainda\n')

        else:
            com_leitura = []  # Tuplas (índice de calor, nome, região)
            sem_leitura = []

            for ponto in pontos:
                if len(ponto["leituras"]) == 0:
                    sem_leitura.append(ponto["nome"])
                else:
                    ultima = ponto["leituras"][-1]
                    com_leitura.append((indice_da_leitura(ultima), ponto["nome"], ponto["regiao"]))

            if len(com_leitura) == 0:
                print('Nenhum ponto tem leituras ainda. Use a opção 4 para registrar.\n')

            else:
                com_leitura = sorted(com_leitura, reverse=True)  # Mais quente primeiro

            for posicao, (ic, nome, regiao) in enumerate(com_leitura, start=1):
                estado = classificar_estado(ic)
                print(f'{posicao}. {nome} ({regiao}) - Índice de calor: {ic}°C - {estado}')
                print(f'   -> {recomendacao(estado)}')

            if len(sem_leitura) > 0:
                print('\nSem leituras: ' + ', '.join(sem_leitura))

            print('')

    # ==== parte do José ====

    elif opcao == 6:  # Recomendação de Ponto, pergunta sua região e te dá o ponto com condições mais favoraveis (temp entre 16 a 30 graus em média; umidade boa; tem cobertura)
        # ==== parte do enzo: opção 6 (Recomendação de Ponto) ====

        print('Opção 6 - Recomendação de Ponto')
        print('---' * 7)

        if len(pontos) == 0:
            print('nenhum ponto cadastrado ainda\n')

        else:
            while True:
                regiao_busca = input('Digite a região (Leste, Sul, Norte, Oeste ou Centro): ').strip().capitalize()
                if regiao_busca in REGIOES:
                    break
                else:
                    print('Região inválida. Tente novamente')

            melhor_ponto = None
            melhor_ic = 0

            for ponto in pontos:
                if ponto["regiao"] == regiao_busca and len(ponto["leituras"]) > 0:
                    ic_medio = indice_medio(ponto["leituras"])
                    if melhor_ponto is None or ic_medio < melhor_ic:
                        melhor_ponto = ponto
                        melhor_ic = ic_medio

            if melhor_ponto is None:
                print(f'\nNenhum ponto com leituras na região {regiao_busca}.\n')

            else:
                estado = classificar_estado(melhor_ic)
                cobertura_txt = "Sim" if melhor_ponto["leituras"][-1]["cobertura"] else "Não"

                print(f'\nMelhor ponto da região {regiao_busca}: {melhor_ponto["nome"]}')
                print(f'Índice de calor médio: {melhor_ic}°C - {estado}')
                print(f'Cobertura na última leitura: {cobertura_txt}')
                print(f'-> {recomendacao(estado)}\n')

        # ==== parte do José ====
    elif opcao == 7:  # Registra um relato que é mais uma descrição sobre um ocorrido (onibus atrasou/assalto/tals)
        # ==== parte do Enzo: opção 7 (Registrar Relato) ====

        print('Opção 7 - Registrar Relato')
        print('---' * 7)

        if len(pontos) == 0:
            print('Nenhum ponto cadastrado ainda\n')

        else:
            for i, ponto in enumerate(pontos, start=1):
                print(f'{i} - {ponto["nome"]} ({ponto["regiao"]})')
            print('0 - voltar ao menu principal')

            while True:
                opc_relato = input('Digite o numero do ponto desejado:')
                opc_relato = validacao(opc_relato)

                if opc_relato == 0:
                    break

                elif 1 <= opc_relato <= len(pontos):
                    ponto_selecionado = pontos[opc_relato - 1]

                    print(f'\n--- Ponto Selecionado: {ponto_selecionado["nome"]} ---')
                    print('Tipo de relato:')
                    for i, tipo_relato in enumerate(TIPOS_RELATO, start=1):
                        print(f'{i} - {tipo_relato}')

                    while True:  #escolhe o tipo
                        escolha_tipo = input('Digite o número do tipo: ')
                        escolha_tipo = validacao(escolha_tipo)

                        if 1 <= escolha_tipo <= len(TIPOS_RELATO):
                            tipo = TIPOS_RELATO[escolha_tipo - 1]
                            break
                        else:
                            print('Tipo inválido, tente novamente')
                    while True:  #descrição sem dados pessoais
                        descricao = input('Descreva o ocorrido (sem seus dados pessoais): ').strip()

                        if descricao == '':
                            print('Erro, a descrição não pode ficar vazia')
                        elif tem_dado_pessoal(descricao):
                            print('Erro, não coloque telefone ou documento no relato.')
                        else:
                            break

                    relato = f'[{date.today().isoformat()}] {tipo}: {descricao}'
                    ponto_selecionado["relatos"].append(relato)

                    salvar_dados(pontos)
                    print('\nRelato registrado e salvo com sucesso. Veja na opção 3.\n')
                    break

                else:
                    print('Número de ponto inválido. Tente novamente.')

        # ==== parte parte do josé ====

    elif opcao == 8:

        print('Opção 8 - Sair')

        print('Desligando o sistema...')
        print('Obrigado por ajudar nossa Comunidade!')
        break
