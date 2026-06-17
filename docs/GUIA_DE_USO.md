# Guia de Uso — Banco Nexus

Manual operacional do simulador bancário de Sistemas Operacionais. Este documento explica como executar o sistema, navegar pelos menus, o que observar em cada tela e quais requisitos do **item 3 do enunciado** cada fluxo demonstra.

---

## 1. Pré-requisitos e execução

### Requisitos

- Python 3.10 ou superior
- Terminal com suporte a cores (opcional; `colorama` melhora a visualização)

### Instalação e execução

```bash
pip install -r requirements.txt
python main.py
```

### Tela inicial

Ao iniciar, o sistema exibe:

1. **Banner** — BANCO NEXUS | Agência Digital 001, com data/hora da sessão
2. **Painel de contas** — três contas ativas (Alice, Bob, Carlos) com número e saldo em R$
3. **Menu principal** — opções organizadas por área (Atendimento, Segurança, Infraestrutura, Administração)

### Legenda de termos

| Termo na interface | Conceito de SO |
|---|---|
| Protocolo (#0001) | PID do processo |
| Transação | Tipo de operação bancária (processo) |
| Perfil (Private / Corrente / Backoffice) | Prioridade (VIP / NORMAL / BATCH) |
| Situação (Na fila, Processando, Suspensa…) | Estado do processo |
| Rest. | Tempo de execução restante (burst) |
| Fila | Tempo de espera |
| Prazo | Deadline |
| Ciclo operacional | Tick da simulação |
| Cache de dados | Memória alocada para a operação |

---

## 2. Mapa geral do menu

```
python main.py
       │
       ▼
  Banner + Contas ativas
       │
       ▼
  Menu Principal
       │
       ├── 1  Central de Processamento de Transações
       ├── 2  Rede de Caixas Eletrônicos (ATMs)
       ├── 3  Auditoria de Integridade
       ├── 4  Gestão de Transferências Simultâneas
       ├── 5  Cache de Dados em Memória
       ├── 6  Esteira de Transações (ATMs → Backend)
       ├── 7  Parâmetros do Sistema
       ├── 8  Painel Gerencial
       └── 0  Encerrar sessão
```

Em qualquer submenu, pressione **Enter** ao final para voltar ao menu principal (exceto quando estiver em modo passo a passo — aí Enter avança um ciclo).

---

## 3. Fluxos detalhados

Cada fluxo abaixo inclui: caminho no menu, passos de execução, o que observar na tela, requisitos do enunciado atendidos e arquivos de código relacionados.

---

### Fluxo A — Central de Processamento de Transações

**Conceito SO:** gerência de processos + escalonamento (RR, Prioridade ou EDF).

#### Caminho no menu

```
1 → [política 1, 2 ou 3] → [modo 1 ou 2]
```

#### Passos de execução

| Passo | Input | Descrição |
|---|---|---|
| 1 | `1` | Abre a Central de Processamento |
| 2 | `1`, `2` ou `3` | Escolhe a política de atendimento (ver tabela abaixo) |
| 3 | `1` ou `2` | Modo tempo real (automático) ou passo a passo |
| 4 | — | Acompanhe os ciclos até o Painel Gerencial final |
| 5 | Enter | Volta ao menu principal |
| 6 | `8` | (Opcional) Reabre o Painel Gerencial da última sessão |

#### Políticas de atendimento

| Input | Nome na interface | Algoritmo SO |
|---|---|---|
| `1` | Fila justa | Round Robin |
| `2` | Clientes Private / prioritários | Escalonamento por Prioridade |
| `3` | Operações urgentes | EDF (Earliest Deadline First) |

#### O que observar na tela

- **Fila de atendimento:** `#0001 → #0002 → #0003` (ordem de execução)
- **Tabela de operações:** Protocolo, Transação, Perfil, Situação, Rest., Fila, Prazo, Resp.
- **Operações suspensas:** protocolos bloqueados aguardando conta ou memória
- **Motivo do bloqueio:** "Conta em uso" ou "Aguardando memória de cache"
- **Mapa de cache:** quadros de memória ocupados por operação
- **Painel Gerencial (final):** transações concluídas, tempos médios, prazos não cumpridos

#### Requisitos do item 3 atendidos

| Requisito | Onde ver | Código |
|---|---|---|
| **3a** Criação de processos | Operações geradas ao iniciar (Transferência, Saque, Depósito…) | `src/banking/operations.py`, `src/core/process_manager.py` |

| **3a** Finalização | Situação "Concluída"; contagem no Painel Gerencial | `src/core/scheduler.py` |

| **3a** Alteração de estados | Entrada → Na fila → Processando → Suspensa → Concluída | `src/core/process.py` (`ProcessState`) |

| **3a** Bloqueio e desbloqueio | "Operações suspensas" + motivo exibido | `src/simulation/engine.py` |

| **3a** Controle de prioridades | Coluna Perfil: Private, Corrente, Backoffice | `src/core/process.py` (`Priority`) |

| **3a** PCB: PID | Coluna Protocolo | `src/core/process.py` (`PCB`) |
| **3a** PCB: prioridade | Coluna Perfil | `src/core/process.py` |
| **3a** PCB: tempo de execução | Coluna Rest. (burst restante) | `src/core/process.py` |
| **3a** PCB: estado | Coluna Situação | `src/core/process.py` |
| **3a** PCB: quantum | Política RR; configurável na opção 7 | `src/core/scheduler.py` (`RoundRobinScheduler`) |
| **3a** PCB: deadline | Coluna Prazo; flags ATRASO / PERDIDO | `src/core/process.py`, `src/core/scheduler.py` (`EDFScheduler`) |

| **3c** Dois ou mais escalonadores | Executar três vezes: `1→1`, `1→2`, `1→3` | `src/core/scheduler.py` |
| **3c** Fila de execução | Linha "Fila de atendimento" | `src/ui/display.py` |
| **3c** Tempo de espera | Coluna Fila + Painel Gerencial | `src/core/metrics.py` |
| **3c** Tempo de resposta | Coluna Resp. + Painel Gerencial | `src/core/metrics.py` |
| **3c** Processos concluídos | "Transações concluídas" no Painel Gerencial | `src/core/metrics.py` |
| Memória | Mapa de cache durante a simulação | `src/core/memory.py` |

#### Dica para apresentação

Use **Prioridade + passo a passo** (`1 → 2 → 2`) para mostrar clientes Private sendo atendidos antes dos demais.

---

### Fluxo B — Rede de Caixas Eletrônicos (ATMs)

**Conceito SO:** threads reais, concorrência, compartilhamento de recursos.

#### Caminho no menu

```
2
```

#### Passos de execução

| Passo | Input | Descrição |
|---|---|---|
| 1 | `2` | Inicia a simulação da rede de ATMs |
| 2 | — | Aguarde a conclusão automática |
| 3 | Enter | Volta ao menu principal |

#### O que observar na tela

- **Movimentação da rede:** transações enviadas pelos ATMs, processadas, tamanho do buffer
- **Monitor de auditoria:** logs em background com contagem de fila, bloqueados e memória

#### Requisitos do item 3 atendidos

| Requisito | Evidência | Código |
|---|---|---|
| **3b** Múltiplas threads reais | 2+ threads ATM + 1 backend + 1 monitor | `src/simulation/engine.py` (`run_concurrent_atm_demo`) |
| **3b** Concorrência | ATMs operam ao mesmo tempo | `threading.Thread` |
| **3b** Paralelismo | Execução simultânea de múltiplos caixas | `threading.Thread` |
| **3b** Compartilhamento de recursos | Buffer e log compartilhados entre threads | `src/concurrency/producer_consumer.py` |
| **3d** Semáforo | Limite de ATMs simultâneos (`BankSemaphore`) | `src/concurrency/sync_primitives.py` |
| **3d** Mutex | Log protegido com `append_safe` | `src/concurrency/sync_primitives.py` |

---

### Fluxo C — Auditoria de Integridade

**Conceito SO:** exclusão mútua, condição de corrida, proteção de recursos compartilhados.

#### Caminho no menu

```
3 → [1, 2, 3 ou 4]
```

#### Passos de execução

| Passo | Input | Cenário |
|---|---|---|
| 1 | `3` | Abre Auditoria de Integridade |
| 2a | `1` | Saldo — **sem** trava de segurança (mutex desligado) |
| 2b | `2` | Saldo — **com** trava de segurança (mutex ligado) |
| 2c | `3` | Livro-razão — gravação **sem** proteção |
| 2d | `4` | Livro-razão — gravação **protegida** |
| 3 | Enter | Volta ao menu principal |

#### O que observar na tela

**Saldo (opções 1 e 2):**

- 4 threads creditam R$ 1,00 cada, 100 vezes → saldo esperado: **R$ 400,00**
- Sem mutex: saldo apurado **incorreto** (condição de corrida)
- Com mutex: saldo apurado **correto**

**Livro-razão (opções 3 e 4):**

- 4 threads gravam 50 linhas cada → esperado: **200 linhas**
- Sem proteção: linhas **perdidas ou corrompidas**
- Com proteção: **200 linhas** íntegras

#### Requisitos do item 3 atendidos

| Requisito | Evidência | Código |
|---|---|---|
| **3d** Mutex | `BankMutex` protege saldo e log | `src/concurrency/sync_primitives.py` |
| **3d** Condição de corrida | Comparar opção 1 vs 2 e 3 vs 4 | `run_race_condition_demo`, `run_log_race_demo` |
| **3d** Proteção de recurso compartilhado | Saldo compartilhado + arquivo de log | `SharedBalance`, `TransactionLog` |
| **3b** Threads reais | 4 threads em cada teste | `threading.Thread` |

#### Dica para apresentação

Execute primeiro `3 → 1` (falha) e depois `3 → 2` (sucesso). O contraste é imediato e fácil de explicar.

---

### Fluxo D — Gestão de Transferências Simultâneas (Deadlock)

**Conceito SO:** sincronização, deadlock e prevenção.

#### Caminho no menu

```
4 → [1 ou 2]
```

#### Passos de execução

| Passo | Input | Descrição |
|---|---|---|
| 1 | `4` | Exibe contas Alice e Bob com saldos |
| 2a | `1` | Transferências cruzadas **sem** protocolo anti-travamento |
| 2b | `2` | Transferências cruzadas **com** ordenação de contas |
| 3 | Enter | Volta ao menu principal |

#### Cenário

Duas transferências ocorrem ao mesmo tempo:

- Thread 1: Alice → Bob (R$ 100,00)
- Thread 2: Bob → Alice (R$ 150,00)

#### O que observar na tela

| Modo | Resultado esperado |
|---|---|
| Sem prevenção (`1`) | Travamento detectado; transferências incompletas |
| Com prevenção (`2`) | 2 transferências concluídas; saldo total conservado |

O **Histórico da operação** mostra a sequência de locks nas contas.

#### Requisitos do item 3 atendidos

| Requisito | Evidência | Código |
|---|---|---|
| **3e** Simulação de deadlock | Locks em ordem oposta + timeout de 3s | `src/concurrency/deadlock.py` (`_transfer_unsafe`) |
| **3e** Prevenção de deadlock | Ordenação de recursos (menor ID de conta primeiro) | `src/concurrency/deadlock.py` (`_transfer_safe`) |
| **3a** Bloqueio | Threads aguardando lock de conta | `src/banking/account_locks.py` |

---

### Fluxo E — Cache de Dados em Memória

**Conceito SO:** gerenciamento de memória e bloqueio por falta de recurso.

#### Caminho no menu

```
5
```

#### Passos de execução

| Passo | Input | Descrição |
|---|---|---|
| 1 | `5` | Inicia demo de pressão de memória |
| 2 | — | Leia o resumo e o mapa de quadros |
| 3 | Enter | Volta ao menu principal |

#### O que observar na tela

- **5 operações** disputam **6 quadros** (cada uma precisa de 2 páginas)
- **3 alocadas** com sucesso na primeira tentativa
- **2 bloqueadas** por falta de memória (page fault)
- Após liberar memória de uma operação, **1 é desbloqueada**
- Mapa de quadros mostra qual operação ocupa cada frame

#### Requisitos do item 3 atendidos

| Requisito | Evidência | Código |
|---|---|---|
| Gerenciamento de memória | Alocação, liberação, page faults | `src/core/memory.py` |
| **3a** Bloqueio por recurso | Operação suspensa aguardando memória | `src/simulation/engine.py` |

---

### Fluxo F — Esteira de Transações (Produtor-Consumidor)

**Conceito SO:** sincronização produtor-consumidor com semáforos e mutex.

#### Caminho no menu

```
6
```

#### Passos de execução

| Passo | Input | Descrição |
|---|---|---|
| 1 | `6` | Inicia esteira ATMs → Backend |
| 2 | — | Acompanhe o log de movimentação |
| 3 | Enter | Volta ao menu principal |

#### O que observar na tela

- **2 ATMs** (produtores) enviam transações
- **1 processador backend** (consumidor) processa a fila
- Buffer com **capacidade 3** — quando cheio, ATM aguarda ("Buffer cheio - bloqueado")
- Quando vazio, backend aguarda ("Buffer vazio - bloqueado")
- Ao final: 10 produzidas, 10 consumidas

#### Requisitos do item 3 atendidos

| Requisito | Evidência | Código |
|---|---|---|
| **3e** Cenário de sincronização | Padrão produtor-consumidor | `src/concurrency/producer_consumer.py` |
| **3d** Semáforos | `empty_slots` e `filled_slots` | `ProducerConsumerBuffer` |
| **3d** Mutex | `buffer_lock` na região crítica | `ProducerConsumerBuffer` |
| **3b** Threads reais | 2 produtores + 1 consumidor | `run_producer_consumer_demo` |

---

### Fluxo G — Parâmetros do Sistema e Painel Gerencial

**Conceito SO:** configuração do escalonador e visualização de métricas.

#### Caminhos no menu

```
7          → Parâmetros do Sistema
8          → Painel Gerencial (última sessão da opção 1)
```

#### Parâmetros configuráveis (opção 7)

| Parâmetro | Conceito SO | Padrão |
|---|---|---|
| Tempo por operação (quantum) | Quantum do Round Robin | 2 |
| Operações na fila padrão | Número de processos | 8 |
| Quadros de cache de memória | Frames de memória | 16 |
| Intervalo entre ciclos | Delay por tick | 0,1s |
| Modo expediente | Simulação sem delay | desligado |
| Caixas eletrônicos na rede | Threads ATM (fluxo B) | 2 |

#### Painel Gerencial (opção 8)

Exibe métricas da **última execução da Central de Processamento** (opção 1):

- Tempo de operação (ciclos)
- Transações concluídas
- Espera média na fila
- Tempo médio de resposta
- Tempo médio total (turnaround)
- Prazos não cumpridos
- Uso de cache de memória

> Se nenhuma sessão foi executada, o sistema orienta a usar a opção 1 primeiro.

#### Requisitos do item 3 atendidos

| Requisito | Evidência | Código |
|---|---|---|
| **3c** Quantum configurável | Opção 7 | `src/simulation/engine.py` (`SimulationConfig`) |
| Interface terminal navegável | Menus hierárquicos com retorno por Enter | `src/ui/menu.py` |

---

## 4. Matriz consolidada: Fluxo × Requisito

| Subitem do enunciado (item 3) | Detalhe | Fluxo(s) |
|---|---|---|
| **3a** | Criação de processos | A |
| **3a** | Finalização de processos | A |
| **3a** | Alteração de estados | A |
| **3a** | Bloqueio e desbloqueio | A, D, E |
| **3a** | Controle de prioridades | A |
| **3a** | PCB: PID | A |
| **3a** | PCB: prioridade | A |
| **3a** | PCB: tempo de execução | A |
| **3a** | PCB: estado | A |
| **3a** | PCB: quantum | A, G |
| **3a** | PCB: deadline | A (EDF) |
| **3b** | Múltiplas threads reais | B, C, F |
| **3b** | Concorrência | B, C |
| **3b** | Paralelismo | B |
| **3b** | Compartilhamento de recursos | B, C |
| **3c** | Dois ou mais escalonadores | A (RR, Prioridade, EDF) |
| **3c** | Fila de execução | A |
| **3c** | Tempo de espera | A, G |
| **3c** | Tempo de resposta | A, G |
| **3c** | Processos concluídos | A, G |
| **3d** | Mutex | C, B |
| **3d** | Semáforos | B, F |
| **3d** | Condição de corrida | C |
| **3d** | Proteção de recursos compartilhados | C, B, F |
| **3e** | Cenário de sincronização | F |
| **3e** | Simulação de deadlock | D |
| **3e** | Prevenção de deadlock | D |
| **Restrições** | Interface terminal com menus | Todos |
| **Restrições** | Modularização em arquivos/classes | Estrutura `src/` |

---

## 5. Dicas de uso

### Para estudo e testes

```bash
python -m pytest tests/ -v
```

15 testes validam escalonadores, gerência de processos, memória, deadlock e condição de corrida.

### Para apresentação ao vivo

1. Ative o **modo expediente** antes da demo: `7` → modo expediente → `s`
2. Use **passo a passo** na Central de Processamento: `1 → 2 → 2`
3. Siga a ordem recomendada: **A → C → F → D → B → E → 8**

### Ordem mínima para cobrir todos os requisitos do item 3

| Ordem | Fluxo | Tempo estimado |
|---|---|---|
| 1 | A (Prioridade, passo a passo) | 3–5 min |
| 2 | A (EDF, mencionar deadline) | 2 min |
| 3 | C (saldo sem/com mutex) | 2 min |
| 4 | F (esteira) | 2 min |
| 5 | D (deadlock + prevenção) | 2 min |
| 6 | B ou E (threads ou memória) | 2 min |
| 7 | G (Painel Gerencial) | 1 min |

### Estrutura de código (para perguntas da banca)

```
src/
├── core/           process.py, process_manager.py, scheduler.py, metrics.py, memory.py
├── banking/        accounts.py, operations.py, account_locks.py
├── concurrency/    sync_primitives.py, producer_consumer.py, deadlock.py
├── simulation/     engine.py
└── ui/             menu.py, display.py, banking_labels.py
```

---

## 6. Referência rápida de inputs

| Objetivo | Sequência de inputs |
|---|---|
| Round Robin automático | `1` → `1` → `1` |
| Prioridade passo a passo | `1` → `2` → `2` |
| EDF automático | `1` → `3` → `1` |
| Race condition saldo (falha) | `3` → `1` |
| Race condition saldo (sucesso) | `3` → `2` |
| Deadlock sem prevenção | `4` → `1` |
| Deadlock com prevenção | `4` → `2` |
| Memória | `5` |
| Produtor-consumidor | `6` |
| Ver métricas | `8` |

---

## 7. Conformidade com o Item 4 (Restrições do Enunciado)

Esta seção documenta como o projeto atende às **restrições do item 4** do enunciado e o que explicar na apresentação.

### 7a. Implementação própria

#### O que o enunciado proíbe

| Proibição | Situação no projeto |
|---|---|
| Simuladores prontos de SO | **Não utilizado.** Não há bibliotecas como `simpy`, simuladores de SO de terceiros, etc. |
| Projetos copiados | Código original da equipe, com arquitetura própria |
| Bibliotecas que implementam os algoritmos automaticamente | **Não utilizado.** Round Robin, Prioridade e EDF estão em `src/core/scheduler.py` |

#### Dependências externas (`requirements.txt`)

| Biblioteca | Uso em runtime | Justificativa |
|---|---|---|
| `colorama` | Cores no terminal | Apenas visualização |
| `pytest` | Testes (`python -m pytest`) | Validação; não faz parte da simulação ao executar `main.py` |

Todo o restante é **biblioteca padrão do Python**: `threading`, `collections`, `dataclasses`, `enum`, `abc`, `random`, `time`.

#### O que é implementação da equipe

| Conceito | Arquivo principal |
|---|---|
| PCB e estados do processo | `src/core/process.py` |
| Criação, bloqueio, finalização | `src/core/process_manager.py` |
| Round Robin, Prioridade, EDF | `src/core/scheduler.py` |
| Métricas (espera, resposta, turnaround) | `src/core/metrics.py` |
| Gerenciamento de memória (quadros) | `src/core/memory.py` |
| Buffer produtor-consumidor | `src/concurrency/producer_consumer.py` |
| Deadlock e prevenção | `src/concurrency/deadlock.py` |
| Orquestração da simulação | `src/simulation/engine.py` |

#### Uso de `threading.Lock` e `threading.Semaphore`

O projeto encapsula as primitivas em `BankMutex` e `BankSemaphore` (`src/concurrency/sync_primitives.py`).

**Isso é permitido** porque:

- `threading.Lock` é o **mutex da linguagem** (primitiva do sistema), não um simulador de SO pronto
- `threading.Semaphore` é o **semáforo da linguagem**, na mesma categoria
- O que é da equipe: **quando** usar proteção, **quais recursos** proteger (saldo, log, buffer), e os **cenários** (condição de corrida, produtor-consumidor, deadlock)

**Frase sugerida para a banca:**

> "Usamos `threading` apenas como primitiva de concorrência. Os algoritmos de escalonamento, PCB, filas, buffer produtor-consumidor, gerência de memória e cenários de deadlock são implementação própria."

#### Tabela para explicar na apresentação

| Biblioteca / módulo | Papel | Por que é permitido |
|---|---|---|
| `threading` | Lock, Semaphore, Thread | Primitivas de concorrência do Python |
| `collections.deque` | Fila circular no Round Robin | Estrutura de dados; o algoritmo RR é nosso |
| `dataclasses`, `enum`, `abc` | Modelagem e organização | Utilitários da linguagem |
| `colorama` | Cores no terminal | Somente interface visual |
| `pytest` | Testes unitários | Validação; não substitui a lógica do SO |

**Não utilizamos:** simpy, frameworks de escalonamento prontos, simuladores de SO de terceiros.

---

### 7b. Modularização

| Requisito | Como o projeto atende |
|---|---|
| Separação em arquivos | Módulos em `src/core/`, `src/banking/`, `src/concurrency/`, `src/simulation/`, `src/ui/` |
| Classes e módulos | `PCB`, `ProcessManager`, `Scheduler`, `SimulationEngine`, `DeadlockDemo`, etc. |
| Organização por responsabilidade | Núcleo de SO separado do domínio bancário e da interface |
| Boas práticas | Classe abstrata `Scheduler`, testes em `tests/`, documentação em `docs/` |

```
src/
├── core/           # PCB, escalonamento, memória, métricas
├── banking/        # Contas, operações, locks de conta
├── concurrency/    # Mutex, semáforos, sincronização, deadlock
├── simulation/     # Engine e configuração
└── ui/             # Menus e exibição (sem regras de escalonamento)
```

A interface (`src/ui/`) não implementa algoritmos de SO — apenas chama a engine e exibe resultados.

---

### 7c. Interface

| Requisito | Como o projeto atende |
|---|---|
| Interface via terminal | `python main.py` — menus no console |
| Menus ou comandos navegáveis | Menu principal (opções 0–8) e submenus com `input()` |
| Exibição de estados | Coluna Situação (Na fila, Processando, Suspensa…), fila de atendimento, motivo de bloqueio |
| Exibição de resultados | Painel Gerencial, logs de auditoria, mapa de memória, resumos de transferência |

O enunciado aceita terminal, desktop ou web; este projeto utiliza **interface terminal**.

---

### Checklist — Item 4

| Subitem | Atende? |
|---|---|
| 4a — Sem simuladores prontos | Sim |
| 4a — Sem bibliotecas de escalonamento prontas | Sim |
| 4a — Bibliotecas explicáveis na apresentação | Sim (ver tabela acima) |
| 4b — Separação em arquivos | Sim |
| 4b — Classes/módulos por responsabilidade | Sim |
| 4b — Boas práticas de programação | Sim |
| 4c — Interface com menus navegáveis | Sim |
| 4c — Exibição de estados e resultados | Sim |

---

Para o roteiro cronometrado de apresentação oral, consulte [ROTEIRO_APRESENTACAO.md](ROTEIRO_APRESENTACAO.md).

Para perguntas técnicas da banca, consulte [perguntasTecnicas.md](perguntasTecnicas.md).

Para entender a estrutura e o papel de cada arquivo, consulte [explicacaoCodigo.md](explicacaoCodigo.md).
