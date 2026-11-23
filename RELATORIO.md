# Relatório — SimES: simulador de E/S e de sistema de arquivos

**Integrantes:** Alice Koepp, Matheus Lima, Filipe Pereira e Júlia Tietbohl

**Repositório:** https://github.com/MathsLima/t2-sisop

## 0. Resumo

Implementamos o núcleo de E/S e de sistema de arquivos, os módulos M1, M2 e M6 e a integração, onde registramos as hipóteses antes da execução oficial final e repetimos os testes e experimentos depois de reaplicar o código. Os resultados apresentados são os CSVs dessa rodada, mas não implementamos o bônus flash.


## 1. Escopo realizado

Grupo de 4 integrantes. Implementamos o núcleo (N1 a N4, com os experimentos X1 a X5), os módulos M1 (cache de blocos, X6), M2 (escalonamento avançado, X7) e M6 (alocação em disco, X11) e a integração ponta a ponta (X12). Não implementamos os módulos M3, M4 e M5 nem o bônus flash.

### Como executamos e registramos os testes

Usamos o ambiente Linux e Python 3.14, mantivemos o código do simulador compatível com Python 3.8 ou superior e não alteramos simes/parametros.py, experimentos.py nem as cargas. Para gerar os gráficos, instalamos matplotlib com python3 -m pip install --user matplotlib, onde essas dependências ficaram no ambiente e não foram adicionadas ao projeto.

Primeiro executamos python3 executar.py testes no esqueleto e registramos 14 erros e 9 testes pulados, relacionados aos TODOs ainda não implementados, o teste de links M4 parava no mkdir. Depois da implementação, repetimos o comando, passaram os 26 testes descobertos, sem falhas, com 4 pulados (M3, M4 e M5 que não escolhemos).

Antes da rodada final, registramos as hipóteses na seção 3, em seguida executamos python3 executar.py experimentos, conferimos resultados/experimentos.csv e as linhas de resultados/es.csv, resultados/arquivos.csv e resultados/arquivos_por_operacao.csv, para X12 conferimos também as 24 combinações nas linhas, não apenas o status geral. Executamos python3 graficos.py e inspecionamos os gráficos gerados. Por fim, executamos python3 ferramentas/validar_entrega.py, que informou 0 erros e 0 avisos. Usamos os CSVs gerados pelos scripts para transcrever os números e as evidências nas seções de cada experimento do RELATORIO.md.

## 2. Implementação

### N2 — Subsistema de E/S

**Onde:** `simes/es/escalonadores.py` (`SSTF`, `SCAN` e M2) e `simes/es/cpu.py` (`custo_cpu`).

**Decisões:** Implementamos SSTF escolhendo a menor distância e preservando a fila em empates, em SCAN atendemos na direção atual e visitamos a borda ao inverter. Para polling usamos a duração do atendimento, para interrupção somamos, por bloco, os custos de interrupção e cópia.

**Dificuldades:** Precisamos respeitar direção, borda e `passar_por` para contabilizar deslocamento e tempo.

### N3 — Sistema de arquivos

**Onde:** `simes/arquivos/sistema.py` (`resolver`, `mkdir`, `create`, `open`, `read`, `write`, `seek`, `close`, `unlink`).

**Decisões:** Implementamos a leitura dos diretórios ao percorrer caminhos e a leitura do diretório pai nas operações que alteram entradas. Compartilhamos o FCB e o contador de aberturas na tabela global, mantendo handle, modo e posição por processo. Em `unlink`, adiamos a liberação até o último `close`.

**Dificuldades:** Coordenamos extensão de arquivo, custos de blocos e vida útil do FCB com as tabelas compartilhadas.

### M1 — Cache de blocos

**Onde:** `simes/es/cache.py`.

**Decisões:** Implementamos LRU atualizando a recência em acertos e escritas, e FIFO mantendo a ordem de chegada. Em write-through gravamos imediatamente, em write-back mantemos blocos sujos até sincronização ou expulsão.

**Dificuldades:** Distinguimos as gravações físicas dos blocos ainda sujos no instante da queda simulada.

### M2 — Escalonamento avançado

**Onde:** `simes/es/escalonadores.py` (`C-SCAN`, `LOOK`, `C-LOOK`, `DEADLINE`).

**Decisões:** Em C-SCAN contabilizamos o percurso à borda e o retorno, em LOOK/C-LOOK evitamos a borda, em DEADLINE atendemos o prazo vencido mais antigo e usamos SSTF antes do vencimento.

**Dificuldades:** Tratamos a volta de C-SCAN e o salto de C-LOOK com custos diferentes, conforme o contrato.

### M6 — Alocação em disco

**Onde:** `simes/arquivos/alocacao.py`.

**Decisões:** Em alocação encadeada contabilizamos leituras dos ponteiros, em FAT mantivemos o mapeamento em memória, em indexada reservamos o índice raiz e os índices secundários necessários, contabilizando leituras e escritas.

**Dificuldades:** Mantivemos a alocação atômica diante de falta de espaço e da passagem do limite de 1.024 blocos por índice.

### Integração ponta a ponta

**Onde:** `simes/integracao.py` (`historico_para_requisicoes`).

**Decisões:** Ordenamos por instante e, em empates, pela ordem original, atribuímos IDs sequenciais e preservamos processo, tipo, bloco e quantidade.

**Dificuldades:** Preservamos a ordem e o instante dos acessos simultâneos do histórico.

## 3. Experimentos

Registramos as hipóteses antes da execução oficial inicial e as mantivemos na rodada final. Depois da reversão temporária do código, reaplicamos as implementações e executamos novamente os testes e experimentos oficiais, os CSVs atuais foram gerados nessa rodada final, não tratamos os resultados antigos como resultados finais.

### X1 — Escalonadores sob quatro padrões de carga

**Hipótese:** Esperávamos que SSTF reduzisse o deslocamento e a resposta média frente a FCFS, sobretudo nas cargas aleatória e concentrada, também esperávamos que SCAN limitasse extremos de espera, possivelmente à custa de deslocamento até a borda.

**Fundamentação:** Baseamos a hipótese em Silberschatz, Galvin e Gagne, 9ª ed., seção 10.4: SSTF favorece requisições próximas e pode postergar as distantes, SCAN percorre o disco em uma direção e retorna.

**Configuração:** Executamos as cargas sequencial, aleatória, concentrada e em rajadas com FCFS/SSTF/SCAN no HDD. Medimos deslocamento, resposta média, p95, maior espera e vazão.

**Resultados:** Obtivemos os seguintes deslocamentos em cilindros, respostas e esperas em ms e vazões em requisições/s.

| Carga | Escalonador | Deslocamento | Resposta média | p95 | Maior espera | Vazão |
|---|---|---:|---:|---:|---:|---:|
| Sequencial | FCFS | 7.184.093 | 10.241,0482 | 19.565,4470 | 20.598,0550 | 61,4760 |
| Sequencial | SSTF | 2.336.365 | 17,3917 | 32,7870 | 37,4370 | 167,4914 |
| Sequencial | SCAN | 2.469.069 | 23,2085 | 43,6500 | 48,5860 | 167,4079 |
| Aleatória | FCFS | 3.316.472 | 50,1041 | 145,0860 | 193,5170 | 82,4516 |
| Aleatória | SSTF | 2.631.714 | 20,9874 | 48,6060 | 116,6530 | 82,4516 |
| Aleatória | SCAN | 3.372.680 | 31,5329 | 65,0610 | 116,7270 | 82,3617 |
| Concentrada | FCFS | 1.864.164 | 19,7984 | 48,5660 | 96,0230 | 83,8093 |
| Concentrada | SSTF | 1.613.030 | 15,0220 | 37,2030 | 130,5190 | 83,8093 |
| Concentrada | SCAN | 3.338.708 | 33,1956 | 68,3310 | 118,7520 | 83,7035 |
| Rajadas | FCFS | 3.341.490 | 266,9744 | 505,3230 | 597,2910 | 83,4633 |
| Rajadas | SSTF | 209.811 | 147,4873 | 277,7160 | 296,9910 | 84,4214 |
| Rajadas | SCAN | 199.955 | 148,6205 | 278,7010 | 285,4420 | 84,4250 |

**Evidências:** Consultamos `resultados/experimentos.csv` e `resultados/es.csv` com `experimento=X1`, além de `graficos/X1_resposta_media_ms.png`.

**Análise:** Observamos que SSTF reduziu o deslocamento e a resposta média frente a FCFS nas quatro cargas. Na concentrada, porém, medimos espera máxima de 130,519 ms para SSTF, acima de FCFS (96,023 ms) e SCAN (118,752 ms), o que ilustra o risco de postergar cilindros distantes. Em rajadas, SCAN teve menor deslocamento e espera máxima que SSTF, com resposta média quase igual. A resposta média alta de FCFS na carga chamada sequencial mostra que a ordem temporal de chegada não garante a ordem física dos blocos. Em sistemas reais, o Linux não usa SSTF puro justamente por causa dessa inanição: o `mq-deadline` combina ordenação por posição com prazos de leitura e de escrita, e o `none` é o usual em SSDs, onde a posição do bloco não altera o custo.

**Veredito:** PARCIALMENTE CONFIRMADA

### X2 — Polling × interrupção conforme o dispositivo

**Hipótese:** Esperávamos que polling gastasse mais CPU no HDD por causa da duração mecânica e que, no dispositivo rápido, os custos fixos de interrupção/cópia por bloco pudessem superar a espera curta de polling.

**Fundamentação:** Baseamos a hipótese nas seções 13.2.1 e 13.2.2 de Silberschatz, Galvin e Gagne: o tempo do dispositivo determina a relação entre espera ocupada e tratamento de interrupção.

**Configuração:** Executamos as cargas aleatória e sequencial em HDD e dispositivo rápido com FCFS e polling/interrupção. Medimos CPU de E/S (%).

**Resultados:** Obtivemos os seguintes percentuais de CPU de E/S.

| Dispositivo | Carga | Polling (%) | Interrupção (%) |
|---|---|---:|---:|
| HDD | Aleatória | 86,2832 | 1,1213 |
| HDD | Sequencial | 99,9977 | 0,8361 |
| Rápido | Aleatória | 0,5280 | 1,1219 |
| Rápido | Sequencial | 1,0739 | 2,2821 |

**Evidências:** Consultamos `resultados/experimentos.csv` e `resultados/es.csv` com `experimento=X2`, além de `graficos/X2_cpu.png`.

**Análise:** Medimos 86,28–100,00% de CPU para polling no HDD, contra 0,84–1,12% para interrupções. No dispositivo rápido, observamos o inverso: o custo fixo por bloco da interrupção superou o breve atendimento em polling, chegando a 2,28% contra 1,07%. Interpretamos isso como consequência das fórmulas do modelo, não como medição de CPU real. Nos sistemas reais a regra é parecida: o Linux, o Windows e o macOS atendem discos por interrupção, e a espera ocupada só aparece onde a latência é muito curta, como nas filas de E/S com polling de dispositivos NVMe no Linux.

**Veredito:** CONFIRMADA

### X3 — Acesso sequencial × direto

**Hipótese:** Esperávamos que a carga sequencial do compilador acessasse blocos fisicamente próximos e reduzisse o tempo por operação em relação ao acesso direto do banco de dados, prevíamos que os blocos acessados por operação poderiam ser semelhantes.

**Fundamentação:** Baseamos a hipótese na seção 11.2 (métodos de acesso) e na seção 10.4 (localidade e custo de disco) de Silberschatz, Galvin e Gagne.

**Configuração:** Executamos as cargas oficiais do compilador e do banco de dados com alocação contígua. Comparamos acessos e tempo médios por operação.

**Resultados:** Obtivemos as seguintes médias por operação nas cargas oficiais.

| Carga | Operação | N | Acessos/op (blocos) | Tempo/op (ms) |
|---|---|---:|---:|---:|
| Compilador | read | 1.719 | 1,0000 | 1,4828 |
| Banco de dados | read | 2.405 | 1,0000 | 5,4918 |
| Compilador | write | 726 | 1,0000 | 0,9068 |
| Banco de dados | write | 1.190 | 1,0000 | 5,5425 |

**Evidências:** Consultamos `resultados/experimentos.csv`, `resultados/arquivos.csv` e `resultados/arquivos_por_operacao.csv` com `experimento=X3`, além de `graficos/X3_tempo_por_operacao.png`.

**Análise:** Observamos uma média de um bloco por operação nas duas cargas, mas as leituras do banco de dados levaram 3,70 vezes o tempo por operação do compilador e as escritas, 6,11 vezes. Como a contagem de acessos por bloco não registra busca e rotação, interpretamos essa diferença como coerente com a localidade sequencial da carga de compilação e os acessos diretos do banco. Nos sistemas reais, o acesso sequencial é ainda mais favorecido, porque o Linux detecta a leitura sequencial e faz readahead no cache de páginas, o que o SimES não modela.

**Veredito:** CONFIRMADA

### X4 — Custo de resolver caminhos conforme a profundidade

**Hipótese:** Esperávamos que cada diretório adicional acrescentasse uma leitura ao `open` e que o tempo também crescesse no HDD, condicionado pela posição física dos blocos.

**Fundamentação:** Baseamos a hipótese na seção 11.3 (estrutura de diretórios) e na seção 10.4 de Silberschatz, Galvin e Gagne.

**Configuração:** Executamos `open` em caminhos com profundidades de 1 a 10 diretórios e medimos acessos e tempo médios.

**Resultados:** Medimos 2 acessos e 4,25 ms por `open` na profundidade 1, e 11 acessos e 4,61 ms na profundidade 10. Nesta carga, cada diretório adicional acrescentou uma leitura e cerca de 0,04 ms.

**Evidências:** Consultamos `resultados/experimentos.csv` e `resultados/arquivos_por_operacao.csv` com `experimento=X4` e `operacao=open`, além de `graficos/X4_open_por_profundidade.png`.

**Análise:** Observamos que as leituras cresceram linearmente, uma por nível. O tempo também cresceu linearmente neste caso porque os blocos físicos estavam próximos, outros posicionamentos podem alterar o tempo sem mudar o número de leituras. No Linux, o cache de nomes (dcache) mantém na memória os componentes já resolvidos, e por isso aberturas repetidas do mesmo caminho raramente leem os diretórios do disco; o SimES não tem esse cache e cobra a leitura de cada nível.

**Veredito:** CONFIRMADA

### X5 — Tabelas de arquivos abertos com vários processos

**Hipótese:** Esperávamos uma entrada global por arquivo distinto, registros de cada abertura nas tabelas por processo e contadores globais maiores que um quando vários processos abrissem o mesmo arquivo.

**Fundamentação:** Baseamos a hipótese na seção 11.1.3 (arquivos abertos) de Silberschatz, Galvin e Gagne.

**Configuração:** Executamos a carga oficial de servidor web e registramos os máximos das tabelas global e por processo e do contador de aberturas.

**Resultados:** Processamos 6.279 operações sem erros. Medimos máximos de 12 entradas na tabela global, 3 na tabela de um processo, 24 na soma das tabelas por processo e 6 no contador global de aberturas.

**Evidências:** Consultamos `resultados/experimentos.csv` e `resultados/arquivos.csv` com `experimento=X5`, além de `graficos/X5_tabelas.png`.

**Análise:** Observamos que as aberturas por processo são contabilizadas separadamente, embora várias possam apontar ao mesmo FCB global. Os máximos podem ocorrer em instantes diferentes da carga. Essa organização é a dos sistemas Unix: cada processo tem sua tabela de descritores, o kernel mantém uma tabela global de arquivos abertos com contador de referências e os arquivos em si são identificados por i-nodes; o Windows usa estrutura equivalente, com tabela de handles por processo.

**Veredito:** CONFIRMADA

### X6 — Cache de blocos (M1)

**Hipótese:** Esperávamos que a capacidade elevasse os acertos até saturar e que LRU favorecesse a localidade recente. Também esperávamos que write-back reduzisse gravações físicas, mas pudesse perder blocos sujos na queda, enquanto write-through não deixaria blocos sujos.

**Fundamentação:** Baseamos a hipótese na seção 13.4.3 (cache) e na seção 12.6 (desempenho) de Silberschatz, Galvin e Gagne.

**Configuração:** Executamos a carga de reuso com LRU/FIFO, capacidades de 64 a 2.048 blocos e políticas write-through/write-back. Usamos o instante de queda definido pelo código oficial e medimos acertos, gravações físicas e blocos sujos perdidos.

**Resultados:** Obtivemos os seguintes acertos (%), gravações físicas e blocos perdidos na queda com write-back.

| Cache | Capacidade | Acerto | Gravações | Perdidos |
|---|---:|---:|---:|---:|
| LRU | 64 | 39,6419 | 715 | 28 |
| LRU | 128 | 49,1049 | 630 | 51 |
| LRU | 256 | 57,6982 | 543 | 55 |
| LRU | 512 | 64,2455 | 541 | 55 |
| LRU | 1.024 | 67,0077 | 541 | 55 |
| LRU | 2.048 | 67,0077 | 541 | 55 |
| FIFO | 64 | 33,0946 | 810 | 22 |
| FIFO | 128 | 43,8875 | 706 | 46 |
| FIFO | 256 | 53,2992 | 607 | 50 |
| FIFO | 512 | 60,1023 | 567 | 50 |
| FIFO | 1.024 | 67,0077 | 541 | 55 |
| FIFO | 2.048 | 67,0077 | 541 | 55 |

Com write-through, executamos 1.045 gravações físicas em cada capacidade e não perdemos blocos sujos. A taxa de acerto também cresceu e chegou a 67,0588%.

**Evidências:** Consultamos `resultados/experimentos.csv` e `resultados/es.csv` com `experimento=X6`, além de `graficos/X6_acerto.png` e `graficos/X6_escrita.png`.

**Análise:** Observamos que a capacidade elevou os acertos até saturar em 1.024 blocos. LRU superou FIFO nas capacidades menores e empatou nas maiores. Write-back reduziu as gravações físicas, mas perdemos até 55 blocos sujos, write-through gravou imediatamente e não perdeu blocos. A perda dependeu da quantidade ainda suja no instante fixo da queda. Nos sistemas reais, o Linux e o Windows usam write-back no cache de páginas, com gravação periódica em segundo plano (threads de flush no Linux, lazy writer no Windows), e por isso o risco de perder dados sujos numa queda de energia existe; as aplicações o reduzem com `fsync` ou com abertura em modo write-through.

**Veredito:** CONFIRMADA

### X7 — Escalonadores avançados e inanição (M2)

**Hipótese:** Esperávamos que, com carga crescente, SSTF mantivesse média baixa e piorasse a cauda, que DEADLINE reduzisse a espera de solicitações vencidas, possivelmente com custo na média, e que SCAN e variantes apresentassem outra relação entre deslocamento e espera.

**Fundamentação:** Baseamos a hipótese na seção 10.4 de Silberschatz, Galvin e Gagne e na regra do esqueleto que força DEADLINE a atender quando o prazo vence.

**Configuração:** Geramos 2.000 requisições concentradas com semente 7 e intervalos médios de 14, 11, 9 e 8 ms. Comparamos FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK e DEADLINE pelas médias, p95 e maior espera.

**Resultados:** Obtivemos as seguintes respostas médias, p95 e maiores esperas (ms) nos intervalos médios de 14 ms e 8 ms.

| Escalonador | 14 ms | 8 ms |
|---|---:|---:|
| FCFS | 15,764 / 41,333 / 71,290 | 281,641 / 538,024 / 616,175 |
| SSTF | 13,390 / 31,979 / 86,649 | 27,776 / 79,571 / 327,061 |
| SCAN | 29,508 / 57,326 / 114,371 | 49,006 / 116,556 / 226,736 |
| C-SCAN | 40,083 / 78,925 / 116,925 | 65,837 / 142,062 / 223,102 |
| LOOK | 13,756 / 33,191 / 72,792 | 31,406 / 87,499 / 170,318 |
| C-LOOK | 14,678 / 37,026 / 102,812 | 38,916 / 100,196 / 163,837 |
| DEADLINE | 13,390 / 31,979 / 86,649 | 28,411 / 84,775 / 244,840 |

**Evidências:** Consultamos `resultados/experimentos.csv` e `resultados/es.csv` com `experimento=X7`, além de `graficos/X7_resposta_p95_ms.png` e `graficos/X7_espera_max_ms.png`.

**Análise:** Observamos que FCFS degradou fortemente com a carga maior. DEADLINE igualou SSTF quando nenhum prazo vencia, como nos 14 ms; no intervalo de 9 ms (valores em `resultados/es.csv`), reduzimos a espera máxima de 265,509 para 204,246 ms. A 8 ms, reduzimos de 327,061 para 244,840 ms, mas a espera ainda superou a de SCAN, C-SCAN, LOOK e C-LOOK. Concluímos que DEADLINE reduziu a espera frente a SSTF, sem garantir a menor espera máxima entre todos. O `mq-deadline` do Linux segue a mesma ideia, mas com prazos próprios para leituras e para escritas (as leituras têm prazo menor) e filas separadas por direção, o que o nosso DEADLINE simplificado não reproduz.

**Veredito:** PARCIALMENTE CONFIRMADA

### X11 — Métodos de alocação (M6)

**Hipótese:** Esperávamos que contígua tivesse baixo custo de mapeamento, mas risco de fragmentação/realocação, que encadeada cobrasse navegação aleatória, que FAT evitasse leituras de ponteiros em disco neste modelo, e que indexada cobrasse acessos aos índices.

**Fundamentação:** Baseamos a hipótese nas seções 12.4 e 12.5 de Silberschatz, Galvin e Gagne, sobre métodos de alocação e espaço livre.

**Configuração:** Executamos a carga `alocacao` em uma partição com 20.000 blocos e comparamos contígua, encadeada, FAT e indexada. Medimos acessos, tempo, realocações, falhas e espaço livre.

**Resultados:** Obtivemos os seguintes indicadores na carga de alocação.

| Alocador | Acessos/op | Tempo médio/op (ms) | Segmentos livres | Maior segmento | Realocações | Falhas |
|---|---:|---:|---:|---:|---:|---:|
| Contígua | 7,3545 | 34,5517 | 50 | 154 | 59 | 113 |
| Encadeada | 77,5158 | 12,7280 | 1 | 1.939 | 0 | 0 |
| FAT | 1,9003 | 4,0058 | 1 | 1.939 | 0 | 0 |
| Indexada | 4,2889 | 14,3215 | 1 | 1.805 | 0 | 0 |

**Evidências:** Consultamos `resultados/experimentos.csv`, `resultados/arquivos.csv` e `resultados/arquivos_por_operacao.csv` com `experimento=X11`, além de `graficos/X11_alocacao.png` e `graficos/X11_fragmentacao.png`.

**Análise:** Observamos que a alocação contígua preservou a contiguidade dos arquivos alocados, mas terminou com 50 segmentos e 113 falhas apesar de ainda haver 2.052 blocos livres, o maior segmento tinha 154 blocos. A alocação encadeada exigiu muitos acessos a ponteiros. FAT foi mais barata neste modelo porque mantivemos os ponteiros em memória, indexada teve custo intermediário de metadados. Consideramos que o modelo não atribui à FAT o custo de persistir/sincronizar a tabela. Nos sistemas reais, a FAT dos pendrives (FAT32 e exFAT) mantém a tabela no disco e a coloca em cache na memória, e é por isso que ela é lenta para arquivos grandes fragmentados e frágil a remoções sem ejetar; o ext4 e o NTFS usam alocação por extents, que se aproxima da alocação contígua com a flexibilidade da indexada.

**Veredito:** PARCIALMENTE CONFIRMADA

### X12 — Integração ponta a ponta

**Hipótese:** Esperávamos que alocação e cache alterassem a sequência e o custo das requisições, que LRU reduzisse acessos repetidos quando houvesse localidade e que as diferenças entre escalonadores dependessem da carga e da disposição física.

**Fundamentação:** Baseamos a hipótese na seção 10.4 e nas seções 12.4–12.6 de Silberschatz, Galvin e Gagne.

**Configuração:** Executamos as cargas do compilador e do banco de dados com alocação contígua/indexada, FCFS/SSTF/SCAN e sem cache/LRU de 1.024 blocos em write-back. Conferimos as 24 combinações nas linhas do CSV.

**Resultados:** Confirmamos status `ok`, 24 execuções e 24 combinações distintas: 2 cargas × 2 alocadores × 3 escalonadores × 2 opções de cache. A tabela mostra a média simples entre os três escalonadores da resposta média (ms) e do deslocamento total (cilindros), além da taxa de acerto LRU média.

| Carga + alocação | Cache | Resposta média (ms) | Deslocamento total médio (cilindros) | Acertos (%) |
|---|---|---:|---:|---:|
| Compilador + contígua | Nenhuma | 5.103,7086 | 2.306,67 | — |
| Compilador + contígua | LRU | 0,4408 | 16.726,67 | 90,3985 |
| Compilador + indexada | Nenhuma | 12.029,4288 | 3.598,00 | — |
| Compilador + indexada | LRU | 0,3549 | 13.401,33 | 95,7142 |
| Banco de dados + contígua | Nenhuma | 4.773,3567 | 127.361,33 | — |
| Banco de dados + contígua | LRU | 1.648,5318 | 101.290,67 | 4,9572 |
| Banco de dados + indexada | Nenhuma | 18.950,8008 | 308.340,67 | — |
| Banco de dados + indexada | LRU | 589,2584 | 102.124,67 | 74,5272 |

**Evidências:** Consultamos `resultados/experimentos.csv` e as 24 linhas de `resultados/es.csv` com `experimento=X12`, além de `graficos/X12_resposta.png`.

**Análise:** Conferimos todas as 24 combinações. LRU reduziu a resposta média agregada nos quatro pares de carga/alocação. Os acertos variaram com a localidade: medimos 4,96% no banco contíguo e 74,53% no banco indexado. Também observamos que a relação entre resposta e deslocamento não foi uniforme: no compilador, o deslocamento total médio aumentou com LRU, no banco, diminuiu. Portanto, interpretamos resposta, deslocamento e acertos em conjunto, sem concluir que a cache sempre reduz o movimento do braço. Sem cache, a alocação indexada teve maior resposta média nesta carga, coerente com os acessos aos índices. As médias agrupadas não isolam o efeito de cada escalonador, para essa comparação, consultamos cada linha individual. Essa ordem de camadas é a dos sistemas reais: o cache de páginas fica acima do escalonador de E/S, de modo que só as requisições que falham no cache chegam ao escalonador, e por isso o cache pode mudar o padrão de acessos que o escalonador enxerga.

**Veredito:** PARCIALMENTE CONFIRMADA

## 4. Relação com sistemas reais

Ao relacionarmos nossos resultados de escalonamento com o Linux, consultamos a documentação de `blk-mq`, das filas de software/hardware e dos schedulers BFQ e deadline, também consideramos o despacho `none`. A camada pode fundir requisições adjacentes e despachar sem reordenação. Nosso SimES usa fila única e HDD serial, portanto não mede paralelismo, fusão de requisições ou drivers. O prazo simplificado de DEADLINE não reproduz o `mq-deadline` do kernel.

Ao compararmos a resolução de caminhos, observamos que o VFS Linux percorre componentes e usa dcache, enquanto o Windows organiza arquivos e diretórios hierarquicamente. O custo fixo por diretório do SimES não representa caches de nomes, concorrência nem revalidação de arquivos remotos.

Ao discutirmos cache e sistemas de arquivos, consultamos a documentação da Microsoft: o cache de arquivos do Windows é write-back por padrão, com lazy writer e opções write-through. No M1, simplificamos isso em políticas FIFO/LRU e sincronização por intervalo fixo. No macOS, o APFS oferece clones, snapshots, compartilhamento de espaço e arquivos esparsos, recursos que não simulamos. Nossos métodos FAT/indexado não equivalem a FAT/exFAT, NTFS, ext4 ou APFS de produção. A documentação ext4 descreve grupos de blocos e heurísticas para reduzir fragmentação, não o modelo contíguo simples deste trabalho.

## 5. Limitações do simulador

- Consideramos que a busca linear, a meia-volta fixa e a transferência constante não representam variação física, firmware, NCQ ou concorrência.
- Nosso modelo usa fila de disco serial, sem fusão de requisições, paralelismo, cache de diretórios ou paginação.
- Contabilizamos CPU por fórmulas constantes, não medimos sobreposição nem escalonamento real.
- Simulamos sincronização de cache fixa e uma única queda, sem persistência nem recuperação.
- Implementamos DEADLINE e os alocadores segundo regras didáticas, não como reproduções integrais de um kernel ou filesystem comercial.
- Na integração, convertemos históricos em eventos, mas não simulamos concorrência entre filesystem e driver.

## 6. Conclusões

1. Concluímos que a resposta média sozinha não representa a espera máxima nem a justiça.
2. Observamos que o custo relativo de polling e interrupção depende da duração do dispositivo e dos custos fixos por bloco do modelo.
3. Medimos que write-back reduz gravações físicas mas mantém dados sujos até a sincronização ou a queda.
4. Concluímos que os métodos de alocação deslocam custos entre metadados, acessos diretos e fragmentação.
5. Em X12, as médias agrupadas escondem o efeito de cada escalonador, por isso conferimos as 24 combinações linha a linha e não apenas o status geral.

## 7. Referências

Consultamos as seguintes referências:

- SILBERSCHATZ, A. GALVIN P. B., GAGNE, G. *Operating System Concepts*. 9. ed. Wiley, 2013. Seções 10.4, 11.1.3, 11.2, 11.3, 12.4–12.6 e 13.2, 13.4.3.
- Linux Kernel Documentation. *blk-mq*. https://docs.kernel.org/block/blk-mq.html
- Linux Kernel Documentation. *Block*. https://docs.kernel.org/block/index.html
- Linux Kernel Documentation. *Pathname lookup*. https://docs.kernel.org/filesystems/path-lookup.html
- Linux Kernel Documentation. *ext4 High Level Design*. https://docs.kernel.org/filesystems/ext4/overview.html
- Microsoft Learn. *Local File Systems*. https://learn.microsoft.com/en-us/windows/win32/fileio/file-systems
- Microsoft Learn. *File Caching*. https://learn.microsoft.com/en-us/windows/win32/fileio/file-caching

## 8. Declaração de autoria e uso de IA

**Uso de ferramentas de IA:**
- **GitHub Copilot (Codespaces):** auxiliou no entendimento inicial do trabalho e na revisão do `RELATORIO.md`.
- **Claude Code (Anthropic):** auxiliou a ajustar o `RELATORIO.md`
