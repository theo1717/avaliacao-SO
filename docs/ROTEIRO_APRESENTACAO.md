# Roteiro de Apresentação — Banco Nexus

Script cronometrado (~17 minutos) para demonstração oral do simulador à banca. Cada bloco indica o que falar, o que executar no terminal e qual requisito do **item 3 do enunciado** destacar.

Consulte o [Guia de Uso](GUIA_DE_USO.md) para detalhes de cada fluxo.

---

## Preparação (antes de entrar na sala)

```bash
pip install -r requirements.txt
python main.py
```

- [ ] Terminal em tela cheia, fonte legível
- [ ] Modo expediente ativado: `7` → modo expediente → `s` → Enter
- [ ] Testar que `python -m pytest tests/ -v` passa (15 testes) — caso perguntem sobre validação

---

## Visão geral do roteiro

| Minutos | Bloco | Fluxo | Requisito destacado |
|---|---|---|---|
| 0–2 | Abertura e contexto | Banner + contas | Tema + interface |
| 2–7 | Central com Prioridade | A (`1→2→2`) | 3a, 3c |
| 7–9 | Central com EDF | A (`1→3→1`) | 3a deadline, 3c |
| 9–11 | Auditoria de saldo | C (`3→1`, `3→2`) | 3d |
| 11–13 | Esteira de transações | F (`6`) | 3e, 3d semáforo |
| 13–15 | Transferências / deadlock | D (`4→1`, `4→2`) | 3e deadlock |
| 15–17 | Threads + encerramento | B (`2`) + Painel (`8`) | 3b, métricas |

---

## Bloco 1 — Abertura (0–2 min)

### Executar

O sistema já deve estar em `python main.py`. Mostre a tela inicial.

### Falar

> "Este é o **Banco Nexus**, nosso simulador de Sistema Operacional em tempo real com temática bancária. Cada **transação** na fila representa um **processo** com PCB completo — protocolo, prioridade, tempo de execução, estado e prazo. Os **caixas eletrônicos** e o **processador backend** são **threads reais** do Python."

Aponte o painel de contas:

> "Temos três contas ativas — Alice, Bob e Carlos — que serão usadas nos cenários de concorrência e deadlock."

### Requisitos cobertos

- Tema do projeto (simulador SO tempo real, temática bancária)
- Interface terminal com menus navegáveis

### Se perguntarem sobre código

- Menu e interface: `src/ui/menu.py`, `src/ui/display.py`
- PCB: `src/core/process.py`

---

## Bloco 2 — Central de Processamento com Prioridade (2–7 min)

### Executar

```
1 → 2 → 2
```

(Prioridade, modo passo a passo)

Pressione **Enter** a cada ciclo para avançar. Avance 4–6 ciclos — suficiente para mostrar a fila mudando.

### Falar

> "Na **Central de Processamento**, as operações entram na fila e o escalonador decide qual atender. Estou usando **escalonamento por prioridade**: clientes **Private** — nosso equivalente a VIP — são atendidos antes dos perfis Corrente e Backoffice."

Aponte a tabela:

> "Aqui vemos o **protocolo** — que é o PID —, o tipo de transação, o **perfil de prioridade**, a **situação** do processo e o tempo restante. Quando uma operação fica **suspensa**, ela foi **bloqueada** — por exemplo, porque a conta está em uso por outra transação."

Aponte a fila:

> "Esta é a **fila de execução** — a ordem em que as operações aguardam processamento."

Aponte o mapa de cache:

> "Cada operação também precisa de **memória** — quadros de cache — para armazenar dados da transação. Se não houver quadros livres, a operação é bloqueada."

Deixe a simulação terminar ou pressione Enter até o Painel Gerencial aparecer:

> "No **Painel Gerencial** temos as métricas exigidas: tempo de espera, tempo de resposta, transações concluídas e prazos não cumpridos."

### Requisitos cobertos

| Item 3 | O que mostrar |
|---|---|
| **3a** Criação de processos | Operações geradas automaticamente |
| **3a** Estados | Na fila → Processando → Suspensa → Concluída |
| **3a** Bloqueio/desbloqueio | Operações suspensas com motivo |
| **3a** Prioridades | Coluna Perfil |
| **3a** PCB completo | Protocolo, Perfil, Situação, Rest., Prazo |
| **3c** Escalonamento | Prioridade (1 de 3 algoritmos) |
| **3c** Fila, espera, resposta, concluídos | Fila + Painel Gerencial |

### Se perguntarem sobre código

- `src/core/process_manager.py` — criar, bloquear, desbloquear
- `src/core/scheduler.py` — `PriorityScheduler`
- `src/core/metrics.py` — métricas

---

## Bloco 3 — EDF e deadline (7–9 min)

### Executar

```
1 → 3 → 1
```

(EDF, modo automático — rápido com modo expediente)

### Falar

> "O terceiro escalonador é o **EDF — Earliest Deadline First**. Operações com **prazo mais próximo** são atendidas primeiro. O campo **Prazo** no PCB é o **deadline** — exigido pelo enunciado como alternativa ao quantum."

> "Temos três algoritmos implementados: **Round Robin**, **Prioridade** e **EDF** — todos com implementação própria, sem bibliotecas de escalonamento prontas."

### Requisitos cobertos

| Item 3 | O que mostrar |
|---|---|
| **3a** Deadline | Coluna Prazo; EDF usa deadline na seleção |
| **3c** 2+ escalonadores | Terceiro algoritmo demonstrado |

### Se perguntarem sobre código

- `src/core/scheduler.py` — `EDFScheduler`

---

## Bloco 4 — Auditoria de Integridade (9–11 min)

### Executar

Primeiro a falha:

```
3 → 1
```

Depois o sucesso:

```
3 → 2
```

### Falar (após opção 1 — sem mutex)

> "Na **Auditoria de Integridade**, simulamos **quatro caixas creditando simultaneamente** na mesma conta. Sem **trava de segurança** — o mutex — o saldo final fica **incorreto**. Isso é a **condição de corrida**: threads acessam o recurso compartilhado sem exclusão mútua."

### Falar (após opção 2 — com mutex)

> "Com o **mutex** ativado, o mesmo cenário produz o saldo **correto** de R$ 400,00. O mutex garante que apenas uma thread altere o saldo por vez."

### Requisitos cobertos

| Item 3 | O que mostrar |
|---|---|
| **3d** Mutex | Com vs sem proteção |
| **3d** Condição de corrida | Saldo incorreto vs correto |
| **3d** Recurso compartilhado | Saldo da conta |
| **3b** Threads | 4 threads simultâneas |

### Opcional (se sobrar tempo)

```
3 → 3    (log sem proteção)
3 → 4    (log com proteção)
```

> "O mesmo princípio se aplica ao **livro-razão** — gravação concorrente em arquivo de log."

### Se perguntarem sobre código

- `src/concurrency/sync_primitives.py` — `BankMutex`, `SharedBalance`

---

## Bloco 5 — Esteira de Transações (11–13 min)

### Executar

```
6
```

### Falar

> "A **Esteira de Transações** implementa o padrão **produtor-consumidor**. Dois **ATMs produzem** transações e um **processador backend consome**. O buffer tem capacidade limitada — quando enche, o ATM **bloqueia** até haver espaço."

> "Usamos **semáforos** para controlar vagas no buffer e **mutex** para proteger a região crítica. Isso atende o requisito de **sincronização** do enunciado."

### Requisitos cobertos

| Item 3 | O que mostrar |
|---|---|
| **3e** Sincronização | Produtor-consumidor |
| **3d** Semáforos | Buffer cheio / vazio |
| **3d** Mutex | Lock no buffer |
| **3b** Threads | 2 produtores + 1 consumidor |

### Se perguntarem sobre código

- `src/concurrency/producer_consumer.py` — `ProducerConsumerBuffer`

---

## Bloco 6 — Deadlock e prevenção (13–15 min)

### Executar

Primeiro sem prevenção:

```
4 → 1
```

Depois com prevenção:

```
4 → 2
```

### Falar (após opção 1)

> "Duas **transferências cruzadas** ocorrem ao mesmo tempo: Alice envia para Bob enquanto Bob envia para Alice. Cada thread bloqueia sua conta de origem e espera a de destino — gerando **deadlock**. Detectamos pelo **timeout** de 3 segundos."

### Falar (após opção 2)

> "Com **prevenção por ordenação de recursos**, sempre bloqueamos a conta de **menor ID primeiro**. As duas transferências concluem sem travamento e o saldo total é **conservado**."

### Requisitos cobertos

| Item 3 | O que mostrar |
|---|---|
| **3e** Simulação de deadlock | Travamento detectado |
| **3e** Prevenção de deadlock | Ordenação de contas |
| **3a** Bloqueio | Threads aguardando lock |

### Se perguntarem sobre código

- `src/concurrency/deadlock.py`
- `src/banking/account_locks.py`

---

## Bloco 7 — Threads, memória e encerramento (15–17 min)

### Executar

Rede de ATMs:

```
2
```

Painel Gerencial:

```
8
```

### Falar (fluxo B)

> "Na **Rede de Caixas Eletrônicos**, múltiplas **threads reais** operam em paralelo — ATMs, backend e monitor de auditoria — compartilhando buffer e log protegidos por semáforo e mutex."

### Falar (opcional — se a banca perguntar sobre memória)

Execute `5` (Cache de Dados em Memória):

> "Cada operação precisa de quadros de memória. Quando a memória está cheia, a operação é **bloqueada** até a liberação — simulando gerenciamento de memória com page faults."

### Falar (Painel Gerencial)

> "O **Painel Gerencial** consolida todas as métricas: transações concluídas, tempos de espera e resposta, prazos perdidos e uso de memória."

### Encerramento

> "O projeto está modularizado em `core`, `banking`, `concurrency`, `simulation` e `ui`. Os algoritmos de escalonamento, gerência de processos, memória e sincronização são **implementação própria**. Usamos `threading.Lock` e `threading.Semaphore` apenas como primitivas da linguagem — equivalentes a mutex e semáforo —, não como simuladores prontos."

```
0
```

### Requisitos cobertos

| Item 3 | O que mostrar |
|---|---|
| **3b** Threads, concorrência, paralelismo | Fluxo B |
| Memória | Fluxo E (opcional) |
| **3c** Métricas finais | Painel Gerencial |
| Modularização | Estrutura `src/` |

---

## Frases prontas para perguntas da banca

### "O que é um processo no seu sistema?"

> "Cada transação bancária — transferência, saque, depósito — é um processo com PCB contendo PID, prioridade, burst time, estado, quantum e deadline."

### "Quantos escalonadores vocês implementaram?"

> "Três: Round Robin com fila circular e quantum, Prioridade com aging para evitar starvation, e EDF para operações com prazo."

### "Como demonstram mutex e semáforo?"

> "Mutex protege saldo e log na Auditoria de Integridade. Semáforos controlam vagas no buffer da Esteira e limitam ATMs simultâneos na Rede de Caixas."

### "Como demonstram deadlock?"

> "Duas transferências cruzadas bloqueiam contas em ordem oposta. Sem prevenção, ocorre deadlock detectado por timeout. Com ordenação de recursos, as transferências concluem normalmente."

### "Usaram algum simulador pronto?"

> "Não. Implementamos PCB, filas, escalonadores, buffer produtor-consumidor e cenários de deadlock. Usamos apenas primitivas do Python (`threading`) e estruturas de dados da stdlib."

### "Onde estão os testes?"

> "`python -m pytest tests/ -v` — 15 testes cobrindo escalonadores, processos, memória, deadlock e condição de corrida."

---

## Checklist de requisitos do item 3

Use esta lista para confirmar que tudo foi demonstrado:

- [ ] **3a** Criação de processos (Fluxo A)
- [ ] **3a** Finalização (Fluxo A — Concluída)
- [ ] **3a** Alteração de estados (Fluxo A — passo a passo)
- [ ] **3a** Bloqueio e desbloqueio (Fluxo A, D, E)
- [ ] **3a** Prioridades (Fluxo A — coluna Perfil)
- [ ] **3a** PCB: PID, prioridade, burst, estado, quantum, deadline (Fluxo A)
- [ ] **3b** Threads reais (Fluxos B, C, F)
- [ ] **3b** Concorrência e paralelismo (Fluxos B, C)
- [ ] **3b** Compartilhamento de recursos (Fluxos B, C)
- [ ] **3c** 2+ escalonadores (Fluxo A — RR, Prioridade, EDF)
- [ ] **3c** Fila de execução (Fluxo A)
- [ ] **3c** Tempo de espera e resposta (Fluxo A + Painel)
- [ ] **3c** Processos concluídos (Painel Gerencial)
- [ ] **3d** Mutex (Fluxo C)
- [ ] **3d** Semáforos (Fluxos B, F)
- [ ] **3d** Condição de corrida (Fluxo C)
- [ ] **3d** Proteção de recursos (Fluxos C, B, F)
- [ ] **3e** Sincronização produtor-consumidor (Fluxo F)
- [ ] **3e** Deadlock (Fluxo D — opção 1)
- [ ] **3e** Prevenção de deadlock (Fluxo D — opção 2)
- [ ] Interface terminal navegável (todos os fluxos)
- [ ] Modularização (`src/` com camadas separadas)

---

## Referência rápida de inputs durante a apresentação

| Momento | Inputs |
|---|---|
| Prioridade passo a passo | `1` → `2` → `2` |
| EDF automático | `1` → `3` → `1` |
| Saldo sem mutex | `3` → `1` |
| Saldo com mutex | `3` → `2` |
| Esteira | `6` |
| Deadlock | `4` → `1` |
| Prevenção | `4` → `2` |
| Rede ATMs | `2` |
| Memória (opcional) | `5` |
| Painel Gerencial | `8` |
| Encerrar | `0` |
