# Uso de Inteligência Artificial no projeto

## 1. Ferramentas utilizadas e finalidade

| Ferramenta | Finalidade |
|---|---|
| Claude (Anthropic) | Encontrar e corrigir erros no código (`main.py`) e revisar se o projeto atendia aos requisitos da disciplina |

O grupo usou a IA **apenas para corrigir erros**. A ideia da solução, a lógica do programa, as funcionalidades do menu e a fórmula do índice de calor foram desenvolvidas pelo grupo. Depois de corrigido o código, a IA também ajudou a organizar o texto do `readme.md` e deste arquivo a partir das informações da proposta do grupo.

## 2. Principais prompts utilizados

Os prompts abaixo estão resumidos. Em todos eles o grupo colou junto o trecho do `main.py` com o problema.

**Prompt 1 — Erro ao digitar texto na temperatura**
> Quando eu digito "abc" na temperatura da opção 4, o programa fecha com NameError. Por que isso acontece e como corrigir usando try/except, sem mudar a lógica do programa?

**Prompt 2 — Arquivo JSON vazio ou corrompido**
> Se o arquivo pontos.json estiver vazio, o programa dá JSONDecodeError e fecha. Como faço para ele avisar o usuário e começar com a lista vazia?

**Prompt 3 — Coordenadas com casas decimais**
> Na hora de cadastrar o ponto, as coordenadas -23.54 -46.47 são recusadas. Como ler a latitude e a longitude como números decimais e guardar numa tupla?

**Prompt 4 — Cobertura gravada de formas diferentes**
> A cobertura do ponto está sendo gravada como "S", "Sim" ou "Nao", mas na leitura fica True/False. Como deixar tudo igual?

**Prompt 5 — Filtro de dados pessoais bloqueando relatos**
> O filtro que impede telefone e CPF no relato está bloqueando textos normais como "Ônibus 8012 atrasou 20 min, 14h30". Como ajustar para bloquear só telefone e documento?

**Prompt 6 — Ctrl+C mostrando erro**
> Quando fecho o programa com Ctrl+C aparece uma mensagem de erro enorme. Tem como encerrar de forma limpa?

**Prompt 7 — Revisão final**
> Revise o main.py e aponte erros ou partes que não seguem boas práticas. Confira também se o projeto usa tudo o que a disciplina pede: menu, validação, try/except, if/elif/else, match/case, while, for, funções com parâmetros e retorno, listas, tuplas, dicionários e leitura e gravação de JSON.

## 3. Erros corrigidos com auxílio da IA

| Erro | Correção |
|---|---|
| Na opção 4, digitar um texto como "abc" na temperatura fechava o programa (`NameError`), porque a verificação da faixa ficava fora do `try` | Criada a função `ler_float(mensagem, minimo, maximo)`, que usa `try/except` e repete a pergunta até o valor ser válido |
| A temperatura aceitava o valor "nan", que era gravado no JSON | `ler_float` passou a recusar "nan" |
| Um `pontos.json` vazio ou corrompido fechava o programa (`JSONDecodeError`) | `carregar_dados()` passou a tratar `json.JSONDecodeError` e começa com a lista vazia |
| Coordenadas reais com casas decimais (ex: -23.54 -46.47) eram recusadas, e na atualização não havia validação | Criada a função `ler_coordenadas`, que converte com `float()` e grava a tupla (latitude, longitude) |
| O nome do ponto podia ficar vazio | Criada a função `ler_texto`, que não aceita texto vazio |
| A cobertura do ponto era gravada como texto ("S", "Sim", "Nao") e a das leituras como `True/False` | Criada a função `ler_sim_nao`, e as duas passaram a ser gravadas como `True/False` |
| Espaços antes ou depois da região e do S/N faziam a resposta ser recusada | Uso de `.strip()` em todas as entradas |
| Na opção 2, um campo inválido não mostrava mensagem e não era possível atualizar a cobertura | Mensagem de campo inválido e novo campo "4 - Cobertura" |
| O filtro de dados pessoais bloqueava relatos comuns, como "Ônibus 8012 atrasou 20 min, 14h30" | `tem_dado_pessoal` passou a contar só dígitos seguidos (aceitando espaço, ponto e traço, como em telefone e CPF) |
| Fechar o programa com Ctrl+C mostrava uma mensagem de erro | Tratamento de `KeyboardInterrupt` e `EOFError` no início do programa |
| Boas práticas: menu inteiro fora de funções, tupla de regiões repetida, nome do arquivo repetido e erros de digitação | Cada opção do menu virou uma função, o menu passou a usar `match/case`, e foram criadas as constantes `ARQUIVO_DADOS`, `REGIOES`, `RESPOSTAS_SIM` e `RESPOSTAS_NAO` |

## 4. Como o grupo verificou, testou e ajustou os resultados

- Executamos o programa e repetimos os casos que davam erro antes da correção: texto e "nan" na temperatura, arquivo `pontos.json` vazio, coordenadas com casas decimais, nome vazio, região com espaços e Ctrl+C.
- Testamos cada opção do menu do começo ao fim: cadastro, atualização de cada campo, remoção com confirmação, listagem com detalhes, registro de leitura, estado atual, recomendação por região e registro de relato.
- Conferimos o índice de calor calculado com a tabela do serviço meteorológico dos EUA (NWS). Por exemplo, 33,5 °C com 55% de umidade resulta em 39,0 °C à sombra, o mesmo valor usado no ESP32.
- Lemos cada alteração sugerida para garantir que todos os integrantes saibam explicar o código, e mantivemos apenas os recursos vistos na disciplina, sem bibliotecas externas.

## 5. Análise crítica

**Benefícios:** a IA encontrou rapidamente erros que só aparecem com entradas inesperadas, como texto no lugar de número ou um arquivo JSON vazio, que não tínhamos testado. Ela também mostrou onde o código repetia trechos que podiam virar funções.

**Limitações:** a IA não conhece o contexto do nosso problema nem os testes que fizemos, então cada sugestão precisou ser conferida executando o programa. Algumas sugestões eram mais avançadas que o conteúdo da disciplina e foram simplificadas.

**Dificuldades:** foi preciso entender cada correção antes de aceitá-la, porque o grupo precisa saber explicar todas as linhas do código. Também foi necessário conferir se os valores do índice de calor continuavam iguais aos do ESP32 depois das mudanças.
