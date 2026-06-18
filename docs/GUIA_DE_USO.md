# Guia de Uso — Banco Nexus

Manual operacional do simulador bancário. Este documento explica como executar o sistema, navegar pelos menus e o que observar em cada tela.

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

### Termos da interface

| Termo | Significado |
|---|---|
| Protocolo (#0001) | Identificador da operação |
| Transação | Tipo de operação (transferência, saque, depósito, etc.) |
| Perfil | Tipo de cliente (Private, Corrente, Backoffice) |
| Situação | Estado atual da operação (Na fila, Processando, Suspensa…) |
| Rest. | Tempo restante para concluir a operação |
| Fila | Tempo de espera na fila |
| Prazo | Limite de tempo para conclusão |
| Ciclo operacional | Passo da simulação |
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

---

### Fluxo A — Central de Processamento de Transações

Processa operações bancárias com diferentes políticas de atendimento.

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

| Input | Nome na interface | Comportamento |
|---|---|---|
| `1` | Fila justa | Atendimento em rodízio, com tempo fixo por operação |
| `2` | Clientes Private / prioritários | Clientes Private são atendidos antes dos demais |
| `3` | Operações urgentes | Operações com prazo mais próximo são atendidas primeiro |

#### O que observar na tela

- **Fila de atendimento:** `#0001 → #0002 → #0003` (ordem de execução)
- **Tabela de operações:** Protocolo, Transação, Perfil, Situação, Rest., Fila, Prazo, Resp.
- **Operações suspensas:** protocolos bloqueados aguardando conta ou memória
- **Motivo do bloqueio:** "Conta em uso" ou "Aguardando memória de cache"
- **Mapa de cache:** quadros de memória ocupados por operação
- **Painel Gerencial (final):** transações concluídas, tempos médios, prazos não cumpridos

#### Dica

Use **Prioridade + passo a passo** (`1 → 2 → 2`) para acompanhar clientes Private sendo atendidos antes dos demais, ciclo a ciclo.

---

### Fluxo B — Rede de Caixas Eletrônicos (ATMs)

Simula vários caixas eletrônicos operando ao mesmo tempo e enviando transações para o backend.

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

---

### Fluxo C — Auditoria de Integridade

Demonstra o impacto de proteger (ou não) recursos compartilhados quando várias operações ocorrem ao mesmo tempo.

#### Caminho no menu

```
3 → [1, 2, 3 ou 4]
```

#### Passos de execução

| Passo | Input | Cenário |
|---|---|---|
| 1 | `3` | Abre Auditoria de Integridade |
| 2a | `1` | Saldo — **sem** trava de segurança |
| 2b | `2` | Saldo — **com** trava de segurança |
| 2c | `3` | Livro-razão — gravação **sem** proteção |
| 2d | `4` | Livro-razão — gravação **protegida** |
| 3 | Enter | Volta ao menu principal |

#### O que observar na tela

**Saldo (opções 1 e 2):**

- 4 threads creditam R$ 1,00 cada, 100 vezes → saldo esperado: **R$ 400,00**
- Sem trava: saldo apurado **incorreto**
- Com trava: saldo apurado **correto**

**Livro-razão (opções 3 e 4):**

- 4 threads gravam 50 linhas cada → esperado: **200 linhas**
- Sem proteção: linhas **perdidas ou corrompidas**
- Com proteção: **200 linhas** íntegras

#### Dica

Execute primeiro `3 → 1` e depois `3 → 2` para comparar o resultado com e sem trava de segurança.

---

### Fluxo D — Gestão de Transferências Simultâneas

Simula transferências cruzadas entre contas, com e sem protocolo anti-travamento.

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

O **Histórico da operação** mostra a sequência de bloqueios nas contas.

---

### Fluxo E — Cache de Dados em Memória

Demonstra alocação de memória e bloqueio de operações quando não há quadros disponíveis.

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
- **2 bloqueadas** por falta de memória
- Após liberar memória de uma operação, **1 é desbloqueada**
- Mapa de quadros mostra qual operação ocupa cada frame

---

### Fluxo F — Esteira de Transações (Produtor-Consumidor)

Simula ATMs enviando transações para um processador backend via buffer compartilhado.

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

- **2 ATMs** enviam transações
- **1 processador backend** processa a fila
- Buffer com **capacidade 3** — quando cheio, ATM aguarda ("Buffer cheio - bloqueado")
- Quando vazio, backend aguarda ("Buffer vazio - bloqueado")
- Ao final: 10 produzidas, 10 consumidas

---

### Fluxo G — Parâmetros do Sistema e Painel Gerencial

Configura o comportamento da simulação e consulta métricas da última sessão.

#### Caminhos no menu

```
7          → Parâmetros do Sistema
8          → Painel Gerencial (última sessão da opção 1)
```

#### Parâmetros configuráveis (opção 7)

| Parâmetro | Padrão |
|---|---|
| Tempo por operação (quantum) | 2 |
| Operações na fila padrão | 8 |
| Quadros de cache de memória | 16 |
| Intervalo entre ciclos | 0,1s |
| Modo expediente | desligado |
| Caixas eletrônicos na rede | 2 |

#### Painel Gerencial (opção 8)

Exibe métricas da **última execução da Central de Processamento** (opção 1):

- Tempo de operação (ciclos)
- Transações concluídas
- Espera média na fila
- Tempo médio de resposta
- Tempo médio total
- Prazos não cumpridos
- Uso de cache de memória

> Se nenhuma sessão foi executada, o sistema orienta a usar a opção 1 primeiro.

---

## 4. Dicas de uso

### Rodar os testes

```bash
python -m pytest tests/ -v
```

### Modo expediente

Ative antes de demos longas para acelerar a simulação: `7` → modo expediente → `s`.

### Ordem sugerida para conhecer o sistema

| Ordem | Fluxo | Descrição |
|---|---|---|
| 1 | A (Prioridade, passo a passo) | Central de Processamento com avanço manual |
| 2 | C (saldo sem/com trava) | Auditoria de Integridade |
| 3 | F (esteira) | Esteira de Transações |
| 4 | D (travamento + prevenção) | Transferências Simultâneas |
| 5 | B ou E | Rede de ATMs ou Cache de Memória |
| 6 | G (Painel Gerencial) | Métricas da última sessão |

---

## 5. Referência rápida de inputs

| Objetivo | Sequência de inputs |
|---|---|
| Fila justa automática | `1` → `1` → `1` |
| Prioridade passo a passo | `1` → `2` → `2` |
| Operações urgentes automático | `1` → `3` → `1` |
| Saldo sem trava | `3` → `1` |
| Saldo com trava | `3` → `2` |
| Travamento sem prevenção | `4` → `1` |
| Travamento com prevenção | `4` → `2` |
| Cache de memória | `5` |
| Esteira de transações | `6` |
| Ver métricas | `8` |
