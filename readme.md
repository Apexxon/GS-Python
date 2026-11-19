# Ponto Fresco — Central de análise em Python

Global Solution 2026.2 · CitizenTech · Engenharia de Software, 1º ano · Computational Thinking with Python

## Ficha da CitizenTech

| Campo | Conteúdo |
|---|---|
| Nome da CitizenTech | Ponto Fresco |
| Cidade e bairro | São Paulo (SP), Aricanduva (zona leste) |
| Cidadão beneficiado | Pessoas idosas e trabalhadores que esperam ônibus em pontos sem cobertura adequada, nos horários mais quentes do dia |
| Problema, em uma frase | Quem espera ônibus em ponto descoberto fica exposto a calor perigoso sem saber o nível de risco nem onde se proteger. |
| Como funciona | Um ESP32 no ponto mede temperatura e umidade, calcula o índice de calor, classifica o risco em 4 níveis e avisa no local com luz, som e mensagem. Os dados alimentam um sistema que gera o mapa de pontos críticos e recebe relatos dos cidadãos. |
| O que cada parte faz | Sensor (Edge): mede, decide e alerta no ponto · Lógica (Python): histórico, estado atual, recomendação e relatos · Matemática: modelo da temperatura e gatilho do alerta · Interface e Interação (Front-end e Web Dev): mapa, estados e CRUD de relatos · Experiência (STXD): requisitos, jornada e protótipo · Pitch (Storytelling): vídeo e marca |
| Link do repositório | https://github.com/Apexxon/GS-Python |
| Indicador de impacto | Horas de exposição em nível Perigo ou acima por ponto e por dia; número de alertas emitidos antes do pico; relatos resolvidos pela prefeitura |
| ODS conectados | 3 (Saúde e bem-estar), 11 (Cidades e comunidades sustentáveis), 13 (Ação contra a mudança do clima) |

## Integrantes

Grupo APPEXON

| Nome | RM |
|---|---|
| Mateus Rodrigues Tavares | 571189 |
| José Henrique Oliveira de Lira | 569037 |
| Enzo Cassiano Machado | 569630 |
| Matheus Donas Vieira | 568626 |
| Rafael Rosatti de Paula | 571280 |

## Sobre a aplicação

A aplicação Python é a "central de análise" do Ponto Fresco. É um programa de terminal que cadastra pontos de ônibus, registra leituras de temperatura e umidade, calcula o **índice de calor** (a temperatura que o corpo realmente sente) e classifica o risco em quatro estados, usando a **mesma fórmula e os mesmos limites do ESP32**.

### Como o índice de calor é calculado

- Fórmula: regressão de Rothfusz, usada pelo serviço meteorológico dos EUA (NWS/NOAA), com a temperatura convertida para °F e o resultado devolvido em °C. Em dias amenos é usada a fórmula simplificada do NWS, e em dias quentes a regressão completa com os ajustes de umidade baixa e alta.
- Correção de sol: quando o ponto **não tem cobertura** no momento da leitura, somam-se **8 °C**, porque sob sol direto a sensação térmica pode subir até cerca de 8 °C (NWS/NOAA).

### Estados de risco (tupla `LIMITES = (27.0, 32.0, 39.0)`)

| Estado | Índice de calor | Recomendação ao cidadão |
|---|---|---|
| normal | abaixo de 27 °C | Sem risco relevante. Pode esperar tranquilo. |
| atenção | de 27 a 32 °C | Está quente. Beba água enquanto espera. |
| alerta | de 32 a 39 °C | Está quente demais para esperar ao sol. Procure sombra. |
| perigo | 39 °C ou mais | Calor perigoso agora. Procure sombra e água o quanto antes. |

## Funcionalidades (menu)

| Opção | O que faz |
|---|---|
| 1 - Cadastrar Ponto de Ônibus | Nome, região (Leste, Sul, Norte, Oeste ou Centro), coordenadas (latitude e longitude) e se o ponto tem cobertura |
| 2 - Atualizar ou Remover Ponto | Altera nome, região, coordenadas ou cobertura, ou remove o ponto, com confirmação antes de excluir |
| 3 - Lista de Pontos | Lista os pontos e mostra os detalhes de um deles: histórico de leituras com índice de calor e estado, e os relatos da comunidade |
| 4 - Registrar Leitura | Registra temperatura (-40 a 80 °C), umidade (0 a 100%) e cobertura no momento, e mostra o índice de calor calculado |
| 5 - Estado Atual | Ordena os pontos do mais quente para o mais fresco pela última leitura, com o estado, a recomendação de calor (omitida no estado normal) e uma mensagem de conforto térmico pela temperatura do ar |
| 6 - Recomendação de Ponto | Pede a região e indica o ponto com o menor índice de calor médio |
| 7 - Registrar Relato | Registra um relato do cidadão (ônibus atrasou, ponto sem cobertura, bebedouro quebrado, pessoa passando mal, problema de segurança ou outro). Recusa descrições com telefone ou documento |
| 8 - Sair | Salva os dados e encerra o programa |

## Como executar

Requisito: **Python 3.10 ou superior** (o programa usa `match/case`). Não há bibliotecas externas: são usadas apenas `json` e `datetime`, da biblioteca padrão.

```bash
cd GS-Python
python main.py
```

Execute o programa a partir da pasta do projeto, pois os dados são lidos e gravados no arquivo `pontos.json` dessa pasta. Se o arquivo não existir, o programa começa sem pontos e o cria no primeiro cadastro. Se ele estiver vazio ou corrompido, o programa avisa e começa sem pontos, sem encerrar.

## Exemplos de uso

**Registrar uma leitura (opção 4)**

```
Digite sua opção: 4

Opção 4 - Registrar Leitura (Temp, Umid, Cobertura)
-----------------------------------
1 - Av. artur ramos, 107 (Sul)
2 - Av. sapopemba, 9000 (Leste)
...
0 - Voltar ao menu principal
Digite o número do ponto desejado: 2

--- Ponto Selecionado: Av. sapopemba, 9000 ---
Iniciando registro de leitura...

Digite a temperatura (°C): abc
Erro! Digite um número válido (ex: 28.5).
Digite a temperatura (°C): 34
Digite a umidade (%): 50
O ponto possui cobertura no momento? (S/N): N

Leitura registrada e salva com sucesso! Índice de calor: 46.4°C (perigo).
```

**Consultar o estado atual (opção 5), com o `pontos.json` de exemplo**

```
Opção 5 - Estado Atual
-----------------------------------
1. Av. sapopemba, 9000 (Leste) - Índice de calor: 46.4°C - perigo
   -> Calor: Calor perigoso agora. Procure sombra e água o quanto antes.
   -> Temperatura: alerta, temperatura em níveis desconfortáveis: 34.0°C
2. Av. artur ramos, 107 (Sul) - Índice de calor: 32.5°C - alerta
   -> Calor: Está quente demais para esperar ao sol. Procure sombra.
   -> Temperatura: alerta, temperatura em níveis desconfortáveis: 31.5°C
3. Praça da sé (Centro) - Índice de calor: 31.0°C - atenção
   -> Calor: Está quente. Beba água enquanto espera.
   -> Temperatura: alerta, temperatura em níveis desconfortáveis: 29.0°C
4. Av. aricanduva, 4000 (Leste) - Índice de calor: 31.0°C - atenção
   -> Calor: Está quente. Beba água enquanto espera.
   -> Temperatura: alerta, temperatura em níveis desconfortáveis: 30.0°C

Sem leituras: Av. inajar de souza, 1200
```

**Recomendação de ponto (opção 6)**

```
Digite a região (Leste, Sul, Norte, Oeste, Centro): leste

Melhor ponto da região Leste: Av. aricanduva, 4000
Índice de calor médio: 31.0°C - atenção
Cobertura na última leitura: Sim
-> Está quente. Beba água enquanto espera.
```

## Conceitos da disciplina aplicados

| Requisito | Onde aparece |
|---|---|
| Menu de opções | `mostrar_menu()` e o laço principal em `main()` |
| Validação de entradas | `validacao`, `ler_float`, `ler_sim_nao`, `ler_regiao`, `ler_texto`, `ler_coordenadas`, `tem_dado_pessoal` |
| try/except | Conversão de texto em número (`ValueError`), leitura do JSON (`FileNotFoundError`, `json.JSONDecodeError`), gravação (`OSError`) e encerramento com Ctrl+C (`KeyboardInterrupt`, `EOFError`) |
| if/elif/else | `classificar_estado`, `mensagem_temperatura`, validações e submenu da opção 2 |
| match/case | Escolha da opção do menu em `main()` e `recomendacao(estado)` |
| while | Laço do menu e repetição das entradas até serem válidas |
| for | `indice_medio`, listagem de pontos, histórico de leituras e montagem do ranking do estado atual |
| Funções com parâmetros e retorno | `calcular_indice_calor(temp_c, umidade, sol)`, `classificar_estado(ic)`, `recomendacao(estado)`, `indice_medio(leituras)`, `ler_float(mensagem, minimo, maximo)` etc. |
| Listas | Lista de pontos, lista de leituras e lista de relatos de cada ponto |
| Tuplas | `LIMITES`, `REGIOES`, `TIPOS_RELATO`, coordenadas `(latitude, longitude)` e tuplas `(índice, nome, região, temperatura)` do estado atual |
| Dicionários | Cada ponto e cada leitura são dicionários |
| JSON (leitura e gravação) | `carregar_dados()` ao iniciar e `salvar_dados()` após cada alteração e ao sair |

## Estrutura do `pontos.json`

```json
[
    {
        "nome": "Av. sapopemba, 9000",
        "regiao": "Leste",
        "coordenadas": [-23.6005, -46.4920],
        "cobertura": false,
        "leituras": [
            {"temperatura": 33.5, "umidade": 55.0, "cobertura": false}
        ],
        "relatos": [
            "[2026-11-10] Ponto sem cobertura: Ponto só com totem, ao lado de muro, sol direto à tarde"
        ]
    }
]
```

O JSON não tem tuplas, então as coordenadas são gravadas como lista e convertidas para tupla ao carregar.

## Origem dos dados

Todos os dados do `pontos.json` de exemplo são **simulados**: os endereços são apenas referências de vias públicas de São Paulo, e as leituras e os relatos foram criados pelo grupo para teste. Nenhum dado pessoal real é armazenado, e o programa recusa relatos com sequências de números que pareçam telefone ou documento.

## Estrutura do projeto

```
GS-Python/
├── main.py       # código-fonte da aplicação
├── pontos.json   # dados de exemplo (simulados)
├── readme.md     # este arquivo
└── prompts.md    # uso de Inteligência Artificial no projeto
```
