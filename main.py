import json
from datetime import date

# ------------
# Ponto Fresco
# ------------
# Central de análise do Ponto Fresco: cadastra pontos de ônibus, registra
# leituras de temperatura e umidade, calcula o índice de calor e o estado de
# risco, recomenda o ponto mais fresco de cada região e registra relatos.

# ==== Constantes ====
ARQUIVO_DADOS = "pontos.json"
LIMITES = (27.0, 32.0, 39.0)  # Tupla: limites de atenção, alerta e perigo em °C, iguais aos do ESP32
CORRECAO_SOL = 8.0  # °C somados ao índice quando o ponto não tem cobertura, ou seja, sol direto
REGIOES = ('Leste', 'Sul', 'Norte', 'Oeste', 'Centro')
RESPOSTAS_SIM = ('S', 'Sim')
RESPOSTAS_NAO = ('N', 'Nao', 'Não')
TIPOS_RELATO = ('Ônibus atrasou', 'Ponto sem cobertura', 'Bebedouro quebrado',
                'Pessoa passando mal', 'Problema de segurança', 'Outro')


# ==== Funções de entrada e validação ====
def validacao(variavel):
    """Recebe a opção digitada pelo usuário, checa se é um número inteiro e retorna como int.
    Se não for válida, retorna -1."""
    variavel = variavel.strip()
    if variavel.isdigit():
        return int(variavel)
    else:
        return -1


def ler_float(mensagem, minimo, maximo):
    """Pede um número decimal ao usuário e repete até que o valor esteja entre minimo e maximo."""
    while True:
        try:
            valor = float(input(mensagem).strip().replace(',', '.'))
        except ValueError:
            print(f'Erro! Digite um número válido (ex: 28.5).')
            continue

        if valor != valor:  # só é verdadeiro quando o valor é "nan" (não é um número)
            print('Erro! Digite um número válido (ex: 28.5).')
        elif valor < minimo or valor > maximo:
            print(f'Erro! O valor deve estar entre {minimo} e {maximo}.')
        else:
            return valor


def ler_sim_nao(mensagem):
    """Pergunta algo de sim ou não e retorna True para sim e False para não."""
    while True:
        resposta = input(mensagem).strip().capitalize()
        if resposta in RESPOSTAS_SIM:
            return True
        elif resposta in RESPOSTAS_NAO:
            return False
        else:
            print('Opção inválida! Digite "S" ou "N".')


def ler_regiao(mensagem):
    """Pede uma região e repete até que ela esteja na tupla REGIOES."""
    while True:
        regiao = input(mensagem).strip().capitalize()
        if regiao in REGIOES:
            return regiao
        else:
            print('Região inválida. Opções: ' + ', '.join(REGIOES) + '.')


def ler_texto(mensagem):
    """Pede um texto e repete até que ele não esteja vazio."""
    while True:
        texto = input(mensagem).strip()
        if texto != '':
            return texto
        else:
            print('Erro! Esse campo não pode ficar vazio.')


def ler_coordenadas(mensagem):
    """Pede latitude e longitude separadas por espaço (ex: -23.54 -46.47).
    Retorna uma tupla (latitude, longitude)."""
    while True:
        partes = input(mensagem).strip().replace(',', '.').split()
        if len(partes) != 2:
            print('Erro! Digite a latitude e a longitude separadas por espaço (ex: -23.54 -46.47).')
            continue
        try:
            latitude = float(partes[0])
            longitude = float(partes[1])
        except ValueError:
            print('Erro! As coordenadas devem ser números (ex: -23.54 -46.47).')
            continue

        if -90 <= latitude <= 90 and -180 <= longitude <= 180:
            return (latitude, longitude)
        else:
            print('Erro! A latitude vai de -90 a 90 e a longitude de -180 a 180.')


def escolher_ponto(pontos):
    """Mostra os pontos cadastrados e pede para o usuário escolher um.
    Retorna o índice do ponto na lista, ou -1 se o usuário escolher voltar."""
    for i, ponto in enumerate(pontos, start=1):
        print(f'{i} - {ponto["nome"]} ({ponto["regiao"]})')
    print('0 - Voltar ao menu principal')

    while True:
        escolha = validacao(input('Digite o número do ponto desejado: '))
        if escolha == 0:
            return -1
        elif 1 <= escolha <= len(pontos):
            return escolha - 1
        else:
            print('Número de ponto inválido! Tente novamente.')


def texto_sim_nao(valor):
    """Converte True/False em "Sim"/"Não" para mostrar na tela."""
    return "Sim" if valor else "Não"


# ==== Funções de arquivo (JSON) ====
def carregar_dados():
    """Carrega os pontos do arquivo JSON. Se o arquivo não existir ou estiver
    corrompido, começa com uma lista vazia."""
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            pontos = json.load(arquivo)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f'Aviso: o arquivo {ARQUIVO_DADOS} está vazio ou corrompido. Começando sem pontos.\n')
        return []

    for ponto in pontos:
        # O JSON não tem tuplas: as coordenadas são gravadas como lista e convertidas ao carregar
        ponto["coordenadas"] = tuple(ponto["coordenadas"])
    return pontos


def salvar_dados(lista_pontos):
    """Salva a lista de pontos no arquivo JSON."""
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
            json.dump(lista_pontos, arquivo, ensure_ascii=False, indent=4)
    except OSError:
        print(f'Erro! Não foi possível salvar o arquivo {ARQUIVO_DADOS}.')


# ==== Índice de calor, estados e recomendações ====
def calcular_indice_calor(temp_c, umidade, sol):
    """Calcula o índice de calor em °C pela regressão de Rothfusz.
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
    """Recebe uma leitura e devolve o índice de calor dela. Sem cobertura = sol direto."""
    return calcular_indice_calor(leitura["temperatura"], leitura["umidade"], not leitura["cobertura"])


def indice_medio(leituras):
    """Recebe a lista de leituras de um ponto e devolve a média dos índices de calor."""
    soma = 0
    for leitura in leituras:
        soma += indice_da_leitura(leitura)
    return round(soma / len(leituras), 1)


def classificar_estado(ic):
    """Classifica o índice de calor em normal, atenção, alerta ou perigo."""
    if ic >= LIMITES[2]:
        return "perigo"
    elif ic >= LIMITES[1]:
        return "alerta"
    elif ic >= LIMITES[0]:
        return "atenção"
    else:
        return "normal"


def recomendacao(estado):
    """Devolve a orientação para o cidadão de acordo com o estado."""
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
            return "Estado desconhecido."


def mensagem_temperatura(temp):
    """Devolve a mensagem de conforto térmico de acordo com a temperatura em °C."""
    if 17 <= temp <= 25:
        return "Nenhum alerta, temperatura está boa"
    elif 8 <= temp < 17 or 25 < temp <= 36:
        return f"alerta, temperatura em níveis desconfortáveis: {temp}°C"
    else:
        return f"alerta extremo! Temperatura preocupante: {temp}°C"


def tem_dado_pessoal(texto):
    """O relato não pode ter telefone ou documento (CPF, RG).
    Considera suspeito um texto com uma sequência de 8 ou mais dígitos seguidos."""
    seguidos = 0
    for caractere in texto:
        if caractere.isdigit():
            seguidos += 1
            if seguidos >= 8:
                return True
        elif caractere not in ' .-':  # telefone e CPF costumam vir com espaço, ponto ou traço
            seguidos = 0
    return False


# ==== Opções do menu ====
def cadastrar_ponto(pontos):
    """Opção 1: cadastra um novo ponto de ônibus."""
    print('Opção 1 - Cadastrar Ponto de Ônibus')
    print('-----' * 7)

    nome = ler_texto('Digite o nome do ponto: ')
    regiao = ler_regiao('Digite a região (' + ', '.join(REGIOES) + '): ')
    coordenadas = ler_coordenadas('Digite as coordenadas (latitude longitude, ex: -23.54 -46.47): ')
    cobertura = ler_sim_nao('O ponto tem cobertura? (S/N): ')

    novo_ponto = {
        "nome": nome.capitalize(),
        "regiao": regiao,
        "coordenadas": coordenadas,
        "cobertura": cobertura,
        "leituras": [],  # Leituras da opção 4
        "relatos": []  # Relatos da opção 7
    }

    pontos.append(novo_ponto)
    salvar_dados(pontos)
    print('\nPonto cadastrado e salvo com sucesso! Para registrar uma leitura, selecione a opção 4.\n')


def atualizar_ou_remover_ponto(pontos):
    """Opção 2: atualiza um campo de um ponto ou remove o ponto."""
    print('Opção 2 - Atualizar ou Remover Ponto')
    print('-----' * 7)

    if len(pontos) == 0:
        print('Nenhum ponto cadastrado ainda!\n')
        return

    indice = escolher_ponto(pontos)
    if indice == -1:
        return
    ponto_selecionado = pontos[indice]

    print(f'\n--- Ponto Selecionado: {ponto_selecionado["nome"]} ---')
    print('1 - Atualizar informações')
    print('2 - Remover ponto')
    print('3 - Voltar')
    sub_opc = validacao(input('Opção: '))

    if sub_opc == 1:
        print('O que você deseja atualizar?')
        print('1 - Nome')
        print('2 - Região')
        print('3 - Coordenadas')
        print('4 - Cobertura')
        campo = validacao(input('Digite o número do campo: '))

        if campo == 1:
            ponto_selecionado['nome'] = ler_texto('Novo nome: ').capitalize()
            print('Nome atualizado!')
        elif campo == 2:
            ponto_selecionado['regiao'] = ler_regiao('Nova região (' + ', '.join(REGIOES) + '): ')
            print('Região atualizada!')
        elif campo == 3:
            ponto_selecionado['coordenadas'] = ler_coordenadas('Novas coordenadas (latitude longitude): ')
            print('Coordenadas atualizadas!')
        elif campo == 4:
            ponto_selecionado['cobertura'] = ler_sim_nao('O ponto tem cobertura? (S/N): ')
            print('Cobertura atualizada!')
        else:
            print('Campo inválido. Nada foi alterado.\n')
            return

        salvar_dados(pontos)
        print('')

    elif sub_opc == 2:
        if ler_sim_nao(f'Tem certeza que deseja apagar "{ponto_selecionado["nome"]}"? (S/N): '):
            pontos.pop(indice)
            salvar_dados(pontos)
            print('Ponto removido com sucesso!\n')
        else:
            print('Operação cancelada.\n')

    elif sub_opc == 3:
        print('Voltando ao menu...\n')

    else:
        print('Opção inválida. Voltando ao menu...\n')


def listar_pontos(pontos):
    """Opção 3: lista os pontos e mostra os detalhes de um deles."""
    print('Opção 3 - Lista de Pontos')
    print('-----' * 7)

    if len(pontos) == 0:
        print('Nenhum ponto cadastrado ainda!\n')
        return

    indice = escolher_ponto(pontos)
    if indice == -1:
        print('Voltando ao menu...\n')
        return
    ponto_selecionado = pontos[indice]
    latitude, longitude = ponto_selecionado["coordenadas"]

    print('\n' + '=' * 30)
    print(f'DETALHES DO PONTO: {ponto_selecionado["nome"]}')
    print('=' * 30)
    print(f'Região: {ponto_selecionado["regiao"]}')
    print(f'Coordenadas: {latitude}, {longitude}')
    print(f'Possui cobertura (no cadastro): {texto_sim_nao(ponto_selecionado["cobertura"])}')

    print('\n--- Histórico de Leituras ---')
    if len(ponto_selecionado["leituras"]) == 0:
        print('Nenhuma leitura registrada ainda.')
    else:
        for index, leitura in enumerate(ponto_selecionado["leituras"], start=1):
            ic = indice_da_leitura(leitura)
            print(f'  {index}. Temp: {leitura["temperatura"]}°C | Umidade: {leitura["umidade"]}% | '
                  f'Cobertura: {texto_sim_nao(leitura["cobertura"])} | '
                  f'Índice de calor: {ic}°C ({classificar_estado(ic)})')

    print('\n--- Relatos da Comunidade ---')  # Relatos da opção 7
    if len(ponto_selecionado["relatos"]) == 0:
        print('Nenhum relato registrado ainda.')
    else:
        for index, relato in enumerate(ponto_selecionado["relatos"], start=1):
            print(f'  {index}. {relato}')

    print('=' * 30 + '\n')


def registrar_leitura(pontos):
    """Opção 4: registra uma leitura de temperatura, umidade e cobertura em um ponto."""
    print('Opção 4 - Registrar Leitura (Temp, Umid, Cobertura)')
    print('-----' * 7)

    if len(pontos) == 0:
        print('Nenhum ponto cadastrado ainda!\n')
        return

    indice = escolher_ponto(pontos)
    if indice == -1:
        return
    ponto_selecionado = pontos[indice]

    print(f'\n--- Ponto Selecionado: {ponto_selecionado["nome"]} ---')
    print('Iniciando registro de leitura...\n')

    temperatura = ler_float('Digite a temperatura (°C): ', -40, 80)
    umidade = ler_float('Digite a umidade (%): ', 0, 100)
    tem_cobertura = ler_sim_nao('O ponto possui cobertura no momento? (S/N): ')

    nova_leitura = {
        "temperatura": temperatura,
        "umidade": umidade,
        "cobertura": tem_cobertura
    }
    ponto_selecionado["leituras"].append(nova_leitura)
    salvar_dados(pontos)

    ic = indice_da_leitura(nova_leitura)
    print(f'\nLeitura registrada e salva com sucesso! Índice de calor: {ic}°C ({classificar_estado(ic)}).\n')


def estado_atual(pontos):
    """Opção 5: mostra os pontos do mais quente ao mais fresco pela última leitura."""
    print('Opção 5 - Estado Atual')
    print('-----' * 7)

    if len(pontos) == 0:
        print('Nenhum ponto cadastrado ainda!\n')
        return

    com_leitura = []  # Tuplas (índice de calor, nome, região, temperatura)
    sem_leitura = []

    for ponto in pontos:
        if len(ponto["leituras"]) == 0:
            sem_leitura.append(ponto["nome"])
        else:
            ultima = ponto["leituras"][-1]
            com_leitura.append((indice_da_leitura(ultima), ponto["nome"], ponto["regiao"], ultima["temperatura"]))

    if len(com_leitura) == 0:
        print('Nenhum ponto tem leituras ainda. Use a opção 4 para registrar.\n')
    else:
        com_leitura = sorted(com_leitura, reverse=True)  # Mais quente primeiro

        for posicao, (ic, nome, regiao, temp_atual) in enumerate(com_leitura, start=1):
            estado = classificar_estado(ic)
            print(f'{posicao}. {nome} ({regiao}) - Índice de calor: {ic}°C - {estado}')

            if estado != "normal":  # com estado normal, não há aviso de calor para dar
                print(f'   -> Calor: {recomendacao(estado)}')
            print(f'   -> Temperatura: {mensagem_temperatura(temp_atual)}')

    if len(sem_leitura) > 0:
        print('\nSem leituras: ' + ', '.join(sem_leitura))
    print('')


def recomendar_ponto(pontos):
    """Opção 6: recomenda o ponto com menor índice de calor médio de uma região."""
    print('Opção 6 - Recomendação de Ponto')
    print('-----' * 7)

    if len(pontos) == 0:
        print('Nenhum ponto cadastrado ainda!\n')
        return

    regiao_busca = ler_regiao('Digite a região (' + ', '.join(REGIOES) + '): ')

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
        cobertura_txt = texto_sim_nao(melhor_ponto["leituras"][-1]["cobertura"])

        print(f'\nMelhor ponto da região {regiao_busca}: {melhor_ponto["nome"]}')
        print(f'Índice de calor médio: {melhor_ic}°C - {estado}')
        print(f'Cobertura na última leitura: {cobertura_txt}')
        print(f'-> {recomendacao(estado)}\n')


def registrar_relato(pontos):
    """Opção 7: registra um relato do cidadão sobre um ponto (sem dados pessoais)."""
    print('Opção 7 - Registrar Relato')
    print('-----' * 7)

    if len(pontos) == 0:
        print('Nenhum ponto cadastrado ainda!\n')
        return

    indice = escolher_ponto(pontos)
    if indice == -1:
        return
    ponto_selecionado = pontos[indice]

    print(f'\n--- Ponto Selecionado: {ponto_selecionado["nome"]} ---')
    print('Tipo de relato:')
    for i, tipo_relato in enumerate(TIPOS_RELATO, start=1):
        print(f'{i} - {tipo_relato}')

    while True:  # escolhe o tipo
        escolha_tipo = validacao(input('Digite o número do tipo: '))
        if 1 <= escolha_tipo <= len(TIPOS_RELATO):
            tipo = TIPOS_RELATO[escolha_tipo - 1]
            break
        else:
            print('Tipo inválido, tente novamente.')

    while True:  # descrição sem dados pessoais
        descricao = ler_texto('Descreva o ocorrido (sem seus dados pessoais): ')
        if tem_dado_pessoal(descricao):
            print('Erro! Não coloque telefone ou documento no relato.')
        else:
            break

    relato = f'[{date.today().isoformat()}] {tipo}: {descricao}'
    ponto_selecionado["relatos"].append(relato)
    salvar_dados(pontos)
    print('\nRelato registrado e salvo com sucesso. Veja na opção 3.\n')


def mostrar_menu():
    """Mostra o menu principal."""
    print('==== PONTO FRESCO ====')
    print('Encontre seu melhor ponto.')
    print('---' * 8)
    print('1 - Cadastrar Ponto de Ônibus')
    print('2 - Atualizar ou Remover Ponto')
    print('3 - Lista de Pontos')
    print('4 - Registrar Leitura (Temp, Umid, Cobertura)')
    print('5 - Estado Atual')
    print('6 - Recomendação de Ponto')
    print('7 - Registrar Relato')
    print('8 - Sair')
    print('---' * 8)


# ==== Programa principal ====
def main():
    pontos = carregar_dados()  # Lista principal que guarda os dados

    while True:
        mostrar_menu()
        opcao = validacao(input('Digite sua opção: '))
        print('')

        match opcao:
            case 1:
                cadastrar_ponto(pontos)
            case 2:
                atualizar_ou_remover_ponto(pontos)
            case 3:
                listar_pontos(pontos)
            case 4:
                registrar_leitura(pontos)
            case 5:
                estado_atual(pontos)
            case 6:
                recomendar_ponto(pontos)
            case 7:
                registrar_relato(pontos)
            case 8:
                salvar_dados(pontos)
                print('Opção 8 - Sair')
                print('Desligando o sistema...')
                print('Obrigado por ajudar nossa comunidade!')
                break
            case _:
                print('-> Opção inválida, tente novamente! <-\n')


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\n\nPrograma encerrado pelo usuário. Os dados já salvos foram mantidos.')
