import json
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

pontos = carregar_dados() # Lista principal que guarda os dados

# Código

while True:
    print('==== PONTO FRESCO ====')
    print('Encontre seu melhor ponto.')
    print('---'*8)
    print('1 - Cadastrar Ponto de Onibus')
    print('2 - Atualizar ou Remover ponto')
    print('3 - Lista de Pontos')
    print('4 - Registrar Leitura (Temp, Umid, Cobertura)')
    print('5 - Estado Atual')
    print('6 - Recomendação de Ponto')
    print('7 - Registrar Relato')
    print('8 - Sair')
    print('---'*8)

    opcao = input('Digite sua opção: ')
    opcao = validacao(opcao)

    if opcao not in (1, 2, 3, 4, 5, 6, 7, 8):
        print('')
        print('-> Opção inválida, tente novamente! <-')
        print('')

    elif opcao == 1:

        print('Opção 1 - Cadastrar Ponto de Onibus')
        print('-----'*7)

        nome = input('Digite o nome do ponto: ')

        while True: # CHECA SE A REGIÃO EXISTE (Ex: Sul, Norte, Centro, Etc.)
            regiao = input('Digite a região: ')
            if regiao.capitalize() not in ('Leste', 'Sul', 'Norte', 'Oeste', 'Centro'):
                print('Região inválida. Tente novamente!')
            else:
                break

        while True:  # CHECA SE AS COORDENADAS SÃO NÚMEROS
            coordenadas = input('Digite as coordenadas: ').strip()
            if coordenadas != '':
                break
            else:
                print('Erro! Coordenadas não podem estar vazias. Tente novamente!')

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

                            # Remove o ponto da lista pelo índice

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

                    print('\n--- Relatos da Comunidade ---') # Relatos da opção 7

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

                    while True: # Pega a temperatura
                        try:
                            temperatura = float(input('Digite a temperatura (°C): ').strip())
                            break
                        except ValueError:
                            print('Erro! Digite um valor de temperatura válido (ex: 28.5 ou -2).')

                    while True: # PEga a umidade
                        try:
                            umidade = float(input('Digite a umidade (%): ').strip())
                            if 0 <= umidade <= 100:
                                break
                            else:
                                print('Erro! A umidade deve estar entre 0 e 100.')
                        except ValueError:
                            print('Erro! Digite um valor de umidade válido.')

                    while True: # Pega a cobertura do ponto
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


    elif opcao == 5: # Estado atual compara a temperatura de todas e retorna um estado (critico, favoravel, etc)
        print('5')
    elif opcao == 6: # Recomendação de Ponto, pergunta sua região e te dá o ponto com condições mais favoraveis (temp entre 16 a 30 graus em média; umidade boa; tem cobertura)
        print('6')
    elif opcao == 7: # Registra um relato que é mais uma descrição sobre um ocorrido (onibus atrasou/assalto/tals)
        print('7')

    elif opcao == 8:

        print('Opção 8 - Sair')

        print('Desligando o sistema...')
        print('Obrigado por ajudar nossa Comunidade!')
        break