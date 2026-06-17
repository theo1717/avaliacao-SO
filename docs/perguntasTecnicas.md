# Perguntas Técnicas — Banco Nexus

Respostas preparadas para a banca, alinhadas ao código do projeto. Consulte também o [Guia de Uso](GUIA_DE_USO.md) e o [Roteiro de Apresentação](ROTEIRO_APRESENTACAO.md).

---

## 1. Qual algoritmo de escalonamento foi utilizado e por quê?

Foram implementados **três algoritmos** em `src/core/scheduler.py`:

| Algoritmo | Uso no banco | Motivação |
|---|---|---|
| **Round Robin** | Fila justa de atendimento | Todas as operações recebem tempo de CPU igual (quantum configurável). Evita que uma operação monopolize o processador. |
| **Prioridade** | Clientes Private/VIP primeiro | Saques e pagamentos urgentes têm prioridade sobre extratos e antifraude. Inclui **aging** para evitar starvation de operações Backoffice. |
| **EDF** (Earliest Deadline First) | Operações com prazo | Transações com **deadline** mais próximo são atendidas primeiro — adequado a tempo real. |

**Por que três?** O enunciado exige pelo menos dois; o projeto oferece um para **equidade** (RR), um para **importância** (Prioridade) e um para **urgência temporal** (EDF), todos com analogia bancária.

**Onde demonstrar:** Menu `1` → opções `1`, `2` ou `3`.

**Código:** `src/core/scheduler.py` — `RoundRobinScheduler`, `PriorityScheduler`, `EDFScheduler`.

---

## 2. Como ocorre a sincronização entre threads?

A sincronização usa **mutex** e **semáforos**, encapsulados em `BankMutex` e `BankSemaphore` (`src/concurrency/sync_primitives.py`), sobre as primitivas `threading.Lock` e `threading.Semaphore`.

### Mecanismos principais

1. **Produtor-consumidor** (`src/concurrency/producer_consumer.py`):
   - Semáforo `empty_slots` — controla vagas no buffer
   - Semáforo `filled_slots` — controla itens disponíveis para consumo
   - Mutex `buffer_lock` — protege a lista interna do buffer

2. **Transferências** (`src/concurrency/deadlock.py`): locks por conta bancária

3. **Saldo e log** (`src/concurrency/sync_primitives.py`): mutex em `SharedBalance` e `TransactionLog`

4. **Memória** (`src/core/memory.py`): mutex na alocação/liberação de quadros

5. **Rede de ATMs** (`src/simulation/engine.py`): semáforo limita ATMs simultâneos; mutex no log

### Fluxo típico (esteira de transações)

1. ATM só produz se houver vaga (`empty_slots.acquire`)
2. ATM entra na região crítica do buffer (`buffer_lock`)
3. ATM libera sinal de item disponível (`filled_slots.release`)
4. Backend faz o processo inverso

**Onde demonstrar:** Menu `6` (Esteira) e Menu `2` (Rede de ATMs).

---

## 3. Onde existem regiões críticas?

Região crítica = trecho em que threads acessam **recurso compartilhado** e apenas uma deve manipulá-lo por vez.

| Região crítica | Recurso | Proteção | Arquivo |
|---|---|---|---|
| Atualização de saldo | `SharedBalance.balance` | `BankMutex` | `sync_primitives.py` |
| Escrita no log | Arquivo de transações | `BankMutex` | `sync_primitives.py` |
| Buffer de transações | Lista interna do buffer | `buffer_lock` (mutex) | `producer_consumer.py` |
| Mapa de quadros de memória | `frames[]` | `BankMutex` | `memory.py` |
| Saldo das contas | `Account.balance` | `threading.Lock` por conta | `accounts.py`, `deadlock.py` |
| Logs internos | `_log`, `_status_log` | `threading.Lock` | vários módulos |

Na **Central de Processamento**, a fila de processos é manipulada pelo escalonador em loop sequencial (ticks), sem threads concorrentes na fila. A concorrência real aparece nas demos com `threading.Thread`.

**Onde demonstrar:** Menu `3` (Auditoria de Integridade) e Menu `6` (Esteira).

---

## 4. Como o deadlock foi tratado?

Duas abordagens em `src/concurrency/deadlock.py`:

### Demonstração (sem prevenção)

- Thread A: lock na conta 1 → tenta lock na conta 2
- Thread B: lock na conta 2 → tenta lock na conta 1
- Ocorre **deadlock**, detectado por **timeout de 3 segundos** em `acquire(timeout=3)`
- Flag `deadlock_detected = True`

### Prevenção (com ordenação de recursos)

- Sempre bloqueia a conta de **menor ID primeiro** (`sorted([from_id, to_id])`)
- Quebra o ciclo de espera circular
- As duas transferências concluem normalmente

**Analogia bancária:** duas transferências cruzadas Alice ↔ Bob; a prevenção é o protocolo “sempre trancar a conta de menor número antes da maior”.

**Onde demonstrar:** Menu `4` → opção `1` (deadlock) e opção `2` (prevenção).

**Código:** `_transfer_unsafe()` e `_transfer_safe()` em `src/concurrency/deadlock.py`.

---

## 5. Como ocorre a substituição de páginas?

**Resposta direta:** o projeto **não implementa substituição de páginas** (nem FIFO, nem LRU de memória virtual).

O que existe em `BankMemoryManager` (`src/core/memory.py`):

1. **Alocação** de quadros livres para cada operação
2. Se **não há quadros suficientes** → incrementa `page_faults` e a operação é **bloqueada**
3. Quando uma operação **termina** → `free(pid)` libera os quadros
4. Operações bloqueadas podem ser **desbloqueadas** quando há memória (`_try_unblock_waiters` em `engine.py`)

Há **alocação, bloqueio e liberação**, mas **não** há algoritmo que despeje a página de outro processo para abrir espaço.

**Sugestão de resposta oral:**

> "Implementamos gerenciamento de memória com alocação de quadros e bloqueio por falta de memória. Substituição de páginas (FIFO/LRU) não foi escopo do simulador; em vez de despejar uma página, a operação aguarda na fila de bloqueados até a liberação."

**Onde demonstrar:** Menu `5` (Cache de Dados em Memória).

---

## 6. Qual a diferença entre FIFO e LRU?

### Conceito teórico (memória virtual)

| | FIFO | LRU |
|---|---|---|
| Critério | Despeja a página há **mais tempo na memória** | Despeja a página **menos usada recentemente** |
| Ideia | Fila: quem entrou primeiro sai primeiro | Mantém histórico de acesso |
| Problema clássico | Pode despejar página ainda muito usada | Mais custoso, porém geralmente melhor |

### No nosso projeto

**Nenhum dos dois** está implementado para substituição de páginas (ver pergunta 5).

**Relações indiretas no projeto:**

- **Round Robin** na fila de processos tem espírito de fila circular, mas é escalonamento de CPU, não substituição de página
- O buffer produtor-consumidor usa `pop(0)` (FIFO de transações), mas isso é fila de dados, não algoritmo de memória

---

## 7. Como o sistema evita condição de corrida?

**Condição de corrida** = resultado incorreto quando threads acessam o mesmo dado sem coordenação (ex.: duas threads leem o mesmo saldo, somam e gravam — uma atualização se perde).

### Demonstração no projeto

- `deposit_unsafe()` — saldo final **incorreto**
- `deposit_safe()` — saldo final **correto** (R$ 400,00 com 4 threads × 100 iterações × R$ 1,00)

### Solução: mutex

```python
with self.mutex:
    temp = self.balance
    temp += amount
    self.balance = temp
```

Garante **exclusão mútua**: só uma thread altera o saldo por vez.

O mesmo princípio vale para:

- Log de transações (`append_safe`)
- Buffer (`with self._buffer_lock`)
- Memória (`with self._mutex` em `allocate`/`free`)

**Semáforos** complementam evitando condições inválidas de buffer (cheio/vazio) — é **sincronização**, não apenas exclusão mútua.

**Onde demonstrar:** Menu `3` → opções `1` e `2` (saldo); `3` e `4` (log).

**Código:** `src/concurrency/sync_primitives.py` — `SharedBalance`, `TransactionLog`.

---

## 8. Qual a complexidade do algoritmo implementado?

Por **ciclo (tick)** da simulação, com **n** processos na fila ready:

| Algoritmo | Operação principal | Complexidade por tick |
|---|---|---|
| **Round Robin** | `popleft` na `deque` | **O(1)** amortizado; no pior caso percorre a fila |
| **Prioridade** | `sort` na lista ready | **O(n log n)** |
| **EDF** | `sort` / `min` por deadline | **O(n log n)** na seleção; preempção **O(n)** |
| **Tick geral** | Atualizar espera, decrementar burst | **O(n)** |
| **Alocação de memória** | Buscar quadros livres | **O(frames)** — valor fixo (ex.: 16) |

**Simulação completa:** com **T** ticks, algo como **O(T × n log n)** com Prioridade/EDF, ou **O(T × n)** com RR em condições normais.

Para o tamanho do projeto (8 processos, até 500 ticks), a complexidade é adequada.

**Código:** `src/core/scheduler.py`, `src/core/memory.py`.

---

## 9. Como ocorre o gerenciamento da memória?

Implementado em `BankMemoryManager` (`src/core/memory.py`) e integrado na `SimulationEngine` (`src/simulation/engine.py`):

1. Cada operação precisa de `pages_required` páginas (derivado do burst em `operations.py`)
2. Na admissão → `_try_allocate_memory(pid)` tenta alocar quadros livres
3. **Sucesso** → quadros marcados com o PID (`cache-conta-pX`)
4. **Falha** → `page_faults++`, operação vai para **BLOCKED** com `block_reason = "memoria"`
5. Ao terminar → `memory.free(pid)` libera todos os quadros da operação
6. **Desbloqueio** → `_try_unblock_waiters()` tenta realocar para processos suspensos

### Demo isolada (Menu 5)

- 5 operações, 6 quadros, 2 páginas cada
- 3 alocam, 2 bloqueiam, 1 desbloqueia após `free`

Não há paginação em disco nem swap — é **alocação de quadros em RAM simulada**.

**Onde demonstrar:** Menu `5` e durante a Central de Processamento (mapa de cache na tela).

---

## 10. Como funciona o compartilhamento de recursos?

| Recurso | Quem compartilha | Como protege |
|---|---|---|
| **Saldo da conta** | Threads na auditoria | Mutex |
| **Contas bancárias** | Threads de transferência | Lock por conta + ordenação anti-deadlock |
| **Buffer de transações** | ATMs (produtores) e backend (consumidor) | Semáforos + mutex |
| **Log de transações** | ATMs e backend | Mutex |
| **Quadros de memória** | Várias operações (processos) | Mutex; bloqueio se insuficiente |
| **Conta em uso** | Operações na Central de Processamento | `AccountLockManager` |

### Padrão geral

- Recurso **exclusivo** (saldo, buffer, memória) → **mutex**
- Recurso com **limite de vagas** (buffer, slots de ATM) → **semáforo**
- Recurso com **risco de deadlock** (duas contas) → **ordenação de locks**

**Onde demonstrar:** Fluxos B, C, D, E e F do [Guia de Uso](GUIA_DE_USO.md).

---

## Referência rápida: pergunta → menu → código

| Pergunta | Menu | Arquivo principal |
|---|---|---|
| Escalonamento | `1` | `src/core/scheduler.py` |
| Sincronização / threads | `2`, `6` | `producer_consumer.py`, `engine.py` |
| Regiões críticas / race condition | `3` | `sync_primitives.py` |
| Deadlock | `4` | `deadlock.py` |
| Memória | `5`, `1` | `memory.py`, `engine.py` |
| Compartilhamento de recursos | `2`, `3`, `4`, `6` | vários |

---

## Dica para a banca

Se perguntarem algo **não implementado** (ex.: substituição FIFO/LRU de páginas), responda com clareza o que **foi** feito e o que seria evolução futura. Isso demonstra domínio e honestidade técnica.
